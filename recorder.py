import subprocess
import time
from config import STREAM_URL, SAVE_FOLDER

MAIN_RECORD = None  # caminho do arquivo principal

def start_recording():
    global MAIN_RECORD

    timestamp = time.strftime("%d%m%Y_%H%M%S")
    output_path = f"{SAVE_FOLDER}/full_{timestamp}.ts"
    MAIN_RECORD = output_path

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # sobrescreve arquivo se existir
        "-i", STREAM_URL,
        "-c", "copy",  # não recodifica, grava direto
        "-f", "mpegts",  # formato que pode ser cortado enquanto grava
        output_path
    ]
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"🎥 Gravando stream em: {output_path}")
    return process, output_path
