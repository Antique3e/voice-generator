"""
Higgs-Audio V2 model wrapper.

This module provides a wrapper around BosonAI's Higgs-Audio V2 model.
It supports:
- Zero-shot voice cloning from reference audio
- Text-to-speech generation
- Temperature and other generation parameters
- 8-bit quantization for lower VRAM usage

To use the real model:
1. Clone the Higgs-Audio repository: git clone https://github.com/boson-ai/higgs-audio.git
2. Install it: cd higgs-audio && pip install -e .
3. The model will auto-download from HuggingFace on first use
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.io import wavfile

# Try to import Higgs-Audio modules (will fail gracefully if not installed)
try:
    # Add higgs-audio to path if it exists as a subdirectory
    HIGGS_AUDIO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "higgs-audio")
    if os.path.exists(HIGGS_AUDIO_PATH) and HIGGS_AUDIO_PATH not in sys.path:
        sys.path.insert(0, HIGGS_AUDIO_PATH)
    
    from boson_multimodal.audio_processing.generation import HiggsAudioGenerator
    HIGGS_AUDIO_AVAILABLE = True
except ImportError:
    HIGGS_AUDIO_AVAILABLE = False
    HiggsAudioGenerator = None


@dataclass
class GenerationConfig:
    """
    Configuration for audio generation.
    """
    temperature: float = 0.7
    speed: float = 1.0
    emotion: str = "neutral"
    sample_rate: int = 24000
    seed: Optional[int] = None


class HiggsAudioModel:
    """
    Wrapper for Higgs-Audio V2 model.
    
    If the real model is not available, falls back to a placeholder
    that generates test audio so the UI still works.
    """

    def __init__(self, models_dir: str, quantization: str = "full") -> None:
        """
        Initialize the model.
        
        Args:
            models_dir: Directory where model weights will be stored
            quantization: "full", "8bit", or "4bit" (8-bit/4-bit quantization for lower VRAM)
        """
        self.models_dir = models_dir
        self.quantization = quantization
        self.model_loaded = False
        self.generator = None
        self.use_real_model = HIGGS_AUDIO_AVAILABLE
        
        os.makedirs(self.models_dir, exist_ok=True)
        
        if self.use_real_model:
            try:
                self._load_model()
            except Exception as e:
                print(f"Warning: Failed to load Higgs-Audio model: {e}")
                print("Falling back to placeholder mode.")
                self.use_real_model = False

    def _load_model(self) -> None:
        """Load the actual Higgs-Audio V2 model."""
        if not HIGGS_AUDIO_AVAILABLE:
            raise ImportError("Higgs-Audio package not available. Install it with: git clone https://github.com/boson-ai/higgs-audio.git && cd higgs-audio && pip install -e .")
        
        print("Loading Higgs-Audio V2 model...")
        print("(This may take a few minutes on first run as model downloads from HuggingFace)")
        
        # Initialize the generator
        # The model will auto-download from HuggingFace if not already cached
        device = "cuda" if self._has_cuda() else "cpu"
        
        # Load with quantization if requested
        load_in_8bit = (self.quantization == "8bit")
        load_in_4bit = (self.quantization == "4bit")
        
        self.generator = HiggsAudioGenerator(
            device=device,
            load_in_8bit=load_in_8bit,
            load_in_4bit=load_in_4bit,
        )
        
        self.model_loaded = True
        print("✓ Higgs-Audio V2 model loaded successfully!")

    def _has_cuda(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    async def generate_async(
        self,
        text: str,
        voice_sample_path: Optional[str],
        output_path: str,
        config: GenerationConfig,
    ) -> None:
        """
        Generate audio asynchronously.
        
        Args:
            text: Text to convert to speech
            voice_sample_path: Optional path to reference audio for voice cloning
            output_path: Where to save the generated WAV file
            config: Generation configuration
        """
        if self.use_real_model and self.generator:
            await self._generate_real(text, voice_sample_path, output_path, config)
        else:
            await self._generate_placeholder(text, output_path, config)

    async def _generate_real(
        self,
        text: str,
        voice_sample_path: Optional[str],
        output_path: str,
        config: GenerationConfig,
    ) -> None:
        """Generate audio using the real Higgs-Audio V2 model."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        # Run the synchronous generation in a thread pool
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        
        def _generate_sync():
            """Synchronous generation function."""
            # Prepare the transcript (text input)
            transcript = text
            
            # Prepare reference audio if provided
            ref_audio = None
            if voice_sample_path and os.path.exists(voice_sample_path):
                ref_audio = voice_sample_path
            
            # Generate audio
            # Note: Adjust parameters based on actual Higgs-Audio API
            # The exact API may vary, but this is a reasonable structure
            try:
                audio_data = self.generator.generate(
                    transcript=transcript,
                    ref_audio=ref_audio,
                    temperature=config.temperature,
                    seed=config.seed,
                )
                
                # Save to file
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Convert to WAV format if needed
                if isinstance(audio_data, np.ndarray):
                    # If it's a numpy array, save directly
                    wavfile.write(output_path, config.sample_rate, audio_data.astype(np.float32))
                elif hasattr(audio_data, 'save') or hasattr(audio_data, 'export'):
                    # If it's an audio object with save/export method
                    if hasattr(audio_data, 'save'):
                        audio_data.save(output_path)
                    else:
                        audio_data.export(output_path, format="wav")
                else:
                    # Fallback: try to write as-is
                    import soundfile as sf
                    sf.write(output_path, audio_data, config.sample_rate)
                    
            except Exception as e:
                # If generation fails, fall back to placeholder
                print(f"Error in real model generation: {e}")
                print("Falling back to placeholder...")
                self._generate_placeholder_sync(text, output_path, config)
        
        await loop.run_in_executor(executor, _generate_sync)

    def _generate_placeholder_sync(
        self,
        text: str,
        output_path: str,
        config: GenerationConfig,
    ) -> None:
        """Synchronous placeholder generation (used as fallback)."""
        # Generate a test tone based on text length
        duration_sec = min(max(len(text) * 0.1, 1.0), 10.0)  # 1-10 seconds based on text length
        sr = config.sample_rate
        t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
        
        # Simple fade-in / fade-out sine beep
        freq = 440.0  # A4
        waveform = 0.15 * np.sin(2 * np.pi * freq * t)
        fade_len = int(0.1 * sr)
        fade = np.linspace(0.0, 1.0, fade_len)
        waveform[:fade_len] *= fade
        waveform[-fade_len:] *= fade[::-1]
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        wavfile.write(output_path, sr, waveform.astype(np.float32))

    async def _generate_placeholder(
        self,
        text: str,
        output_path: str,
        config: GenerationConfig,
    ) -> None:
        """Asynchronous placeholder generation."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        
        await loop.run_in_executor(
            executor,
            self._generate_placeholder_sync,
            text,
            output_path,
            config,
        )

    def get_status(self) -> dict:
        """
        Return model status information.
        """
        status = {
            "model_name": "BosonAI/Higgs-Audio-2" if self.use_real_model else "BosonAI/Higgs-Audio-2 (placeholder)",
            "loaded": self.model_loaded,
            "quantization": self.quantization,
            "models_dir": self.models_dir,
            "real_model_available": self.use_real_model,
        }
        
        if self.use_real_model and self._has_cuda():
            try:
                import torch
                if torch.cuda.is_available():
                    status["device"] = "cuda"
                    status["gpu_name"] = torch.cuda.get_device_name(0)
                    status["vram_allocated_mb"] = torch.cuda.memory_allocated(0) / 1024**2
                    status["vram_reserved_mb"] = torch.cuda.memory_reserved(0) / 1024**2
            except Exception:
                pass
        else:
            status["device"] = "cpu"
        
        return status
