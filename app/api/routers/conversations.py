from fastapi import APIRouter,HTTPException,status
from sqlalchemy import select
import asyncio

from app.api.deps import CurrentUser,DbDep
from app.models import Conversation,Message
from app.schemas.conversation import ConversationCreate,ConversationOut,MessageCreate,MessageOut
from app.services.rag import generate_answer
from app.core.config import get_settings
from app.services.vector_store import get_qdrant_client

router = APIRouter(prefix="/conversations",tags=["conversations"])

async def _get_owned_conversation(db:DbDep, conversation_id: int, user) -> Conversation:
  conv = await db.get(Conversation, conversation_id)
  if not conv or conv.user_id != user.id:
    raise HTTPException(status_code=404,detail="会话不存在")
  return conv


#创建会话
@router.post("",response_model=ConversationOut,status_code=status.HTTP_201_CREATED)
async def create_conversation(payload: ConversationCreate,db: DbDep, user: CurrentUser):
  conversation = Conversation(user_id = user.id, title = payload.title or "新对话")
  db.add(conversation)
  await db.commit()
  await db.refresh(conversation)
  return conversation

#会话列表
@router.get("",response_model=list[ConversationOut])
async def list_conversations(db: DbDep, user: CurrentUser):
  result = await db.scalars(select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.updated_at.desc()))
  return result.all()

#会话详细
@router.get("/{conversation_id}", response_model= ConversationOut)
async def get_conversation(conversation_id: int, db: DbDep, user: CurrentUser):
  return await _get_owned_conversation(db,conversation_id,user)

#删除会话
@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: int,db: DbDep, user: CurrentUser):
  conv = await _get_owned_conversation(db,conversation_id, user)
  await db.delete(conv)
  await db.commit()


#发消息
@router.post("/{conversation_id}/messages",response_model=MessageOut,status_code=status.HTTP_201_CREATED)
async def add_message(conversation_id: int,db: DbDep, user: CurrentUser,payload: MessageCreate):
  await _get_owned_conversation(db,conversation_id,user)
  client = get_qdrant_client()
  # 查历史
  history = await db.scalars(select(Message).where(Message.conversation_id== conversation_id).order_by(Message.id.desc()).limit(10))
  #存用户信息
  message = Message(conversation_id = conversation_id,role="user",content = payload.content)
  db.add(message)
  await db.commit()
  await db.refresh(message)
  #调回答
  msgs:list[Message] = list(history.all())
  msgs.reverse()
  history_text:str = "\n".join(f"{m.role}: {m.content}" for m in msgs)
  answer = await asyncio.to_thread(generate_answer,client=client,user_id=user.id,question=payload.content,top_k=get_settings().TOP_K,history=history_text)

  #存assistant信息
  assistant_msg = Message(conversation_id=conversation_id,role="assistant",content = answer["answer"],sources=answer["sources"])
  db.add(assistant_msg)
  await db.commit()
  await db.refresh(assistant_msg)

  return assistant_msg


#看消息
@router.get("/{conversation_id}/messages",response_model=list[MessageOut])
async def list_messages(conversation_id: int, db: DbDep, user: CurrentUser):
  await _get_owned_conversation(db,conversation_id,user)
  result = await db.scalars(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.id))
  return result.all()
    



