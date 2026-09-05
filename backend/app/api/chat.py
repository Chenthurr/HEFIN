from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.agents.orchestrator import orchestrator_graph
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.models.user import User
from app.services.safety_guard import apply_safety_gate

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    language: str | None = Field(default=None, max_length=8)
class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    route: str

@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, current_user: User = Depends(get_current_user)):
    require_permission(current_user.role, "ai_chat")
    blocked, disclaimer = apply_safety_gate(payload.message)
    if blocked: return ChatResponse(answer=disclaimer, citations=[], route="safety_gate")
    try:
        result = await orchestrator_graph.ainvoke({"query": payload.message, "language": payload.language or current_user.preferred_language, "route": "", "retrieved_context": [], "answer": "", "citations": []})
    except Exception as exc:
        raise HTTPException(status_code=503, detail="The AI service is not ready. Check the model provider, Qdrant, and knowledge base configuration.") from exc
    return ChatResponse(answer=result["answer"], citations=result["citations"], route=result["route"])
