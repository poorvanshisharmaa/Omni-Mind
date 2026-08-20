from __future__ import annotations

import platform
import shutil
import subprocess
import wave
from pathlib import Path

_VOICE_BY_LANG = {
    "en": "Samantha", "hi": "Lekha", "fr": "Thomas", "es": "Monica",
    "ja": "Kyoko", "de": "Anna", "zh": "Ting-Ting", "ar": "Maged", "pt": "Luciana",
}

_WORDS_PER_SECOND = 2.3  # ~140 wpm, used only by the silent fallback


class TTSEngine:
    def synth(self, text: str, language: str, out_path: Path) -> Path:
        raise NotImplementedError


class SystemSayTTSEngine(TTSEngine):
    """Real speech synthesis via macOS's built-in `say` command — no model
    download, no GPU. Stands in for XTTS-v2 / MMS-TTS per the spec.
    """

    def synth(self, text: str, language: str, out_path: Path) -> Path:
        voice = _VOICE_BY_LANG.get(language.lower(), _VOICE_BY_LANG["en"])
        aiff_path = out_path.with_suffix(".aiff")
        try:
            subprocess.run(
                ["say", "-v", voice, "-o", str(aiff_path), text],
                check=True, capture_output=True, timeout=60,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            subprocess.run(["say", "-o", str(aiff_path), text], check=True, capture_output=True, timeout=60)

        subprocess.run(
            ["afconvert", "-f", "WAVE", "-d", "LEI16", str(aiff_path), str(out_path)],
            check=True, capture_output=True, timeout=30,
        )
        aiff_path.unlink(missing_ok=True)
        return out_path


class SilentPlaceholderTTSEngine(TTSEngine):
    """Writes a valid, correctly-timed silent WAV file. Used on platforms
    without a system TTS voice (anything but macOS) so the pipeline never
    breaks — the audio file is real, just silent.
    """

    def synth(self, text: str, language: str, out_path: Path) -> Path:
        duration = max(1.0, len(text.split()) / _WORDS_PER_SECOND)
        framerate = 16000
        n_frames = int(duration * framerate)
        with wave.open(str(out_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(framerate)
            wav_file.writeframes(b"\x00\x00" * n_frames)
        return out_path


def get_tts_engine() -> TTSEngine:
    if platform.system() == "Darwin" and shutil.which("say") and shutil.which("afconvert"):
        return SystemSayTTSEngine()
    return SilentPlaceholderTTSEngine()
