import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="FitHer · 她健康",
    page_icon="🌸",
    layout="centered"
)

# 自定义样式
st.markdown("""
<style>
    .main { background-color: #fff5f7; }
    .stChatMessage { border-radius: 16px; }
    h1 { color: #e75480; }
</style>
""", unsafe_allow_html=True)

st.title("🌸 FitHer · 她健康")
st.caption("你的专属健身与营养 AI 顾问")

# 侧边栏：用户画像
with st.sidebar:
    st.header("👤 我的信息")
    st.caption("填写后回答更个性化")

    age = st.number_input("年龄", min_value=10, max_value=100, value=25)
    weight = st.number_input("体重 (kg)", min_value=30.0, max_value=200.0, value=55.0)
    height = st.number_input("身高 (cm)", min_value=100.0, max_value=220.0, value=165.0)
    goal = st.selectbox("我的目标", ["减脂", "塑形", "增肌", "保持健康", "孕期营养", "产后恢复"])
    life_stage = st.selectbox("当前阶段", ["普通", "备孕", "孕期", "哺乳期"])
    cycle_phase = st.selectbox("生理周期", ["经期", "卵泡期", "排卵期", "黄体期", "暂不填写"])
    fitness_level = st.selectbox("健身经验", ["新手", "中级", "进阶"])
    dietary = st.text_input("饮食限制", placeholder="如：不吃海鲜、素食...")

    user_profile = {
        "age": age,
        "gender": "女",
        "weight": weight,
        "height": height,
        "goal": goal,
        "life_stage": life_stage,
        "cycle_phase": cycle_phase if cycle_phase != "暂不填写" else None,
        "fitness_level": fitness_level,
        "dietary": dietary or "无"
    }

# 聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是你的专属健康顾问 🌸 可以问我任何关于健身和饮食的问题～"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
if prompt := st.chat_input("问我任何健身或饮食问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                res = requests.post(
                    f"{API_URL}/chat",
                    json={"query": prompt, "user_profile": user_profile}
                )
                answer = res.json()["answer"]
            except Exception as e:
                answer = f"出错了：{e}，请确认后端服务正在运行。"
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})