"""
Basic first-run setup script.

For now this just ensures that the expected folders exist, similar to how
ComfyUI has an `output` folder ready for you. Later you can extend this to:
- Download the real BosonAI/Higgs-Audio-2 model
- Prepare config files
- Run any environment checks
"""

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
VOICE_INPUT_DIR = os.path.join(OUTPUT_DIR, "voice_inputs")
GENERATED_DIR = os.path.join(OUTPUT_DIR, "audio")
MODELS_DIR = os.path.join(BASE_DIR, "models_data")


def main() -> None:
  print("Setting up Voice AI Studio folders…")
  for path in [OUTPUT_DIR, VOICE_INPUT_DIR, GENERATED_DIR, MODELS_DIR]:
    os.makedirs(path, exist_ok=True)
    print(f"OK  {path}")

  print(
    "\nDone. You can now run:\n"
    "  python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload\n"
    "or simply:\n"
    "  python app.py\n"
  )


if __name__ == "__main__":
  main()


