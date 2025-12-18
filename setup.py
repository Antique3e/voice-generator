"""
First-run setup script for Voice AI Studio.

This script:
1. Creates necessary output folders (like ComfyUI's output/)
2. Optionally clones and installs Higgs-Audio V2 repository
3. Sets up the environment for model usage
"""

import os
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
VOICE_INPUT_DIR = os.path.join(OUTPUT_DIR, "voice_inputs")
GENERATED_DIR = os.path.join(OUTPUT_DIR, "audio")
MODELS_DIR = os.path.join(BASE_DIR, "models_data")
HIGGS_AUDIO_DIR = os.path.join(BASE_DIR, "higgs-audio")


def create_folders() -> None:
    """Create all necessary output folders."""
    print("Setting up Voice AI Studio folders…")
    for path in [OUTPUT_DIR, VOICE_INPUT_DIR, GENERATED_DIR, MODELS_DIR]:
        os.makedirs(path, exist_ok=True)
        print(f"✓  {path}")


def install_higgs_audio() -> bool:
    """
    Clone and install Higgs-Audio V2 repository.
    Returns True if successful, False otherwise.
    """
    print("\n" + "="*60)
    print("Higgs-Audio V2 Installation")
    print("="*60)
    
    # Check if already installed
    if os.path.exists(HIGGS_AUDIO_DIR):
        print(f"✓  Higgs-Audio directory already exists at: {HIGGS_AUDIO_DIR}")
        response = input("  Re-install? (y/N): ").strip().lower()
        if response != 'y':
            print("  Skipping Higgs-Audio installation.")
            return True
    
    # Ask user if they want to install
    print("\nTo use the real Higgs-Audio V2 model, you need to install it.")
    print("This will:")
    print("  1. Clone the repository from GitHub")
    print("  2. Install it as a Python package")
    print("  3. Download model weights on first use (~3GB)")
    print()
    response = input("Install Higgs-Audio V2 now? (Y/n): ").strip().lower()
    
    if response == 'n':
        print("  Skipping. You can install it later with:")
        print("    git clone https://github.com/boson-ai/higgs-audio.git")
        print("    cd higgs-audio && pip install -e .")
        return False
    
    try:
        # Clone repository
        print("\n1. Cloning Higgs-Audio repository...")
        if os.path.exists(HIGGS_AUDIO_DIR):
            print(f"   Removing existing directory: {HIGGS_AUDIO_DIR}")
            import shutil
            shutil.rmtree(HIGGS_AUDIO_DIR)
        
        result = subprocess.run(
            ["git", "clone", "https://github.com/boson-ai/higgs-audio.git", HIGGS_AUDIO_DIR],
            check=True,
            capture_output=True,
            text=True,
        )
        print("   ✓ Repository cloned successfully")
        
        # Install the package
        print("\n2. Installing Higgs-Audio package...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", HIGGS_AUDIO_DIR],
            check=True,
            capture_output=True,
            text=True,
        )
        print("   ✓ Package installed successfully")
        
        # Install Higgs-Audio requirements
        print("\n3. Installing Higgs-Audio dependencies...")
        higgs_requirements = os.path.join(HIGGS_AUDIO_DIR, "requirements.txt")
        if os.path.exists(higgs_requirements):
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", higgs_requirements],
                check=True,
                capture_output=True,
                text=True,
            )
            print("   ✓ Dependencies installed")
        
        print("\n✓ Higgs-Audio V2 installation complete!")
        print("\nNote: The model weights will be downloaded automatically")
        print("      from HuggingFace on first use (~3GB).")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error during installation:")
        print(f"  {e.stderr}")
        print("\nYou can install manually later with:")
        print("  git clone https://github.com/boson-ai/higgs-audio.git")
        print("  cd higgs-audio && pip install -e .")
        return False
    except FileNotFoundError:
        print("\n✗ Git not found. Please install Git first:")
        print("  https://git-scm.com/downloads")
        print("\nOr install manually:")
        print("  git clone https://github.com/boson-ai/higgs-audio.git")
        print("  cd higgs-audio && pip install -e .")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def main() -> None:
    """Main setup function."""
    print("="*60)
    print("Voice AI Studio - Setup")
    print("="*60)
    print()
    
    # Always create folders
    create_folders()
    
    # Optionally install Higgs-Audio
    install_higgs_audio()
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nYou can now run the server:")
    print("  python app.py")
    print("\nOr with uvicorn directly:")
    print("  python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload")
    print("\nThen open your browser to: http://localhost:8000")
    print()


if __name__ == "__main__":
    main()
