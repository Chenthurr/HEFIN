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

def classify_intent(state: OrchestratorState) -> OrchestratorState:
    query = state["query"].lower()
    if any(k in query for k in ["claim", "insurance", "premium", "benefit"]): route = AgentRoute.FINANCE
    elif any(k in query for k in ["study", "trial", "publication", "research"]): route = AgentRoute.RESEARCH
    else: route = AgentRoute.MEDICAL
    return {**state, "route": route.value}

async def _rag_answer(state: OrchestratorState, source_filter: str | None = None) -> OrchestratorState:
    chunks = await retriever.search(embed_query(state["query"]), top_k=5, source_filter=source_filter)
    if not chunks: return {**state, "answer": "I couldn't find grounded sources for that yet — the knowledge base may not be seeded for this topic.", "citations": []}
    context = "\n\n".join(f"[{c.source}] {c.text}" for c in chunks)
    prompt = ("You are HEFIN, an evidence-grounded healthcare information assistant. Answer ONLY from the supplied context. Never invent facts, sources, numbers, or clinical recommendations. Keep the answer concise and patient-friendly. The response is educational, not a diagnosis or prescription. Answer in the requested language. Cite supplied source names where useful.\n\n" f"Context:\n{context}\n\nQuestion: {state['query']}\n\nAnswer:")
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
