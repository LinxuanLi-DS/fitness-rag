import json
import chromadb
from tqdm import tqdm
from chromadb.utils import embedding_functions

# 初始化 ChromaDB（本地存储）
client = chromadb.PersistentClient(path="chromadb")

# 用 sentence-transformers 做向量化
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 创建两个集合：食物 + 动作
food_col = client.get_or_create_collection("foods", embedding_function=ef)
exercise_col = client.get_or_create_collection("exercises", embedding_function=ef)


def build_food_text(food):
    """把食物数据拼成一段自然语言，方便向量化"""
    nutrients = food.get("nutrients", {})
    parts = [f"{food['name']}"]
    for k, v in nutrients.items():
        parts.append(f"{k}: {v}")
    return ", ".join(parts)


def build_exercise_text(ex):
    """把动作数据拼成一段自然语言"""
    instructions = " ".join(ex.get("instructions", []))
    secondary = ", ".join(ex.get("secondary_muscles", []))
    return (
        f"{ex['name']}. "
        f"Body part: {ex['body_part']}. "
        f"Target muscle: {ex['target_muscle']}. "
        f"Equipment: {ex['equipment']}. "
        f"Secondary muscles: {secondary}. "
        f"Instructions: {instructions}"
    )


def load_foods():
    print("📥 加载食物数据...")
    with open("data/raw/usda/foods.json") as f:
        return json.load(f)


def load_exercises():
    print("📥 加载动作数据...")
    with open("data/raw/exercises/exercises.json") as f:
        return json.load(f)


def index_foods(foods):
    print(f"\n🥦 开始向量化食物数据（共 {len(foods)} 条）...")
    batch_size = 500
    for i in tqdm(range(0, len(foods), batch_size)):
        batch = foods[i:i+batch_size]
        ids = [str(f["fdc_id"]) for f in batch]
        docs = [build_food_text(f) for f in batch]
        metas = [{"name": f["name"], "type": "food"} for f in batch]
        food_col.add(ids=ids, documents=docs, metadatas=metas)
    print(f"✅ 食物数据入库完成，共 {food_col.count()} 条")


def index_exercises(exercises):
    print(f"\n🏋️ 开始向量化动作数据（共 {len(exercises)} 条）...")
    ids = [str(ex["id"]) for ex in exercises]
    docs = [build_exercise_text(ex) for ex in exercises]
    metas = [{"name": ex["name"], "type": "exercise"} for ex in exercises]
    exercise_col.add(ids=ids, documents=docs, metadatas=metas)
    print(f"✅ 动作数据入库完成，共 {exercise_col.count()} 条")


def test_query():
    print("\n🔍 测试检索...")
    
    # 测试食物检索
    food_results = food_col.query(
        query_texts=["high protein low fat food for muscle building"],
        n_results=3
    )
    print("\n食物检索结果（高蛋白低脂）：")
    for doc in food_results["documents"][0]:
        print(f"  - {doc[:80]}...")

    # 测试动作检索
    ex_results = exercise_col.query(
        query_texts=["chest exercise for beginners"],
        n_results=3
    )
    print("\n动作检索结果（胸部训练）：")
    for doc in ex_results["documents"][0]:
        print(f"  - {doc[:80]}...")


if __name__ == "__main__":
    foods = load_foods()
    exercises = load_exercises()
    index_foods(foods)
    index_exercises(exercises)
    test_query()
    print("\n🎉 向量数据库构建完成！")