from __future__ import annotations

import subprocess
from pathlib import Path


class VideoConversionError(RuntimeError):
    """Raised when a video file cannot be converted to audio."""


def extract_audio_from_video(video_path: Path, output_path: Path) -> Path:
    """Extract a 16kHz mono MP3 audio track from a video file using ffmpeg.

    Uses the ffmpeg binary bundled by the `imageio-ffmpeg` package so no
    system-wide ffmpeg install is required.
    """
    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise VideoConversionError(
            "imageio-ffmpeg is required to convert video to audio; pip install imageio-ffmpeg"
        ) from exc

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            ffmpeg_exe,
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "libmp3lame",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-b:a",
            "128k",
            str(output_path),
        ],
        capture_output=True,
        check=False,
    )

    if result.returncode != 0 or not output_path.exists():
        stderr_tail = result.stderr.decode("utf-8", errors="replace")[-500:]
        raise VideoConversionError(f"ffmpeg failed to extract audio (exit={result.returncode}): {stderr_tail}")

    return output_path
