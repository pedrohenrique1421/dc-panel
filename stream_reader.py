import subprocess
import threading
import queue
import time
from utils import safe_log
from config import STREAM_URL, WIDTH, HEIGHT

process = None
process_lock = threading.Lock()
frame_queue = queue.Queue(maxsize=15)

def start_ffmpeg():
    global process
    with process_lock:
        if process:
            try:
                process.kill()
            except:
                pass
        try:
            process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i", STREAM_URL,
                    "-f", "rawvideo",
                    "-pix_fmt", "bgr24",
                    "-vf", f"scale={WIDTH}:{HEIGHT}",
                    "pipe:1"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**8
            )
            print("\n🔄 FFmpeg iniciado")
        except Exception as e:
            safe_log("Falha ao iniciar FFmpeg", e)
            process = None
            time.sleep(2)

def read_frames():
    global process
    frame_size = WIDTH * HEIGHT * 3

    while True:
        try:
            if not process:
                start_ffmpeg()
            raw_frame = process.stdout.read(frame_size)
            if len(raw_frame) != frame_size:
                raise RuntimeError("Frame incompleto")
            if frame_queue.full():
                frame_queue.get_nowait()
            frame_queue.put_nowait(raw_frame)
        except Exception as e:
            safe_log("Erro na leitura do stream", e)
            if process:
                process.kill()
                process = None
            time.sleep(2)
