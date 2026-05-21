import os
import json
import time
import requests
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
OUTPUT_FILE = "data/raw/exercises/exercises.json"
os.makedirs("data/raw/exercises", exist_ok=True)

HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
}
BASE_URL = "https://exercisedb.p.rapidapi.com"

# 我们关心的肌肉群
BODY_PARTS = [
    "back", "cardio", "chest", "lower arms", "lower legs",
    "neck", "shoulders", "upper arms", "upper legs", "waist"
]

def fetch_by_bodypart(body_part, limit=20):
    url = f"{BASE_URL}/exercises/bodyPart/{body_part}"
    params = {"limit": limit, "offset": 0}
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"  获取 {body_part} 失败(第{attempt+1}次): {e}")
            time.sleep(2)
    return []

def main():
    all_exercises = []
    print(f"开始抓取 {len(BODY_PARTS)} 个肌肉群的动作数据...\n")

    for part in tqdm(BODY_PARTS):
        exercises = fetch_by_bodypart(part)
        for ex in exercises:
            record = {
                "id": ex.get("id"),
                "name": ex.get("name"),
                "body_part": ex.get("bodyPart"),
                "target_muscle": ex.get("target"),
                "equipment": ex.get("equipment"),
                "instructions": ex.get("instructions", []),
                "secondary_muscles": ex.get("secondaryMuscles", [])
            }
            all_exercises.append(record)
        time.sleep(0.5)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_exercises, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 完成！共 {len(all_exercises)} 条动作数据")
    print(f"保存至 {OUTPUT_FILE}")
    print("\n示例：")
    if all_exercises:
        print(json.dumps(all_exercises[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()