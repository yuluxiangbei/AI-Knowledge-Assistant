import asyncio
import time
import httpx


BASE = "http://127.0.0.1:8000/api/v1"
SUFFIX = str(int(time.time()))

async def main():
  async with httpx.AsyncClient() as client:
    r = await client.post(
      f"{BASE}/auth/register",
      json={f"username": "alice{SUFFIX}", "password": "secret123"},
    )
    print("注册A:",r.status_code)
    token_a = r.json()["access_token"]
    r = await client.post(
      f"{BASE}/auth/register",
      json={f"username": "bob{SUFFIX}", "password": "secret123"},
    )
    print("注册B:",r.status_code)
    token_b = r.json()["access_token"]
    h_a = {"Authorization": f"Bearer {token_a}"}
    h_b = {"Authorization": f"Bearer {token_b}"}

    #A创建对话
    r = await client.post(f"{BASE}/conversations",headers=h_a,json={"title":"第六课测试"})
    print("创建对话: ",r.status_code)
    cid = r.json()["id"]

    #A发消息
    r = await client.post(f"{BASE}/conversations/{cid}/messages",headers=h_a,json={"content":"什么是RAG?"})
    print("第一次发消息: ",r.status_code,"role=",r.json()["role"])

    #A看消息
    r = await client.get(f"{BASE}/conversations/{cid}/messages",headers=h_a)
    print("第一次看消息: ",r.status_code,"条数=",len(r.json()))

    #会话列表
    r = await client.get(f"{BASE}/conversations",headers=h_a)
    print("会话列表:", r.status_code, "条数=", len(r.json()))
    # A 看会话详情
    r = await client.get(f"{BASE}/conversations/{cid}",headers= h_a)
    print("会话详情:", r.status_code) 

    #A发消息
    r = await client.post(f"{BASE}/conversations/{cid}/messages",headers=h_a,json={"content":"晚上吃什么呢？"})
    print("第二次发消息: ",r.status_code,"role=",r.json()["role"])

    #A看消息
    r = await client.get(f"{BASE}/conversations/{cid}/messages",headers=h_a)
    print("第二次看消息: ",r.status_code,"条数=",len(r.json()))

    #会话列表
    r = await client.get(f"{BASE}/conversations",headers=h_a)
    print("会话列表:", r.status_code, "条数=", len(r.json()))

    # A 看会话详情
    r = await client.get(f"{BASE}/conversations/{cid}",headers= h_a)
    print("会话详情:", r.status_code) 

    # ========== ⑥ 越权三连击:B 拿 A 的会话 id ==========
    # 这三次是"坏人测试":B 想碰 A 的会话,必须全部 404
    r = await client.get(f"{BASE}/conversations/{cid}", headers=h_b)
    print("B看A的会话:", r.status_code)                           

    r = await client.post(f"{BASE}/conversations/{cid}/messages", headers=h_b,
                          json={"content": "偷看"})
    print("B往A的会话发消息:", r.status_code)                    

    r = await client.get(f"{BASE}/conversations/{cid}/messages", headers=h_b)
    print("B看A的消息:", r.status_code)  

    # ========== ⑦ A 删除会话 ==========
    r = await client.delete(f"{BASE}/conversations/{cid}", headers=h_a)
    print("删除会话:", r.status_code)                            

    # ========== ⑧ 删后验证 ==========
    r = await client.get(f"{BASE}/conversations/{cid}", headers=h_a)
    print("删后再查:", r.status_code)                        

asyncio.run(main())



