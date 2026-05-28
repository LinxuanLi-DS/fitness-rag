from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api.routers.users import router as users_router
from api.routers.chat import router as chat_router
from api.routers.vision import router as vision_router
from api.routers.feedback import router as feedback_router
from api.routers.survey import router as survey_router

app = FastAPI(title="FitRAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(chat_router)
app.include_router(vision_router)
app.include_router(feedback_router)
app.include_router(survey_router)

# 提供前端静态文件
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

@app.get("/survey-page")
def survey_page():
    return FileResponse("frontend/survey.html")