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

# ========== 三个助手的专属人设和系统提示 ==========
ASSISTANT_CONFIGS = {
    "xiaojian": {
        "name": "小健",
        "role": "专业力量训练教练",
        "expertise": "力量训练、增肌计划、运动损伤预防、训练动作纠正",
        "system_prompt": """你是"小健"💪，一位专业的力量训练教练和体能训练师。

你的专长领域：
- 力量训练动作指导（卧推、深蹲、硬拉等）
- 增肌/减脂训练计划制定
- 运动损伤预防与康复
- 训练频率、组数、次数安排
- 运动前后的热身与拉伸

你不擅长但会转介的话题：
- 详细营养计算 → 建议找"小康"
- 生活习惯/睡眠/压力 → 建议找"十七"

回答风格：
- 直接、有力、鼓励性
- 给出具体的动作名称、组数、次数
- 强调安全和正确姿势
- 像健身房里那个靠谱的老大哥""",
    },
    "xiaokang": {
        "name": "小康",
        "role": "注册营养师",
        "expertise": "营养计算、饮食方案、食物搭配、特殊人群营养",
        "system_prompt": """你是"小康"💕，一位专业的注册营养师和饮食顾问。

你的专长领域：
- 宏量营养素计算（蛋白质、碳水、脂肪）
- 个性化饮食方案制定（减脂餐、增肌餐、均衡餐）
- 食物营养成分分析
- 特殊人群营养（孕期、哺乳期、经期、素食者）
- 食品安全与食物搭配
- 拍照识食物后的营养估算

你不擅长但会转介的话题：
- 具体训练动作/组数安排 → 建议找"小健"
- 心理调节/睡眠/生活平衡 → 建议找"十七"

回答风格：
- 温暖、专业、有数据支撑
- 给出具体的克数、热量、营养素数值
- 推荐具体的食物和搭配
- 像你的营养师闺蜜/好朋友""",
    },
    "shiqing": {
        "name": "十七",
        "role": "健康生活方式教练",
        "expertise": "睡眠管理、压力调节、生活习惯优化、整体健康",
        "system_prompt": """你是"十七"🐱，一位关注整体健康的生活方式教练。

你的专长领域：
- 睡眠管理与作息调节
- 压力管理与心理健康
- 生活习惯优化（久坐、久坐办公等）
- 女性健康管理（经期调理、产后恢复、更年期）
- 日常养生与中医调理建议
- 运动与休息的平衡

你不擅长但会转介的话题：
- 具体训练动作/组数 → 建议找"小健"
- 详细营养计算/食谱 → 建议找"小康"

回答风格：
- 温柔、有同理心、轻松
- 关注用户的整体状态而非单一指标
- 会适当用emoji让对话更轻松
- 像一只暖心的猫咪陪伴你""",
    },
}


def retrieve(query: str, n_results: int = 5):
    """根据问题检索相关的食物和动作数据"""
    food_results = food_col.query(query_texts=[query], n_results=n_results)
    exercise_results = exercise_col.query(query_texts=[query], n_results=n_results)
    return food_results["documents"][0], exercise_results["documents"][0]


