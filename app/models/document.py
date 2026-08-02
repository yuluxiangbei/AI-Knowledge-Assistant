from datetime import datetime


from sqlalchemy import String,ForeignKey,Integer,func,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.mysql import LONGTEXT

from app.db.base import Base

class Document(Base):
  __tablename__ = "documents"
  id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
  user_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
  filename: Mapped[str] = mapped_column(String(255),nullable=False,index=True)
  stored_path: Mapped[str] = mapped_column(String(500),nullable=False)
  text_content : Mapped[str] = mapped_column(LONGTEXT,nullable= False)
  file_size: Mapped[int] = mapped_column(Integer,nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),nullable=False)

