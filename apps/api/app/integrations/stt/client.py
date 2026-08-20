import asyncio
import os
import shutil
from pathlib import Path

import httpx
from dotenv import load_dotenv
from pydub import AudioSegment

# Dynamically find ffmpeg/ffprobe on the host OS (Windows/Linux/Cloud)
ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    AudioSegment.converter = ffmpeg_path

ffprobe_path = shutil.which("ffprobe")
if ffprobe_path:
    AudioSegment.ffprobe = ffprobe_path

ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / ".env.local"
load_dotenv(ENV_PATH)

TENANT_ID = os.getenv("AZURE_OPENAI_WHISPER_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_OPENAI_WHISPER_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_OPENAI_WHISPER_SECRET")
WHISPER_ENDPOINT = os.getenv("AZURE_OPENAI_WHISPER_ENDPOINT")


async def get_azure_token() -> str:
    """Fetches an OAuth2 token using Client Credentials flow."""
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://cognitiveservices.azure.com/.default",
    }
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        return response.json()["access_token"]


async def transcribe_audio_chunk(file_path: Path, token: str) -> str:
    """Sends a single audio chunk to Azure Whisper."""
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
        # Read into memory to prevent chunked transfer encoding
        with open(file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        files = {"file": (file_path.name, audio_bytes, "audio/wav")}

        response = await client.post(WHISPER_ENDPOINT, headers=headers, files=files)

        print(f"--- AZURE WHISPER RAW RESPONSE ---")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        print(f"----------------------------------")

        response.raise_for_status()
        try:
            data = response.json()
            return data.get("text", "")
        except ValueError:
            return response.text.strip()


async def process_media_file(file_path: Path) -> str:
    """Converts video to audio, chunks to <24MB, and transcribes sequentially with rate limits."""
    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET, WHISPER_ENDPOINT]):
        return "[STT Skipped: Whisper credentials missing]"

    extracted_text = ""
    chunk_paths = []

    try:
        # Load media (pydub automatically extracts audio from mp4/mov if ffmpeg is installed)
        print(f"Loading media: {file_path.name}")
        audio = AudioSegment.from_file(file_path)

        # Target 24MB. WAV is roughly 10MB per minute (at 16kHz mono).
        # To be extremely safe, we will chunk into 2-minute segments.
        two_minutes_ms = 2 * 60 * 1000

        for i in range(0, len(audio), two_minutes_ms):
            chunk = audio[i:i + two_minutes_ms]
            chunk_path = file_path.with_suffix(f".chunk{i}.wav")
            # Export as 16kHz mono WAV to minimize size
            chunk.export(chunk_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
            chunk_paths.append(chunk_path)

        token = await get_azure_token()

        for idx, cp in enumerate(chunk_paths):
            print(f"Transcribing chunk {idx + 1}/{len(chunk_paths)}: {cp.name} (Size: {cp.stat().st_size / (1024 * 1024):.2f} MB)")
            text = await transcribe_audio_chunk(cp, token)
            extracted_text += text + " "

            # Rate Limit Enforcement: 3 requests per minute = 20 seconds between requests
            if idx < len(chunk_paths) - 1:
                print("Sleeping for 21 seconds to respect 3 req/min rate limit...")
                await asyncio.sleep(21)

        return extracted_text.strip()

    except Exception as e:
        return f"[Media Processing Failed: {str(e)}]"
    finally:
        # Cleanup chunks
        for cp in chunk_paths:
            cp.unlink(missing_ok=True)
