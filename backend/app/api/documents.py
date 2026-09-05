from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user
from app.core.permissions import require_permission
from app.db.session import get_db
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.schemas.document import DocumentRead
from app.services.report_parser import extract_text, summarize_report
from app.services.storage import download_bytes, upload_bytes

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
ALLOWED_CONTENT_TYPES = {"application/pdf", "text/plain"}

@router.post("/upload", response_model=DocumentRead)
async def upload_document(file: UploadFile, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    require_permission(current_user.role, "upload_reports")
    if file.content_type not in ALLOWED_CONTENT_TYPES: raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    data = await file.read(); storage_key = upload_bytes(data, file.content_type, file.filename)
    doc = Document(owner_id=current_user.id, filename=file.filename, content_type=file.content_type, storage_key=storage_key, status=DocumentStatus.UPLOADED)
    db.add(doc); await db.commit(); await db.refresh(doc); return doc

@router.post("/{document_id}/parse", response_model=DocumentRead)
async def parse_document(document_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == document_id)); doc = result.scalar_one_or_none()
    if not doc or doc.owner_id != current_user.id: raise HTTPException(status_code=404, detail="Document not found")
    doc.status = DocumentStatus.PARSING; await db.commit()
    try:
        data = download_bytes(doc.storage_key); text = extract_text(data, doc.content_type); summary = await summarize_report(text, language=current_user.preferred_language)
        doc.extracted_text = text; doc.summary = summary; doc.status = DocumentStatus.PARSED
    except Exception as exc:
        doc.status = DocumentStatus.FAILED; await db.commit(); raise HTTPException(status_code=500, detail=f"Parsing failed: {exc}") from exc
    await db.commit(); await db.refresh(doc); return doc

@router.get("", response_model=list[DocumentRead])
async def list_documents(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.owner_id == current_user.id)); return result.scalars().all()
