from pydantic import BaseModel,Field,ConfigDict

class RegisterRequest(BaseModel):
  username : str = Field(min_length=3,max_length=64)
  password : str = Field(min_length=6)

class LoginRequest(BaseModel):
  username : str
  password : str

class UserOut(BaseModel):
  model_config = ConfigDict(from_attributes=True) #实现ORM 对象到响应模型的自动转换
  id : int
  username : str

class TokenOut(BaseModel):
  access_token : str
  token_type : str = "bearer"
  user : UserOut