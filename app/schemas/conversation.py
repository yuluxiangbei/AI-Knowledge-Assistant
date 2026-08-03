from datetime import datetime


from pydantic import BaseModel,Field,ConfigDict

class ConversationCreate(BaseModel):
  title: str | None = Field(default= None, max_length=100)

class ConversationOut(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id : int
  title : str
  created_at : datetime
  updated_at : datetime

class MessageCreate(BaseModel):#发消息
  content: str = Field(min_length=1,max_length=10000)

class MessageOut(BaseModel):
  model_config = ConfigDict(from_attributes= True)
  id: int
  role: str
  content: str
  created_at: datetime
  sources: list | None = None


