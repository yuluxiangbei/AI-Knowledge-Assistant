from datetime import datetime

from pydantic import BaseModel,Field,ConfigDict

class DocumentOut(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  filename: str
  file_size: int
  created_at: datetime