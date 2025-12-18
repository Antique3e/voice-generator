"""
Quick diagnostic script to check if Higgs-Audio V2 is properly installed.
Run this to see what's wrong.
"""

import os
import sys

print("=" * 60)
print("Higgs-Audio V2 Diagnostic Check")
print("=" * 60)
print()

# Check 1: Is higgs-audio directory present?
HIGGS_AUDIO_PATH = os.path.join(os.path.dirname(__file__), "higgs-audio")
print(f"1. Checking for higgs-audio directory...")
if os.path.exists(HIGGS_AUDIO_PATH):
    print(f"   ✓ Found: {HIGGS_AUDIO_PATH}")
else:
    print(f"   ✗ NOT FOUND: {HIGGS_AUDIO_PATH}")
    print("   → Run: git clone https://github.com/boson-ai/higgs-audio.git")
print()

# Check 2: Can we import the module?
print("2. Checking if boson_multimodal can be imported...")
try:
    if os.path.exists(HIGGS_AUDIO_PATH) and HIGGS_AUDIO_PATH not in sys.path:
        sys.path.insert(0, HIGGS_AUDIO_PATH)
    
    from boson_multimodal.audio_processing.generation import HiggsAudioGenerator
    print("   ✓ SUCCESS: Higgs-Audio can be imported!")
    print("   → Model should work")
except ImportError as e:
    print(f"   ✗ FAILED: {e}")
    print("   → Higgs-Audio is not installed properly")
    print("   → Run: cd higgs-audio && pip install -e .")
print()

# Check 3: Check PyTorch and CUDA
print("3. Checking PyTorch and CUDA...")
try:
    import torch
    print(f"   ✓ PyTorch version: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"   ✓ CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("   ⚠ CUDA not available (will use CPU)")
except ImportError:
    print("   ✗ PyTorch not installed")
    print("   → Run: pip install torch")
print()

# Check 4: Check model wrapper
print("4. Checking model wrapper...")
try:
    from models.higgs_audio import HiggsAudioModel, HIGGS_AUDIO_AVAILABLE
    print(f"   ✓ Model wrapper imported")
    print(f"   → HIGGS_AUDIO_AVAILABLE = {HIGGS_AUDIO_AVAILABLE}")
    
    # Try to initialize
    models_dir = os.path.join(os.path.dirname(__file__), "models_data")
    model = HiggsAudioModel(models_dir=models_dir, quantization="full")
    print(f"   → Model initialized")
    print(f"   → use_real_model = {model.use_real_model}")
    print(f"   → model_loaded = {model.model_loaded}")
    
    if not model.use_real_model:
        print("   ⚠ WARNING: Running in placeholder mode (beep only)")
        print("   → Install Higgs-Audio to use real model")
    else:
        print("   ✓ Real model is available!")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 60)
print("Diagnostic Complete")
print("=" * 60)

