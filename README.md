# 🏋️ FitRAG — 个性化健身与健康饮食 AI 助手

> 基于 RAG 技术的健身 + 营养问答 App，支持个性化用户画像，给出真正适合你的建议。

---

## ✨ 核心功能

- **智能问答** — 基于权威数据库（USDA 营养数据 + ExerciseDB 动作库）回答健身/饮食问题
- **个性化建议** — 根据用户身高、体重、目标（增肌/减脂/保持）、饮食限制定制回答
- **历史记录** — 保存对话，追踪你的健康旅程
- **微信小程序** — 随时随地使用，无需安装

---

## 🏗️ 技术架构

```
微信小程序（前端）
      ↓
FastAPI 后端（腾讯云）
      ↓
RAG Pipeline
├── 检索层：ChromaDB + all-MiniLM-L6-v2
└── 生成层：Claude API
      ↓
知识库
├── USDA FoodData Central（营养数据）
└── ExerciseDB（健身动作）
```

---

## 🚀 本地开发

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/fitness-rag.git
cd fitness-rag
```

### 2. 创建虚拟环境

```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 API keys
```

### 4. 构建向量数据库

```bash
python scripts/fetch_usda.py
python scripts/fetch_exercises.py
python scripts/build_vectorstore.py
```

### 5. 启动后端

```bash
uvicorn api.main:app --reload
```

---

## 📁 项目结构

```
fitness-rag/
├── src/              # RAG 核心逻辑
├── api/              # FastAPI 后端
├── miniprogram/      # 微信小程序
├── scripts/          # 数据抓取脚本
├── data/             # 数据文件
└── deploy/           # 部署配置
```

---

## 🗺️ 开发路线图

- [x] 项目初始化
- [ ] Phase 1：RAG 后端核心
- [ ] Phase 2：用户系统 + 个性化
- [ ] Phase 3：微信小程序前端
- [ ] Phase 4：腾讯云部署 + 上线

---

## 📄 License

MIT