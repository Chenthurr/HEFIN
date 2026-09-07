import enum
from typing import TypedDict
from langgraph.graph import END, StateGraph
from app.rag.embeddings import embed_query
from app.rag.retriever import retriever
from app.services.model_router import TaskComplexity, model_router

class AgentRoute(str, enum.Enum):
    MEDICAL = "medical"; RESEARCH = "research"; FINANCE = "finance"
class OrchestratorState(TypedDict):
    query: str; language: str; route: str; retrieved_context: list[str]; answer: str; citations: list[str]

COMMON_HEALTH = {
    "cold": ("Common cold", "Rest, drink plenty of fluids, and consider saline nasal spray or steam for congestion. For pain or fever, use an appropriate over-the-counter medicine only as directed on its label and check for interactions or duplicate ingredients. Antibiotics do not treat ordinary colds. Seek care for trouble breathing, severe dehydration, chest pain, confusion, or symptoms that are severe or getting worse."),
    "flu": ("Flu", "Rest and fluids can help. Stay home while feverish and reduce close contact with others. Antiviral treatment can be useful for some people, especially when started early, so contact a clinician promptly if symptoms are significant or you are at higher risk of complications. Seek urgent help for difficulty breathing, chest pain, confusion, severe weakness, or dehydration."),
    "fever": ("Fever", "Fever is commonly caused by infection. Rest, drink fluids, and monitor how you feel. If using an over-the-counter fever reducer, follow the package directions and avoid combining products with the same active ingredient. Seek urgent care for difficulty breathing, severe headache with stiff neck, confusion, seizure, severe dehydration, or a rapidly worsening condition."),
    "cough": ("Cough", "A cough can occur with viral infections, allergies, asthma, reflux, and other conditions. Fluids, warm drinks, and avoiding smoke can help. Persistent, recurrent, bloody, or severe coughs should be assessed by a clinician. Seek urgent care for significant breathing difficulty, blue lips, chest pain, or coughing up more than a small amount of blood."),
    "headache": ("Headache", "Hydration, regular meals, sleep, and reducing obvious triggers may help some headaches. Use pain medicines only as directed and avoid frequent repeated use without medical advice. A sudden, extremely severe headache, or headache with weakness, confusion, fainting, seizure, stiff neck, or vision loss needs urgent medical assessment."),
    "diarrhea": ("Diarrhea", "The main priority is replacing fluids and electrolytes. Take frequent small drinks and eat simple foods as tolerated. Avoid dehydration, and be cautious with anti-diarrheal medicines if there is blood in the stool or fever. Seek medical care for severe dehydration, bloody or black stools, severe abdominal pain, persistent symptoms, or symptoms in a very young, frail, or high-risk person."),
    "constipation": ("Constipation", "Increase fluids, gradually increase dietary fibre, and stay physically active if able. Regular toilet routines can help. Seek medical advice for persistent constipation, unexplained weight loss, blood in the stool, vomiting, severe abdominal pain, or a sudden major change in bowel habits."),
    "diabetes": ("Diabetes", "Diabetes involves high blood glucose over time. Helpful basics include balanced meals, regular physical activity, taking prescribed medicines as directed, and monitoring glucose when advised. An HbA1c test is commonly used to assess average glucose over roughly the previous 2–3 months. A diagnosis should be made using appropriate testing by a clinician, not symptoms alone."),
    "hypertension": ("High blood pressure", "High blood pressure often has no obvious symptoms, so regular measurement matters. Helpful habits include limiting excess salt, staying active, maintaining a healthy weight when appropriate, not smoking, moderating alcohol, sleeping well, and taking prescribed treatment consistently. Very high readings with chest pain, severe breathlessness, weakness, confusion, or vision changes require urgent assessment."),
    "asthma": ("Asthma", "Asthma can cause episodes of wheeze, cough, chest tightness, or breathlessness. Avoid known triggers and use prescribed controller and reliever inhalers according to your asthma plan. If a reliever inhaler is not helping, breathing is very difficult, or you cannot speak normally because of breathlessness, seek emergency care."),
    "allergy": ("Allergies", "Avoiding a known trigger is the most useful first step. For mild allergy symptoms, appropriate antihistamines or other over-the-counter treatments may help when used according to the label. Swelling of the lips, tongue, or throat, trouble breathing, faintness, or rapidly worsening symptoms can indicate a severe allergic reaction and require emergency help."),
}

