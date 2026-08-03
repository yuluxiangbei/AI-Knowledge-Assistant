from pydantic_settings import BaseSettings,SettingsConfigDict

from functools import lru_cache


class Settings(BaseSettings):
  # 告诉 pydantic:去 .env 文件里找配置
  model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")
  APP_NAME : str = "AI-Knowledge-Assistant"
  SECRET_KEY : str= "change-me"
  ALGORITHM : str = "HS256"
  DATABASE_URL : str = "mysql+asyncmy://app:app123456@127.0.0.1:3306/ai_knowledge?charset=utf8mb4"
  DEBUG : bool = False
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
  MAX_UPLOAD_SIZE_MB: int = 10
  MAX_DOCS_PER_USER: int = 50
  DEEPSEEK_API_KEY: str = ""
  DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
  DEEPSEEK_MODEL: str = "deepseek-chat"
  OPENAI_API_KEY: str = ""
  EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
  CHUNK_SIZE: int = 500
  CHUNK_OVERLAP: int = 50
  TOP_K: int = 5
  CORS_ORIGINS: list[str] = ["http://localhost:8501"]
  QDRANT_URL: str = "http://localhost:6333"
  QDRANT_API_KEY: str = ""
  QDRANT_COLLECTION: str = "ai_knowledge_chunks"
  EMBEDDING_DIM: int = 512
# 全局唯一的 settings 对象(用了缓存,只加载一次)
@lru_cache
def get_settings() -> Settings:
  return Settings()