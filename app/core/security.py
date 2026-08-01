import bcrypt

def hash_password(plain : str) -> str:
  passwd = bcrypt.hashpw(plain.encode("utf-8"),bcrypt.gensalt())
  return passwd.decode()

def verify_password(plain : str, hashed: str) -> bool:
  result = bcrypt.checkpw(plain.encode("utf-8"),hashed.encode("utf-8"))
  return result

