from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from config import MURF_API_KEY  # this pulls from .env

app = FastAPI()

# Serve static frontend files
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def read_index():
    return FileResponse("index.html")

class TextInput(BaseModel):
    text: str

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
