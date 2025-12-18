import os
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.io import wavfile


@dataclass
class GenerationConfig:
    """
    Simple configuration object for generation settings.
    This is intentionally lightweight; you can expand it as you add
    real model parameters.
    """

    temperature: float = 0.7
    speed: float = 1.0
    emotion: str = "neutral"
    sample_rate: int = 24000


class HiggsAudioModel:
    """
    Placeholder wrapper for Higgs-Audio V2.

    For now, this class does NOT load the real model. Instead, it writes
    a small test WAV file so that the full UI & backend flow work end-to-end.

    Later, you can replace the internals of `generate_async` with real calls
    to BosonAI/Higgs-Audio-2 (for example through Hugging Face Transformers
    or another inference library) while keeping the public API stable.
    """

    def __init__(self, models_dir: str, quantization: str = "full") -> None:
        self.models_dir = models_dir
        self.quantization = quantization
        self.model_loaded = False

        # In a real implementation, you would:
        # - Download / cache BosonAI/Higgs-Audio-2 into models_dir
        # - Load with the desired quantization (full / 8-bit / 4-bit)
        # - Move model to GPU
        #
        # For now we just ensure the directory exists.
        os.makedirs(self.models_dir, exist_ok=True)

    async def generate_async(
        self,
        text: str,
        voice_sample_path: Optional[str],
        output_path: str,
        config: GenerationConfig,
    ) -> None:
        """
        Asynchronous placeholder generation.

        - Ignores `voice_sample_path` and `config` for now.
        - Creates a short, simple sine-wave "beep" so you can verify that:
          - Backend endpoints work
          - The front-end history, download, and playback are wired correctly.
        """
        duration_sec = 2.0  # length of test audio
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

    def get_status(self) -> dict:
        """
        Return a simple status dict. You can extend this later to include:
        - model name / path
        - quantization
        - VRAM usage
        - loaded / unloaded state, etc.
        """
        return {
            "model_name": "BosonAI/Higgs-Audio-2 (placeholder)",
            "loaded": self.model_loaded,
            "quantization": self.quantization,
            "models_dir": self.models_dir,
        }