COMBINATION_GUIDANCE = [
    (("chest pain", "pressure in chest", "tightness in chest"),
     ("Chest pain needs careful assessment", "Chest pain can have many causes and some are emergencies. Do not rely on a chatbot to determine the cause. If the pain is severe, new, persistent, or comes with shortness of breath, sweating, fainting, nausea, or pain spreading to the arm, jaw, back, or shoulder, seek emergency medical care now.")),
    (("shortness of breath", "difficulty breathing", "trouble breathing", "can't breathe", "cannot breathe"),
     ("Breathing difficulty needs attention", "New or significant difficulty breathing should not be diagnosed online. Sit upright and avoid exertion while arranging medical assessment. Seek emergency help if breathing is severe, worsening, associated with chest pain, blue/grey lips, confusion, fainting, or inability to speak normally.")),
    (("fever", "cough", "body ache"),
     ("Fever + cough + body aches", "This combination can occur with respiratory infections such as influenza or COVID-19, but symptoms alone cannot confirm the cause. Rest, drink fluids, monitor your symptoms, and reduce close contact with others while unwell. Consider appropriate testing when relevant. Seek urgent care for breathing difficulty, chest pain, confusion, severe weakness, or dehydration.")),
    (("fever", "cough", "sore throat"),
     ("Fever + cough + sore throat", "These symptoms are commonly seen with respiratory infections, but they can have different causes. Rest, fluids, warm drinks, and avoiding smoke may help. Consider testing when appropriate. Seek medical assessment if symptoms are severe, persistent, worsening, or accompanied by breathing difficulty, chest pain, confusion, or dehydration.")),
    (("fever", "vomiting", "diarrhea"),
     ("Fever + vomiting + diarrhea", "An infection can cause this combination, but other causes are possible. Focus on small, frequent amounts of fluid and electrolytes and eat as tolerated. Seek medical care for severe dehydration, blood or black stool, severe abdominal pain, persistent vomiting, confusion, or worsening symptoms.")),
    (("headache", "stiff neck"),
     ("Headache + stiff neck", "A headache with a stiff neck can sometimes signal a serious illness. If this is new or severe, especially with fever, confusion, rash, vomiting, light sensitivity, weakness, or reduced consciousness, seek urgent medical assessment rather than relying on self-care advice.")),
    (("dizziness", "fainting"),
     ("Dizziness + fainting", "Fainting or near-fainting can have several causes. Sit or lie down somewhere safe and avoid driving. Seek urgent medical assessment if fainting is new, recurrent, occurs during exercise, follows chest pain or palpitations, causes injury, or is accompanied by weakness, confusion, severe headache, or breathing difficulty.")),
]

def classify_intent(state: OrchestratorState) -> OrchestratorState:
    query = state["query"].lower()
    if any(k in query for k in ["claim", "insurance", "premium", "benefit"]): route = AgentRoute.FINANCE
    elif any(k in query for k in ["study", "trial", "publication", "research"]): route = AgentRoute.RESEARCH
    else: route = AgentRoute.MEDICAL
    return {**state, "route": route.value}

def _common_health_answer(query: str) -> str | None:
    q = query.lower()
    for required_terms, (title, tips) in COMBINATION_GUIDANCE:
        if all(term in q for term in required_terms):
            return f"**{title} — general guidance**\n\n{tips}\n\nThis is general health information, not a diagnosis or personalised treatment plan."

    terms = {
        "cold": ["cold", "common cold"], "flu": ["flu", "influenza"], "fever": ["fever", "temperature"],
        "cough": ["cough"], "headache": ["headache", "migraine"], "diarrhea": ["diarrhea", "loose stool"],
        "constipation": ["constipation"], "diabetes": ["diabetes", "blood sugar", "hba1c", "a1c"],
        "hypertension": ["high blood pressure", "hypertension"], "asthma": ["asthma", "wheezing"],
        "allergy": ["allergy", "allergies", "hay fever"],
    }
    for key, matches in terms.items():
        if any(term in q for term in matches):
            name, tips = COMMON_HEALTH[key]
            return f"**{name} — general guidance**\n\n{tips}\n\nThis is general health information, not a diagnosis or personalised treatment plan. If you tell me your age, symptoms, how long they have been present, and any relevant medicines or conditions, I can help you think through what to discuss with a clinician."
    return None

async def _rag_answer(state: OrchestratorState, source_filter: str | None = None) -> OrchestratorState:
    chunks = await retriever.search(embed_query(state["query"]), top_k=5, source_filter=source_filter)
    if not chunks:
        fallback = _common_health_answer(state["query"])
        if fallback:
            return {**state, "answer": fallback, "citations": ["HEFIN basic health guidance"]}
        return {**state, "answer": "I couldn't find grounded sources for that yet — the knowledge base may not be seeded for this topic. Try asking about common cold, flu, fever, cough, headache, diarrhea, constipation, diabetes, high blood pressure, asthma, or allergies, or describe a combination of symptoms and how long you have had them.", "citations": []}
    context = "\n\n".join(f"[{c.source}] {c.text}" for c in chunks)
    prompt = ("You are HEFIN, an evidence-grounded healthcare information assistant. Answer ONLY from the supplied context. Never invent facts, sources, numbers, diagnoses, or prescriptions. Keep the answer concise and patient-friendly. Give general educational information and practical low-risk self-care tips when supported by the context. Clearly flag symptoms that need urgent or emergency care. Do not tell the user to start, stop, or change prescription medicines. Answer in the requested language. Cite supplied source names where useful.\n\n" f"Context:\n{context}\n\nQuestion: {state['query']}\n\nAnswer:")
    answer = await model_router.generate(prompt, complexity=TaskComplexity.MODERATE)
    return {**state, "answer": answer, "citations": sorted({c.source for c in chunks})}

async def medical_agent(state): return await _rag_answer(state)
async def research_agent(state): return await _rag_answer(state, source_filter="PubMed")
async def finance_agent(state): return await _rag_answer(state, source_filter="Insurance Policy Database")
def route_selector(state): return state["route"]

def build_orchestrator_graph():
    graph = StateGraph(OrchestratorState); graph.add_node("classify_intent", classify_intent); graph.add_node("medical", medical_agent); graph.add_node("research", research_agent); graph.add_node("finance", finance_agent); graph.set_entry_point("classify_intent")
    graph.add_conditional_edges("classify_intent", route_selector, {"medical":"medical", "research":"research", "finance":"finance"})
    graph.add_edge("medical", END); graph.add_edge("research", END); graph.add_edge("finance", END); return graph.compile()

orchestrator_graph = build_orchestrator_graph()
