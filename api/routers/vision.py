from fastapi import APIRouter, UploadFile, File, Form
from openai import OpenAI
import base64
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/vision", tags=["vision"])

qwen = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    question: str = Form(default="请分析这张图片中的食物，给出营养成分估算和健康建议。")
):
    # 读取图片并转 base64
    img_bytes = await file.read()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    mime = file.content_type or "image/jpeg"

    response = qwen.chat.completions.create(
        model="qwen-vl-plus",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"}
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]
    )

    return {"answer": response.choices[0].message.content}