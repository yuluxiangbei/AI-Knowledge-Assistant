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
    with open("D:\\work\\简历\\简历.pdf", "rb") as f:
        r = await client.post(f"{BASE}/documents/upload", headers=h_a,
                              files={"file": ("简历/简历.pdf", f, "application/pdf")})

asyncio.run(main())