from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os
from datetime import datetime
import assemblyai as aai
from config import MURF_API_KEY
from config import ASSEMBLY_API_KEY  

# Initialize FastAPI
app = FastAPI()

# Setup Uploads
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve static frontend files
app.mount("/static", StaticFiles(directory="."), name="static")

# Root HTML
@app.get("/")
def read_index():
    return FileResponse("index.html")

# Text-to-Speech Input Schema
class TextInput(BaseModel):
    text: str

# Generate Speech using Murf.ai
@app.post("/generate-audio")
def generate_audio(data: TextInput):
    headers = {
        "Content-Type": "application/json",
        "api-key": MURF_API_KEY
    }

    payload = {
        "text": data.text,
        "voiceId": "en-US-natalie",
        "pronunciationDictionary": {
            "2010": {
                "pronunciation": "two thousand and ten",
                "type": "SAY_AS"
            },
            "live": {
                "pronunciation": "laɪv",
                "type": "IPA"
            }
        }
    }

    response = requests.post("https://api.murf.ai/v1/speech/generate", headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        return {
            "audio_url": data.get("audioFile"),
            "duration_sec": data.get("audioLengthInSeconds"),
            "words": data.get("wordDurations")
        }
    else:
        return {"error": response.json()}


# Upload Audio File
@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, filename)

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    return {
        "filename": filename,
        "content_type": file.content_type,
        "size": os.path.getsize(file_location),
    }


# Transcribe Uploaded Audio File
@app.post("/transcribe/file")
async def transcribe_audio(file: UploadFile = File(...)):

    aai.settings.api_key = ASSEMBLY_API_KEY
    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)

    # Read binary content
    audio_bytes = await file.read()
    # print("Audio bytes read successfully", audio_bytes )

    try:
        transcript = aai.Transcriber(config=config).transcribe(audio_bytes)

        print("Transcription result:", transcript)
        
        if transcript.status == "error":
            return JSONResponse(status_code=500, content={"error": transcript.error})
        return {"transcript": transcript.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
