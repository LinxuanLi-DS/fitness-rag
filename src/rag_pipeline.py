import os
import chromadb
from openai import OpenAI
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

# 初始化 Qwen 客户端
qwen = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 连接 ChromaDB
db = chromadb.PersistentClient(path="chromadb")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
food_col = db.get_collection("foods", embedding_function=ef)
exercise_col = db.get_collection("exercises", embedding_function=ef)


def retrieve(query: str, n_results: int = 5):
    """根据问题检索相关的食物和动作数据"""
    food_results = food_col.query(query_texts=[query], n_results=n_results)
    exercise_results = exercise_col.query(query_texts=[query], n_results=n_results)
    return food_results["documents"][0], exercise_results["documents"][0]


def build_prompt(query: str, foods: list, exercises: list, user_profile: dict = None):
    """把检索结果 + 用户画像拼成发给 Qwen 的 prompt"""
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

    return f"""你是一位专业的健身和营养顾问，请根据以下参考资料回答用户的问题。
回答要具体、实用，并结合用户的个人情况给出个性化建议。
回答请使用中文。
{profile_text}
参考食物数据：
{food_context}

参考健身动作数据：
{exercise_context}

用户问题：{query}

回答要求：
- 简单问候或闲聊：简短友好回应，1-2句话即可
- 具体健身/饮食问题：给出详细专业的建议，包括具体数据、步骤和注意事项
- 方案制定类问题（如"给我一个计划"）：结构化详细回答，分步骤说明
- 原则：该详细时详细，该简短时简短，像真正的私人教练一样自然对话

请回答："""


def ask(query: str, user_profile: dict = None):
    """完整的 RAG 问答流程"""
    print(f"\n🔍 检索相关知识...")
    foods, exercises = retrieve(query)

    print(f"📝 构建 prompt...")
    prompt = build_prompt(query, foods, exercises, user_profile)

    print(f"🤖 Qwen 正在思考...\n")
    response = qwen.chat.completions.create(
        model="qwen-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # 测试1：普通问题
    print("=" * 50)
    print("测试1：普通问题")
    print("=" * 50)
    answer = ask("我想增肌，每天应该吃什么？")
    print(answer)

    # 测试2：个性化问题
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