from datetime import datetime

from sqlalchemy import ForeignKey,String,Text,func,DateTime
from sqlalchemy.orm import Mapped,mapped_column

from app.db.base import Base


class Message(Base):
  __tablename__ = "messages"
  id: Mapped[int] = mapped_column(primary_key=True,autoincrement= True)
  conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id",ondelete="CASCADE"),nullable=False,index=True)
  role: Mapped[str] = mapped_column(String(20),nullable=False)
  content: Mapped[Text] = mapped_column(Text,nullable= False)
  created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),nullable= False)