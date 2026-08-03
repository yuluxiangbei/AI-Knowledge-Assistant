import asyncio
import time
import httpx


BASE = "http://127.0.0.1:8000/api/v1"
SUFFIX = str(int(time.time()))

async def main():
  async with httpx.AsyncClient(trust_env=False) as client:
    r = await client.post(
      f"{BASE}/auth/register",
      json={"username": f"alice{SUFFIX}", "password": "secret123"},
    )
    print("注册A:",r.status_code)
    token_a = r.json()["access_token"]
    h_a = {"Authorization": f"Bearer {token_a}"}

    with open("D:\\work\\简历\\test.txt", "rb") as f:
        r = await client.post(f"{BASE}/documents/upload", headers=h_a,
                          files={"file": ("test.txt", f, "text/plain")})
        print("上传:", r.status_code)
    #A创建对话
    r = await client.post(f"{BASE}/conversations",headers=h_a,json={"title":"第六课测试"})
    print("创建对话: ",r.status_code)
    cid = r.json()["id"]
    #A发消息
    r = await client.post(f"{BASE}/conversations/{cid}/messages",headers=h_a,json={"content":"FastAPI 基于什么实现异步?"})
    j = r.json()   # 解析一次,存变量,别反复调
    print("第一次发消息:", r.status_code, "role=", j["role"], "content=", j["content"], "sources=", j["sources"])
    #A发消息
    r = await client.post(f"{BASE}/conversations/{cid}/messages",headers=h_a,json={"content":"它支持异步吗？"})
    j = r.json()   # 解析一次,存变量,别反复调
    print("第二次发消息:", r.status_code, "role=", j["role"], "content=", j["content"], "sources=", j["sources"])
    #会话列表
    r = await client.get(f"{BASE}/conversations",headers=h_a)
    print("会话列表:", r.status_code, "条数=", len(r.json()))

    # A 看会话详情
    r = await client.get(f"{BASE}/conversations/{cid}",headers= h_a)
    print("会话详情:", r.status_code) 
    # 文档列表
    r = await client.get(f"{BASE}/documents", headers=h_a)
    print("文档列表:", r.status_code, "条数=", len(r.json()))
    doc_id = r.json()[0]["id"]   # 拿刚上传的文档 id

    # 删除文档
    r = await client.delete(f"{BASE}/documents/{doc_id}", headers=h_a)
    print("删除文档:", r.status_code)   # 期望 204

asyncio.run(main())