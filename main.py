from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil, os
from pipeline import process_pipeline

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/process/")
async def process_audio(file: UploadFile = File(...),
                        start_sec: int = Form(0),
                        end_sec: int = Form(30),
                        steps: str = Form("")):
    os.makedirs("static", exist_ok=True)
    upload_path = os.path.join("static", file.filename)
    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    steps_list = [s.strip() for s in steps.split(",") if s.strip()]
    try:
        res = process_pipeline(upload_path, start_sec, end_sec, steps_list)
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
