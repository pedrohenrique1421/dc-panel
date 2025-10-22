import subprocess
import threading
import queue
import time
from model.utils import safe_log
from config import STREAM_URL, WIDTH, HEIGHT
from colorama import Back, Fore # type: ignore

# Melhorar a velocidade de LEITURA

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
                    "-an",
                    "-f", "rawvideo",
                    "-pix_fmt", "bgr24",
                    "-vf", f"scale={WIDTH}:{HEIGHT}",
                    "pipe:1"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=10**8
            )
            print(f"\n🔄 {Fore.LIGHTWHITE_EX}FFmpeg {Back.GREEN} iniciado{Back.RESET}\n")
        except Exception as e:
            safe_log("Falha ao iniciar FFmpeg", e)
            process = None
            time.sleep(2)
def read_frames():
    global process
    frame_size = WIDTH * HEIGHT * 3
    last_frame_time = time.time()

    while True:
        try:
            if not process:
                start_ffmpeg()

            # tenta ler o frame com timeout de 1 segundo
            start_time = time.time()
            raw_frame = process.stdout.read(frame_size)
            if time.time() - start_time > 8:
                raise TimeoutError("FFmpeg travado — reiniciando...")

            if len(raw_frame) != frame_size:
                raise RuntimeError("Frame incompleto")

            last_frame_time = time.time()  # frame recebido, reset watchdog

            if frame_queue.full():
                frame_queue.get_nowait()
            frame_queue.put_nowait(raw_frame)

        except Exception as e:
            safe_log("Erro na leitura do stream", e)
            with process_lock:
                if process:
                    try:
                        process.kill()
                    except:
                        pass
                    process = None
            time.sleep(2)