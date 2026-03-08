from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import google.generativeai as genai
import os
import shutil
import uuid

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-flash-lite-latest")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate_outfit(request: Request,
                          file: UploadFile = File(...),
                          event: str = Form(...),
                          wedding_type: str = Form(None)):

    filename = f"{UPLOAD_FOLDER}/{uuid.uuid4()}.jpg"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with open(filename, "rb") as img:
        image_bytes = img.read()

    try:
        prompt = f"You are a professional fashion stylist. Suggest the best outfit for this event: {event}."
        if event == "Wedding" and wedding_type:
            prompt += f" The wedding type is {wedding_type}."
        prompt += " Return only text."
        response = model.generate_content(
            [
                prompt,
                {
                    "mime_type": file.content_type,
                    "data": image_bytes
                }
            ],
            stream=False
        )
        result_text = response.text
        result_text = result_text.replace('*', '\n')

    except Exception as e:
        result_text = f"AI Error: {e}"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result_text
    })