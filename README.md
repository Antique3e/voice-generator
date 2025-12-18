## Voice AI Studio (ComfyUI-style TTS Shell)

This is a minimal, ComfyUI-inspired web UI shell for future voice models such as
**BosonAI/Higgs-Audio-2**. It uses:

- **Backend**: FastAPI (similar to how ComfyUI serves its API)
- **Frontend**: Pure HTML + CSS + vanilla JS
- **Outputs**: Simple `outputs/` folder you can browse, just like ComfyUI

Right now, the "model" is a lightweight placeholder that generates a short sine
wave test audio file. The full structure is designed so you can later plug in
Higgs-Audio or any other TTS / voice model without changing the UI.

---

### Project layout

- `app.py` – main FastAPI app (serves UI and API endpoints)
- `models/higgs_audio.py` – model wrapper with a **placeholder** generator
- `templates/index.html` – ComfyUI-style dark layout
- `static/css/style.css` – dark, panel-based styling (ComfyUI-inspired)
- `static/js/app.js` – front-end logic (upload, generate, history, toasts)
- `outputs/`
  - `audio/` – generated audio files (history is based on this folder)
  - `voice_inputs/` – uploaded voice reference clips
- `models_data/` – place for downloaded model weights in the future
- `requirements.txt` – Python dependencies
- `setup.py` – simple first-run setup (creates folders)

---

### Installation (local or on a cloud GPU)

1. **Clone**

```bash
git clone <this-repo-url> voice-ai-studio
cd voice-ai-studio
```

2. **Create and activate a virtualenv (recommended)**

```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows PowerShell
# or
source .venv/bin/activate  # Linux / macOS
```

3. **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **First-run setup (creates folders, like ComfyUI's output dir)**

```bash
python setup.py
```

5. **Start the server (port 8000, ComfyUI-style)**

```bash
python app.py
```

Then open a browser and go to:

- `http://localhost:8000`

On RunPod / Colab / other cloud GPU, expose port 8000 according to the
platform's instructions.

---

### Basic usage

1. Open the web UI.
2. Paste some text into the **Script** textarea.
3. (Optional) Upload a short voice sample (`WAV/MP3/FLAC/OGG`). For now this is
   just stored, but in the future it will be passed to the real model for
   zero-shot voice cloning.
4. Adjust **Temperature**, **Speed**, and **Emotion** if you like.
5. Click **Generate** (or press `Ctrl+Enter`).

The backend will create a test `.wav` file in `outputs/audio/`. The right panel
will:

- Show an **audio player**
- Enable the **Download** button
- Add an entry to the **History** list (based on files in `outputs/audio/`)

---

### API endpoints (MVP)

- **GET** `/`
  - Serves the main HTML UI.

- **POST** `/upload-voice`
  - Upload and store a reference voice clip.
  - Body: `file` (form-data, audio file: WAV/MP3/FLAC/OGG)
  - Returns: `{"voice_id": "...", "filename": "..."}`.

- **POST** `/generate`
  - Generate audio from text (placeholder sine wave for now).
  - Body (form-data):
    - `text` (string, required, max 5000 chars)
    - `voice_id` (string, optional, from `/upload-voice`)
    - `temperature` (float)
    - `speed` (float)
    - `emotion` (string)
  - Returns:
    - `{"id": "...", "filename": "...", "download_url": "/download/<filename>"}`.

- **GET** `/download/{filename}`
  - Download a generated `.wav` file from `outputs/audio/`.

- **GET** `/history`
  - Returns a list of the last N generations, based on files in
    `outputs/audio/`.

- **GET** `/status`
  - Basic model status (placeholder: model name, quantization, directory).

---

### How history works (Comfy-style)

- Every generation writes a single `.wav` file into `outputs/audio/`.
- Filenames look like:

  - `<uuid>.wav`, or  
  - `<uuid>__<text-preview>.wav`

- The `/history` endpoint scans this folder, sorts by **modification time**, and
  returns the newest N entries. The UI shows:

  - Short text preview
  - Timestamp
  - **Play** and **Download** buttons

This is similar to how ComfyUI keeps images in an `output` folder that you can
inspect manually if you want.

---

### Swapping in a real model later

The key file is `models/higgs_audio.py`. Right now:

- `HiggsAudioModel.generate_async(...)` creates a short sine-wave `.wav` file.
- `HiggsAudioModel.get_status()` reports basic placeholder info.

To integrate a real model such as **BosonAI/Higgs-Audio-2**:

1. Install the correct dependencies (e.g. `transformers`, `torch`, model hub
   client, etc.).
2. Download model weights into `models_data/` (you can extend `setup.py` to do
   this automatically).
3. In `HiggsAudioModel.__init__`, load the model from `models_data/` with your
   desired quantization (full / 8-bit / 4-bit).
4. Replace the sine-wave logic in `generate_async` with:
   - Running the model with `text`, `voice_sample_path`, and settings from
     `GenerationConfig`.
   - Saving the resulting audio as 24kHz 16‑bit PCM WAV to `output_path`.

The FastAPI routes and the front-end JS do **not** need to change – only the
internals of the model wrapper.

---

### Troubleshooting

- **Blank page / cannot connect**
  - Make sure the server is running: `python app.py`.
  - Check that your browser uses the correct URL: `http://localhost:8000`.

- **Python import errors**
  - Re-run: `pip install -r requirements.txt`.
  - Check that your virtualenv is activated.

- **No history items appear**
  - Confirm that `.wav` files are being created in `outputs/audio/`.
  - If you deleted the folder manually, run `python setup.py` again.

- **Port already in use**
  - Stop other processes using port 8000, or change the port in `app.py` and
    your run command.

---

### Notes

- UI is intentionally minimal but styled to feel close to ComfyUI:
  - Dark theme
  - Panel-based layout
  - Output folder you can browse manually
- All front-end code is plain HTML/CSS/JS so you can easily tweak it.


