# Voice AI Studio

A ComfyUI-inspired web interface for **BosonAI/Higgs-Audio V2** and other voice AI models. Dark, modern, and professional-looking - just like ComfyUI, but for voice generation.

## Features

- 🎨 **ComfyUI-style dark interface** - Clean, modern, professional
- 🎤 **Zero-shot voice cloning** - Upload a 3-10 second voice sample
- 📝 **Text-to-speech generation** - Natural, expressive speech
- 🎛️ **Advanced controls** - Temperature, speed, emotion settings
- 📁 **Output folder** - Browse generations like ComfyUI's output folder
- 🔄 **Generation history** - View and replay previous generations
- ⚡ **8-bit/4-bit quantization** - Lower VRAM usage for smaller GPUs
- 🚀 **Cloud GPU ready** - Works on RunPod, Modal, Colab, etc.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Antique3e/voice-generator.git
cd voice-generator
```

### 2. Set Up Environment

```bash
# Create virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\activate  # Windows PowerShell
# or
source .venv/bin/activate  # Linux / macOS

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run Setup

```bash
python setup.py
```

This will:
- Create necessary folders (`outputs/`, `models_data/`)
- Optionally install Higgs-Audio V2 (you'll be prompted)

**Note:** If you choose to install Higgs-Audio V2, it will:
- Clone the repository from GitHub
- Install it as a Python package
- Download model weights (~3GB) on first use from HuggingFace

### 4. Start the Server

```bash
python app.py
```

Then open your browser to: **http://localhost:8000**

---

## Using Higgs-Audio V2

### Installation Options

#### Option 1: Automatic (Recommended)

Run `python setup.py` and choose "Y" when prompted to install Higgs-Audio V2.

#### Option 2: Manual Installation

If you skipped the automatic installation, you can install it manually:

```bash
# Clone the Higgs-Audio repository
git clone https://github.com/boson-ai/higgs-audio.git

# Install it
cd higgs-audio
pip install -e .
pip install -r requirements.txt
cd ..
```

The model weights will be automatically downloaded from HuggingFace on first use.

### Using the Web UI

1. **Enter Text** - Type or paste the text you want to convert to speech (max 5000 characters)

2. **Upload Voice (Optional)** - For zero-shot voice cloning:
   - Drag and drop an audio file (WAV, MP3, FLAC, OGG)
   - Or click to browse
   - Use a 3-10 second voice sample for best results

3. **Adjust Settings** (Optional):
   - **Temperature**: Controls creativity/randomness (0.0-2.0)
   - **Speed**: Playback speed (0.5-2.0)
   - **Emotion**: Voice style/emotion

4. **Generate** - Click the "Generate" button (or press `Ctrl+Enter`)

5. **Listen & Download** - The generated audio appears in the right panel with playback controls

### Model Status

The status bar in the header shows:
- ✓ Green dot = Model loaded and ready
- Model name and quantization mode
- GPU name and VRAM usage (if using CUDA)

---

## Project Structure

```
voice-generator/
├── app.py                 # FastAPI backend server
├── models/
│   └── higgs_audio.py     # Higgs-Audio V2 model wrapper
├── templates/
│   └── index.html         # Main UI template
├── static/
│   ├── css/
│   │   └── style.css      # ComfyUI-inspired dark theme
│   └── js/
│       └── app.js         # Frontend logic
├── outputs/               # Generated files (like ComfyUI's output/)
│   ├── audio/             # Generated audio files
│   └── voice_inputs/      # Uploaded voice samples
├── models_data/           # Model weights storage
├── higgs-audio/           # Higgs-Audio repository (if installed)
├── requirements.txt       # Python dependencies
├── setup.py              # First-run setup script
└── README.md             # This file
```

---

## API Endpoints

- **GET** `/` - Serves the main web UI

- **POST** `/upload-voice` - Upload a voice reference clip
  - Body: `file` (form-data, audio file)
  - Returns: `{"voice_id": "...", "filename": "..."}`

- **POST** `/generate` - Generate audio from text
  - Body (form-data):
    - `text` (string, required, max 5000 chars)
    - `voice_id` (string, optional)
    - `temperature` (float, default 0.7)
    - `speed` (float, default 1.0)
    - `emotion` (string, default "neutral")
  - Returns: `{"id": "...", "filename": "...", "download_url": "/download/<filename>"}`

- **GET** `/download/{filename}` - Download generated audio file

- **GET** `/history` - Get generation history (last 20 items)

- **GET** `/status` - Get model status and system info

---

## Quantization Options

To reduce VRAM usage, you can use quantization. Edit `app.py` and change:

```python
voice_model = HiggsAudioModel(
    models_dir=MODELS_DIR,
    quantization="8bit",  # or "4bit" for even lower VRAM
)
```

- **Full**: Best quality, highest VRAM (~6-8GB)
- **8-bit**: Good quality, lower VRAM (~4-6GB)
- **4-bit**: Lower quality, minimal VRAM (~2-4GB)

---

## Using on Cloud GPUs

### RunPod

1. Create a RunPod pod with Python
2. Clone the repo: `git clone https://github.com/Antique3e/voice-generator.git`
3. Install and run:
   ```bash
   cd voice-generator
   pip install -r requirements.txt
   python setup.py
   python app.py
   ```
4. Expose port 8000 in RunPod settings
5. Access via the RunPod URL

### Google Colab

1. Upload/clone the repo in Colab
2. Install:
   ```python
   !pip install -r requirements.txt
   !python setup.py
   ```
3. Run the server:
   ```python
   !python app.py
   ```
4. Use `ngrok` or Colab's port forwarding to access the UI

### Modal / Other Cloud Platforms

Follow similar steps - ensure port 8000 is exposed and accessible.

---

## Troubleshooting

### Model Not Loading

- **Error: "Higgs-Audio package not available"**
  - Run `python setup.py` and install Higgs-Audio V2
  - Or manually: `git clone https://github.com/boson-ai/higgs-audio.git && cd higgs-audio && pip install -e .`

- **CUDA/GPU errors**
  - Make sure PyTorch with CUDA is installed: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
  - Check GPU availability: `python -c "import torch; print(torch.cuda.is_available())"`

### UI Issues

- **Blank page**
  - Check server is running: `python app.py`
  - Open browser console (F12) for errors
  - Verify URL: `http://localhost:8000` (not https)

- **No audio generated**
  - Check terminal for error messages
  - Verify `outputs/audio/` folder exists
  - Check browser console for API errors

### Port Already in Use

- Change port in `app.py`:
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
  ```

### Out of Memory (OOM)

- Use 8-bit quantization (see Quantization Options above)
- Reduce batch size if applicable
- Close other applications using GPU

---

## How It Works

### Placeholder Mode

If Higgs-Audio V2 is not installed, the app runs in **placeholder mode**:
- Generates test sine-wave audio files
- UI and all features work normally
- Good for testing the interface

### Real Model Mode

When Higgs-Audio V2 is installed:
- Model loads on startup (or first generation)
- Supports zero-shot voice cloning
- High-quality text-to-speech generation
- Automatic model download from HuggingFace

The model wrapper (`models/higgs_audio.py`) automatically detects if Higgs-Audio is available and uses it, otherwise falls back to placeholder mode.

---

## Keyboard Shortcuts

- `Ctrl+Enter` - Generate audio
- `Esc` - Cancel generation (if supported)

---

## Credits

- **Higgs-Audio V2** by [Boson AI](https://github.com/boson-ai/higgs-audio)
- UI inspired by [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

---

## License

See LICENSE file in the repository.

---

## Support

For issues with:
- **This web interface**: Open an issue on this repository
- **Higgs-Audio model**: See [Higgs-Audio repository](https://github.com/boson-ai/higgs-audio)

---

## Contributing

Contributions welcome! The codebase is designed to be:
- Clean and well-commented
- Easy to modify and extend
- Modular (UI, backend, and model are separate)

Feel free to:
- Add support for other voice models
- Improve the UI/UX
- Add new features
- Fix bugs
