import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentRead(BaseModel):
    id: uuid.UUID
    filename: str
    content_type: str
    status: DocumentStatus
    summary: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
