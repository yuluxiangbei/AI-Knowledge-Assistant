from fastapi import APIRouter,HTTPException,UploadFile
from pathlib import Path
from uuid import uuid4
from sqlalchemy import func,select

from app.models.document import Document
from app.api.deps import DbDep,CurrentUser
from app.schemas.document import DocumentOut

from app.core.config import get_settings
from app.services.parser import parse_document

# 基于文件位置算项目根,不依赖工作目录
BASE_DIR = Path(__file__).resolve().parents[3]   # app/api/routers/ 往上3级 = 项目根
UPLOAD_DIR = BASE_DIR / "uploads"

router = APIRouter(prefix="/documents",tags=["documents"])

@router.post("/upload",response_model=DocumentOut)
async def upload_document(file: UploadFile,db: DbDep,user: CurrentUser):
  content = await file.read()
  if len(content) > get_settings().MAX_UPLOAD_SIZE_MB*1024*1024:
    raise HTTPException(status_code=413,detail="Payload Too Large")

  clean_filename = Path(file.filename or "").name
  ext = Path(clean_filename).suffix.lower()
  if ext not in {".pdf",".md",".txt"}:
    raise HTTPException(status_code=400,detail="不支持的格式")
  count = await db.scalar(select(func.count()).select_from(Document).where(Document.user_id == user.id))
  if count >= get_settings().MAX_DOCS_PER_USER:
    raise HTTPException(status_code=409,detail="文档数量已达上限")
  
  stored_name = f"{uuid4()}{ext}"
  storage_path = UPLOAD_DIR/ str(user.id)/ stored_name
  storage_path.parent.mkdir(parents=True,exist_ok=True)
  Path(storage_path).write_bytes(content)
  doc = Document(user_id = user.id,filename = clean_filename,stored_path=str(storage_path),file_size = len(content),text_content=parse_document(storage_path))
  db.add(doc)
  await db.commit()
  await db.refresh(doc)