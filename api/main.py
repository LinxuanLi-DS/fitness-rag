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
from api.routers.period import router as period_router
from api.routers.daily_log import router as daily_log_router

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
app.include_router(period_router)
app.include_router(daily_log_router)

# 提供前端静态文件
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

@app.get("/survey-page")
def survey_page():
    return FileResponse("frontend/survey.html")

# PWA files - must be served at root
@app.get("/manifest.json")
def pwa_manifest():
    return FileResponse("frontend/manifest.json", media_type="application/manifest+json")

@app.get("/sw.js")
def pwa_sw():
    return FileResponse("frontend/sw.js", media_type="application/javascript")

@app.get("/icon-192.png")
def pwa_icon192():
    return FileResponse("frontend/icon-192.png", media_type="image/png")

@app.get("/icon-512.png")
def pwa_icon512():
    return FileResponse("frontend/icon-512.png", media_type="image/png")

@app.get("/icon.svg")
def pwa_icon_svg():
    return FileResponse("frontend/icon.svg", media_type="image/svg+xml")