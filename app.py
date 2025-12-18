import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from models.higgs_audio import HiggsAudioModel, GenerationConfig


# -----------------------------------------------------------------------------
# Paths & basic setup
# -----------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
VOICE_INPUT_DIR = os.path.join(OUTPUT_DIR, "voice_inputs")
GENERATED_DIR = os.path.join(OUTPUT_DIR, "audio")
MODELS_DIR = os.path.join(BASE_DIR, "models_data")

os.makedirs(VOICE_INPUT_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


app = FastAPI(title="Voice AI Studio", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# -----------------------------------------------------------------------------
# Model instance (placeholder – real loading can be added later)
# -----------------------------------------------------------------------------

voice_model = HiggsAudioModel(
    models_dir=MODELS_DIR,
    quantization="full",  # default, can be switched via config / UI later
)


# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------

class HistoryItem(BaseModel):
    id: str
    filename: str
    text_preview: str
    timestamp: str
    duration_seconds: Optional[float] = None


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

def list_history(limit: int = 20) -> List[HistoryItem]:
    """
    Read files from the GENERATED_DIR and build a lightweight history list,
    similar to how ComfyUI exposes an outputs folder that you can browse.
    """
    items: List[HistoryItem] = []

    if not os.path.isdir(GENERATED_DIR):
        return items

    # Sort by modification time, newest first
    files = sorted(
        [
            f
            for f in os.listdir(GENERATED_DIR)
            if os.path.isfile(os.path.join(GENERATED_DIR, f)) and f.lower().endswith(".wav")
        ],
        key=lambda name: os.path.getmtime(os.path.join(GENERATED_DIR, name)),
        reverse=True,
    )

    for f in files[:limit]:
        path = os.path.join(GENERATED_DIR, f)
        ts = datetime.fromtimestamp(os.path.getmtime(path)).isoformat(timespec="seconds")
        # Text preview is stored in filename metadata after a separator if present
        # Pattern: <uuid>__<preview>.wav
        base = os.path.splitext(f)[0]
        parts = base.split("__", 1)
        text_preview = parts[1] if len(parts) == 2 else ""

        items.append(
            HistoryItem(
                id=parts[0],
                filename=f,
                text_preview=text_preview,
                timestamp=ts,
                duration_seconds=None,  # TODO: read from metadata if needed
            )
        )

    return items


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """
    Serve the main UI. This is similar to how ComfyUI serves its index.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "port": 8000,
        },
    )


@app.post("/upload-voice")
async def upload_voice(file: UploadFile = File(...)) -> JSONResponse:
    """
    Store uploaded voice sample in VOICE_INPUT_DIR.
    Returns a token/path that can be used in subsequent generation requests.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = {".wav", ".mp3", ".flac", ".ogg"}
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail="Unsupported audio format.")

    voice_id = str(uuid.uuid4())
    dest_filename = f"{voice_id}{ext}"
    dest_path = os.path.join(VOICE_INPUT_DIR, dest_filename)

    with open(dest_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return JSONResponse({"voice_id": voice_id, "filename": dest_filename})


@app.post("/generate")
async def generate(
    text: str = Form(...),
    voice_id: Optional[str] = Form(None),
    temperature: float = Form(0.7),
    speed: float = Form(1.0),
    emotion: str = Form("neutral"),
) -> JSONResponse:
    """
    Trigger an audio generation.
    For now, this uses a lightweight placeholder implementation that produces
    a simple test WAV file. The structure is ready for a real Higgs-Audio V2
    integration.
    """
    text = (text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text input is required.")

    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text is too long (max 5000 characters).")

    voice_path: Optional[str] = None
    if voice_id:
        # Look for a file that starts with this voice_id
        candidates = [
            os.path.join(VOICE_INPUT_DIR, f)
            for f in os.listdir(VOICE_INPUT_DIR)
            if f.startswith(voice_id)
        ]
        if candidates:
            voice_path = candidates[0]

    cfg = GenerationConfig(
        temperature=temperature,
        speed=speed,
        emotion=emotion,
        sample_rate=24000,
    )

    # Use first 50 characters as text preview in the filename for history
    preview = text.replace("\n", " ")[:50].strip()
    preview = preview.replace("__", "_")

    out_id = str(uuid.uuid4())
    filename = f"{out_id}__{preview}.wav" if preview else f"{out_id}.wav"
    output_path = os.path.join(GENERATED_DIR, filename)

    try:
        await voice_model.generate_async(
            text=text,
            voice_sample_path=voice_path,
            output_path=output_path,
            config=cfg,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}") from e

    return JSONResponse(
        {
            "id": out_id,
            "filename": filename,
            "download_url": f"/download/{filename}",
        }
    )


@app.get("/download/{filename}")
async def download(filename: str) -> FileResponse:
    """
    Download a generated audio file from the outputs/audio folder.
    """
    safe_name = os.path.basename(filename)
    path = os.path.join(GENERATED_DIR, safe_name)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(path, media_type="audio/wav", filename=safe_name)


@app.get("/history")
async def get_history() -> JSONResponse:
    """
    Return last N generations based on files in the outputs/audio folder.
    This mirrors ComfyUI's "outputs" folder behavior, but via an API for the UI.
    """
    items = list_history(limit=20)
    return JSONResponse({"items": [item.dict() for item in items]})


@app.get("/status")
async def status() -> JSONResponse:
    """
    Basic status endpoint. Later this can expose VRAM, model names, etc.
    """
    model_status = voice_model.get_status()
    return JSONResponse(model_status)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


