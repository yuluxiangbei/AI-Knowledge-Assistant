from datetime import datetime

from sqlalchemy import ForeignKey,DateTime,func,String
from sqlalchemy.orm import Mapped,mapped_column

from app.db.base import Base

class Conversation(Base):
  __tablename__ = "conversations"
  id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
  user_id : Mapped[int] = mapped_column(ForeignKey("users.id"),index=True,nullable=False)
  title : Mapped[str] = mapped_column(String(100),default="新对话",nullable=False)
  created_at : Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),nullable=False)
  updated_at : Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),onupdate=func.now(),nullable=False)