def build_prompt(query: str, foods: list, exercises: list,
                 user_profile: dict = None, assistant_id: str = "xiaokang",
                 chat_history: list = None):
    """把检索结果 + 用户画像 + 助手人设拼成prompt"""
    config = ASSISTANT_CONFIGS.get(assistant_id, ASSISTANT_CONFIGS["xiaokang"])

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
- 运动频率：{user_profile.get('exercise_freq', '未知')}
- 睡眠：{user_profile.get('sleep', '未知')}
- 健身经验：{user_profile.get('fitness_level', '未知')}
"""
        # 女性专属字段
        if user_profile.get("life_stage") and user_profile["life_stage"] != "普通":
            profile_text += f"- 生理阶段：{user_profile['life_stage']}\n"
        if user_profile.get("cycle_phase") and user_profile["cycle_phase"] != "暂不填写":
            profile_text += f"- 生理周期：{user_profile['cycle_phase']}\n"
        if user_profile.get("target_weight"):
            profile_text += f"- 目标体重：{user_profile['target_weight']} kg\n"
        # 经期信息
        if user_profile.get("period_info"):
            pi = user_profile["period_info"]
            profile_text += f"\n当前经期状态：\n"
            profile_text += f"- 当前阶段：{pi.get('current_phase', '未知')}\n"
            profile_text += f"- 周期第几天：第{pi.get('current_cycle_day', '?')}天\n"
            if pi.get('days_until_next') is not None:
                profile_text += f"- 距下次经期：{pi['days_until_next']}天\n"
            if pi.get('phase_description'):
                profile_text += f"- 阶段建议：{pi['phase_description']}\n"
        # 经期历史
        if user_profile.get("period_history"):
            profile_text += f"\n最近经期记录：\n"
            for r in user_profile["period_history"]:
                line = f"- {r.get('start', '?')} → {r.get('end', '进行中')}"
                if r.get('duration'): line += f" ({r['duration']}天)"
                if r.get('symptoms'): line += f" [症状: {', '.join(r['symptoms'])}]"
                profile_text += line + "\n"

    food_context = "\n".join([f"- {f}" for f in foods])
    exercise_context = "\n".join([f"- {e}" for e in exercises])

    # 构建对话历史
    history_text = ""
    if chat_history:
        # 只取最近10条（5轮对话）
        recent = chat_history[-10:]
        history_lines = []
        for msg in recent:
            role = msg.get("role", "")
            text = msg.get("text", "")
            if role == "user":
                history_lines.append(f"用户：{text}")
            elif role == "bot":
                history_lines.append(f"助手：{text}")
        if history_lines:
            history_text = "\n\n之前的对话记录（请参考，保持上下文连贯）：\n" + "\n".join(history_lines)

    return f"""{config['system_prompt']}

{profile_text}
参考食物数据：
{food_context}

参考健身动作数据：
{exercise_context}
{history_text}

用户问题：{query}

回答要求：
- 仔细理解用户的意图，不要答非所问
- 如果提供了之前的对话记录，请参考上下文保持回答连贯，不要重复之前说过的内容
- 如果问题完全超出你的专长领域，礼貌说明并推荐合适的助手（小健/小康/十七）
- 如果问题与健身、饮食、健康完全无关，礼貌引导
- 简单问候或闲聊：1-2句话回应
- 具体问题：给出专业建议，有数据有细节
- 方案制定类：结构化回答，分步骤

格式要求（严格遵守）：
- 用中文回答
- 使用清晰的markdown格式
- 绝对不要用代码块（```）包裹你的回答

正确格式示例（直接输出，不要包裹在代码块中）：

## 训练计划

1. **动作名称**
   - 目标肌群：xxx
   - 动作要点：xxx
   - 组数次数：3组 × 10次

2. **动作名称**
   - 目标肌群：xxx
   - 动作要点：xxx
   - 组数次数：3组 × 12次

## 小贴士
- 建议1
- 建议2

禁止：
- 不要出现不完整的 ** 或 * 标记
- 不要出现以 . 开头的行（应该用 1. 2. 3.）
- 不要混用 ## 和 ### 标题
- 不要用 ``` 代码块包裹回答内容

请回答："""


def ask(query: str, user_profile: dict = None, assistant_id: str = "xiaokang", chat_history: list = None):
    """完整的 RAG 问答流程"""
    print(f"\n🔍 检索相关知识 (助手: {assistant_id})...")
    foods, exercises = retrieve(query)

    print(f"📝 构建 prompt...")
    prompt = build_prompt(query, foods, exercises, user_profile, assistant_id, chat_history)

    print(f"🤖 Qwen 正在思考...\n")
    response = qwen.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    profile = {
        "gender": "女", "age": 25, "weight": 55, "height": 165,
        "goal": "减脂", "dietary": "无限制", "exercise_freq": "每周3-4次",
        "sleep": "7-8小时", "fitness_level": "新手", "cycle_phase": "经期",
    }
    print("=" * 50)
    print("测试小健（力量训练）")
    print("=" * 50)
    print(ask("我想练胸肌，推荐几个动作", user_profile=profile, assistant_id="xiaojian"))

    print("\n" + "=" * 50)
    print("测试小康（营养饮食）")
    print("=" * 50)
    print(ask("经期应该吃什么", user_profile=profile, assistant_id="xiaokang"))

    print("\n" + "=" * 50)
    print("测试十七（健康生活）")
    print("=" * 50)
    print(ask("最近老是失眠怎么办", user_profile=profile, assistant_id="shiqing"))