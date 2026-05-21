import os
import anthropic
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# 初始化 Claude 客户端
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 连接 ChromaDB
client = chromadb.PersistentClient(path="chromadb")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
food_col = client.get_collection("foods", embedding_function=ef)
exercise_col = client.get_collection("exercises", embedding_function=ef)


def retrieve(query: str, n_results: int = 5):
    """根据问题检索相关的食物和动作数据"""
    food_results = food_col.query(query_texts=[query], n_results=n_results)
    exercise_results = exercise_col.query(query_texts=[query], n_results=n_results)

    foods = food_results["documents"][0]
    exercises = exercise_results["documents"][0]
    return foods, exercises


def build_prompt(query: str, foods: list, exercises: list, user_profile: dict = None):
    """把检索结果 + 用户画像拼成发给 Claude 的 prompt"""

    # 用户画像部分（如果有）
    profile_text = ""
    if user_profile:
        profile_text = f"""
用户信息：
- 性别：{user_profile.get('gender', '未知')}
- 年龄：{user_profile.get('age', '未知')}
- 体重：{user_profile.get('weight', '未知')} kg
- 身高：{user_profile.get('height', '未知')} cm
- 目标：{user_profile.get('goal', '未知')}
- 饮食限制：{user_profile.get('dietary', '无')}
"""

    food_context = "\n".join([f"- {f}" for f in foods])
    exercise_context = "\n".join([f"- {e}" for e in exercises])

    prompt = f"""你是一位专业的健身和营养顾问，请根据以下参考资料回答用户的问题。
回答要具体、实用，并结合用户的个人情况给出个性化建议。
回答请使用中文。
{profile_text}
参考食物数据：
{food_context}

参考健身动作数据：
{exercise_context}

用户问题：{query}

请给出专业、友好的回答："""

    return prompt


def ask(query: str, user_profile: dict = None):
    """完整的 RAG 问答流程"""
    print(f"\n🔍 检索相关知识...")
    foods, exercises = retrieve(query)

    print(f"📝 构建 prompt...")
    prompt = build_prompt(query, foods, exercises, user_profile)

    print(f"🤖 Claude 正在思考...\n")
    message = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


if __name__ == "__main__":
    # 测试1：没有用户画像
    print("=" * 50)
    print("测试1：普通问题")
    print("=" * 50)
    answer = ask("我想增肌，每天应该吃什么？")
    print(answer)

    # 测试2：带用户画像
    print("\n" + "=" * 50)
    print("测试2：个性化问题")
    print("=" * 50)
    profile = {
        "gender": "男",
        "age": 25,
        "weight": 70,
        "height": 175,
        "goal": "增肌",
        "dietary": "无限制"
    }
    answer = ask("给我推荐一个胸部训练动作", user_profile=profile)
    print(answer)