import subprocess
import numpy as np
import threading
import queue
import time
from ultralytics import YOLO

# === Configurações ===
stream_url = "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16"
width, height = 640, 360

# caminho do modelo YOLO
model = YOLO("C:\DC panel v1.0.0\\runs\detect\\train\weights\\best.pt")

# === Fila de frames ===
frame_queue = queue.Queue(maxsize=50)

# === Variáveis globais ===
process = None
process_lock = threading.Lock()
reconnecting = False

# === Função para iniciar/reiniciar FFmpeg ===
def start_ffmpeg():
    global process, reconnecting
    with process_lock:
        if process:
            try:
                process.kill()
            except:
                pass
        print("🔄 Iniciando FFmpeg...")
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-i", stream_url,
                "-f", "rawvideo",
                "-pix_fmt", "bgr24",
                "-vf", f"scale={width}:{height}",
                "pipe:1"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10**8
        )
        reconnecting = False

# === Thread de leitura de frames ===
def read_frames():
    global process, reconnecting
    frame_size = width * height * 3
    while True:
        if not process:
            start_ffmpeg()
        raw_frame = process.stdout.read(frame_size)
        if len(raw_frame) != frame_size:
            if not reconnecting:
                print("⚠️ Stream falhou, reiniciando FFmpeg...")
                reconnecting = True
                threading.Thread(target=start_ffmpeg, daemon=True).start()
            time.sleep(1)
            continue
        try:
            if frame_queue.full():
                frame_queue.get_nowait()  # descarta frame antigo
            frame_queue.put_nowait(raw_frame)
        except queue.Full:
            pass

threading.Thread(target=read_frames, daemon=True).start()

# === Thread de detecção YOLO ===
def detect_yolo():
    while True:
        try:
            raw_frame = frame_queue.get(timeout=0.1)
        except queue.Empty:
            time.sleep(0.01)
            continue

        frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))

        # Roda a detecção YOLO
        results = model(frame, verbose=False)

        if len(results[0].boxes) > 0:
            print("🎯 Logo DETECTADA!")
        else:
            print("❌ Logo NÃO detectada.")

threading.Thread(target=detect_yolo, daemon=True).start()

# === Loop principal apenas para manter o notebook vivo ===
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Captura interrompida pelo usuário")

with process_lock:
    if process:
        process.terminate()
