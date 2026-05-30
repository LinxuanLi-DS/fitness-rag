"""测试ngrok + API"""
import requests
import json

# 1. 获取ngrok URL
try:
    r = requests.get("http://localhost:4040/api/tunnels", timeout=5)
    tunnels = r.json()["tunnels"]
    api = tunnels[0]["public_url"]
    print(f"ngrok URL: {api}")
except:
    api = "https://sliceable-rambling-evil.ngrok-free.dev"
    print(f"用默认URL: {api}")

# 2. 登录111
print("\n--- 登录 111 ---")
r = requests.post(f"{api}/users/login", json={"username": "111", "password": "111"}, timeout=10)
print(f"状态: {r.status_code}")
if r.ok:
    token = r.json()["access_token"]
    print(f"token: {token[:30]}...")
    
    # 3. 获取档案
    print("\n--- 获取档案 /users/me ---")
    r2 = requests.get(f"{api}/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=10)
    print(f"状态: {r2.status_code}")
    print(f"数据: {json.dumps(r2.json(), ensure_ascii=False, indent=2)}")
else:
    print(f"登录失败: {r.text}")

# 4. 登录李林烜
print("\n--- 登录 李林烜 ---")
r = requests.post(f"{api}/users/login", json={"username": "李林烜", "password": "123456"}, timeout=10)
print(f"状态: {r.status_code}")
if r.ok:
    token = r.json()["access_token"]
    r2 = requests.get(f"{api}/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=10)
    print(f"数据: {json.dumps(r2.json(), ensure_ascii=False, indent=2)}")
else:
    print(f"登录失败: {r.text}")
