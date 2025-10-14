import asyncio
import uvloop
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from convert_to_speech import TTSHandler

# Use uvloop for high performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(title="Async TTS API")

# Output directory
OUTPUT_DIR = Path("/app/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# TTS handler
tts = TTSHandler()

# Request model
class TTSRequest(BaseModel):
    text: str
    language: str
    filename: str

@app.post("/tts")
async def generate_tts(req: TTSRequest):
    """_summary_

    Args:
        req (TTSRequest): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    try:
        audio_bytes = tts.text_to_speech_bytes(req.text, req.language)
        output_path = OUTPUT_DIR / req.filename
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return {"status": "success", "path": str(output_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/bulk")
async def generate_tts_bulk(requests: list[TTSRequest]):
    """_summary_

    Args:
        requests (list[TTSRequest]): _description_

    Returns:
        _type_: _description_
    """
    tasks = [generate_tts(req) for req in requests]
    return await asyncio.gather(*tasks)
