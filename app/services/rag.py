from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from qdrant_client import QdrantClient


from app.core.config import get_settings
from app.services.vector_store import search_chunks,embedder,ensure_collection,upsert_chunks,get_qdrant_client


llm = OpenAI(api_key=get_settings().DEEPSEEK_API_KEY, base_url=get_settings().DEEPSEEK_BASE_URL)


def generate_answer(client:QdrantClient,user_id:int,question:str,top_k:int,history:str):
  query_vector = embedder().encode(question)
  context = ""
  sources = []

  hits = search_chunks(client,user_id=user_id,query_vector=query_vector.tolist(),top_k=top_k)

  for index,hit in enumerate(hits,start=1):
    if hit is None:
      continue
    filename = hit.payload["filename"] # type: ignore
    chunk_index = hit.payload["chunk_index"] # type: ignore
    content = hit.payload["content"] # type: ignore

    context+=(
      f"[{index}] {filename} chunk {chunk_index}\n"
      f"{content}\n\n"
    )
    sources.append({"filename":filename,"chunk_index":chunk_index})

  messages:list[ChatCompletionMessageParam] = [
    {"role": "system", "content": "你是知识库助手,只依据提供的资料回答;资料中没有的就说'资料中未提及';引用用 [n] 标注"},
    {"role": "user", "content": "资料:\n" + context +"\n历史记录:\n"+ history + "\n\n问题:" + question}
  ]

  reply = llm.chat.completions.create(model=get_settings().DEEPSEEK_MODEL, messages=messages)
  return {"answer": reply.choices[0].message.content, "sources": sources}


if __name__ == "__main__":
  client = get_qdrant_client()
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
  print(generate_answer(client=client,user_id=1,question="FastAPI 基于什么实现异步？",top_k=2,history=""))
  print("结束")