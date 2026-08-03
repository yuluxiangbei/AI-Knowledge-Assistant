from fastapi import APIRouter,HTTPException,UploadFile,status
from pathlib import Path
from uuid import uuid4
from sqlalchemy import func,select
import asyncio

from app.models.document import Document
from app.api.deps import DbDep,CurrentUser
from app.schemas.document import DocumentOut

from app.core.config import get_settings
from app.services.parser import parse_document
from app.services.chunker import chunk_text
from app.services.vector_store import upsert_chunks,get_qdrant_client,ensure_collection,delete_document_vectors

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
  count = await db.scalar(select(func.count()).select_from(Document).where(Document.user_id == user.id)) or 0

  if count >= get_settings().MAX_DOCS_PER_USER:
    raise HTTPException(status_code=409,detail="文档数量已达上限")
  
  stored_name = f"{uuid4()}{ext}"
  storage_path = UPLOAD_DIR/ str(user.id)/ stored_name
  storage_path.parent.mkdir(parents=True,exist_ok=True)
  storage_path.write_bytes(content)
  doc = Document(user_id = user.id,filename = clean_filename,stored_path=str(storage_path),file_size = len(content),text_content=parse_document(storage_path))
  db.add(doc)
  await db.commit()
  await db.refresh(doc)
  client = get_qdrant_client()
  try:
    chunks = chunk_text(doc.text_content) #切块
    if chunks:
      await asyncio.to_thread(ensure_collection,client)
      await asyncio.to_thread(upsert_chunks,client =client,user_id=user.id,document_id=doc.id,filename=doc.filename,chunks=chunks)

  except Exception:
    await db.delete(doc)
    await db.commit()
    await asyncio.to_thread(delete_document_vectors,client=client,user_id=user.id,document_id=doc.id)
    raise HTTPException(status_code=500,detail="数据有问题")
  
  return doc

    
@router.get("",response_model=list[DocumentOut])
async def get_documents(db:DbDep,user:CurrentUser):
  result = await db.scalars(select(Document).where(Document.user_id == user.id).order_by(Document.id.desc()))
  return result.all()

@router.delete("/{document_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_doc(db:DbDep,user:CurrentUser,document_id: int):
  db_doc = await db.scalar(select(Document).where(Document.user_id == user.id,Document.id == document_id))
  if not db_doc:
    raise HTTPException(status_code=404,detail="所删除的文件不存在")
  client = get_qdrant_client()
  await asyncio.to_thread(delete_document_vectors,client=client,user_id=user.id,document_id=document_id)
  await db.delete(db_doc)
  await db.commit()
