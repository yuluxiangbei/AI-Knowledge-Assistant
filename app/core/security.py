from datetime import datetime, timedelta, timezone   # 标准库

import bcrypt                                        # 第三方
import jwt

from app.core.config import get_settings             # 本地


def hash_password(plain : str) -> str:
  passwd = bcrypt.hashpw(plain.encode("utf-8"),bcrypt.gensalt())
  return passwd.decode()

def verify_password(plain : str, hashed: str) -> bool:
  result = bcrypt.checkpw(plain.encode("utf-8"),hashed.encode("utf-8"))
  return result

settings = get_settings()
def create_access_token(subject: str | int) -> str:

  exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

  payload = {
    "sub":str(subject),
    "exp": exp,
  }

  token = jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
  return token

def decode_access_token(token: str) -> dict:
  payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
  return payload
  


