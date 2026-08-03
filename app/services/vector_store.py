from qdrant_client import QdrantClient,models
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from uuid import uuid4


from app.core.config import get_settings


def ensure_collection(client:QdrantClient):
  COLLECTION_NAME = get_settings().QDRANT_COLLECTION
  if client.collection_exists(COLLECTION_NAME):
    return
  client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(
      size = get_settings().EMBEDDING_DIM,
      distance=models.Distance.COSINE))
  client.create_payload_index(collection_name=COLLECTION_NAME,field_name="user_id",field_schema=models.PayloadSchemaType.INTEGER)
  client.create_payload_index(collection_name=COLLECTION_NAME,field_name="document_id",field_schema=models.PayloadSchemaType.INTEGER)

# 全局唯一的编码(用了缓存,只加载一次)
@lru_cache
def embedder():
  return SentenceTransformer(get_settings().EMBEDDING_MODEL)


def upsert_chunks(client:QdrantClient,user_id: int,document_id: int,filename: str,chunks: list[str]):
  vectors = embedder().encode(chunks)
  points = []
  for index,vector in enumerate(vectors):
    points.append(models.PointStruct(id=uuid4(),vector=vector.tolist(),payload={"user_id":user_id,"document_id":document_id,
                                                         "filename":filename,"chunk_index":index,"content":chunks[index]}))

  delete_document_vectors(client,user_id,document_id)
  client.upsert(points=points,collection_name=get_settings().QDRANT_COLLECTION)


def search_chunks(client:QdrantClient,user_id:int,query_vector:list[float],top_k: int):
  result = client.query_points(collection_name=get_settings().QDRANT_COLLECTION,query=query_vector,query_filter=models.Filter(must=[
                          models.FieldCondition(key="user_id",match=models.MatchValue(value=user_id)),
                        ]))
  return result.points


def delete_document_vectors(client:QdrantClient,user_id:int,document_id:int,):
  client.delete(collection_name=get_settings().QDRANT_COLLECTION,
                points_selector=models.FilterSelector(filter=models.Filter(must=[
                  models.FieldCondition(key="user_id",match = models.MatchValue(value=user_id)),
                  models.FieldCondition(key="document_id",match = models.MatchValue(value=document_id)),
                ])))


if __name__ == "__main__":
  client = QdrantClient(url=get_settings().QDRANT_URL)
  chunks = ["FastAPI 基于 asyncio 实现异步", "async def 定义的协程需要 await 调用", "SQLAlchemy 异步会话要搭配 async with 使用"]
  ensure_collection(client)
  upsert_chunks(client, user_id=1, document_id=1, filename="test.txt", chunks=chunks)
  count = client.get_collection(get_settings().QDRANT_COLLECTION).points_count
  print("第一次插入后:", count)

  upsert_chunks(client, user_id=1, document_id=1, filename="test.txt", chunks=chunks)
  count = client.get_collection(get_settings().QDRANT_COLLECTION).points_count
  print("第二次插入后:", count)

  queryvector = embedder().encode("FastAPI 基于 什么 实现异步")
  print("user1 搜索:", search_chunks(client, user_id=1, query_vector=queryvector.tolist(), top_k=2))
  print("user2 搜索:", search_chunks(client, user_id=2, query_vector=queryvector.tolist(), top_k=2))   # ← 隔离测试,别漏!
  print("结束")