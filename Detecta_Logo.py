import subprocess
import numpy as np
import threading
import queue
import time
from ultralytics import YOLO
import cv2
import os
from collections import deque

# === Configurações ===
stream_url = "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16"
video_fps = 25            # FPS do vídeo gravado
pre_seconds = 3           # segundos antes da logo
logo_missing_tolerance = 2  # segundos sem logo antes de parar gravação
yolo_conf = 0.25          # confiança mínima YOLO (0-1)

# caminho do modelo YOLO
model = YOLO(r"C:\DC panel v1.0.0\runs\detect\train\weights\best.pt")

# === Fila de frames e buffer circular ===
frame_queue = queue.Queue(maxsize=200)
buffer_frames = deque(maxlen=video_fps*pre_seconds)

# Pasta para salvar os vídeos
output_folder = "clips"
os.makedirs(output_folder, exist_ok=True)

# === Variáveis globais ===
process = None
process_lock = threading.Lock()
reconnecting = False

# === Descobrir resolução do stream via FFmpeg ===
def get_stream_resolution(url):
    import re
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "csv=p=0", url],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    match = re.findall(r'(\d+)', result.stdout.decode())
    if len(match) >= 2:
        return int(match[0]), int(match[1])
    else:
        return 640, 360

width, height = get_stream_resolution(stream_url)
print(f"📺 Stream resolução detectada: {width}x{height}")

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
            time.sleep(0.5)
            continue
        try:
            frame_queue.put_nowait(raw_frame)
        except queue.Full:
            pass

threading.Thread(target=read_frames, daemon=True).start()

# === Thread de detecção e gravação contínua ===
def detect_and_record_continuous():
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    flag_gravando = False
    out = None
    last_detect_time = 0

    while True:
        try:
            raw_frame = frame_queue.get(timeout=0.1)
        except queue.Empty:
            time.sleep(0.01)
            continue

        frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))
        buffer_frames.append(frame.copy())

        results = model(frame, verbose=False, conf=yolo_conf)
        num_boxes = len(results[0].boxes)
        # print(f"Frame processado, boxes detectadas: {num_boxes}")  # debug

        if num_boxes > 0:
            last_detect_time = time.time()
            if not flag_gravando:
                # Inicia gravação
                timestamp = int(time.time())
                output_path = os.path.join(output_folder, f"clip_{timestamp}.mp4")
                out = cv2.VideoWriter(output_path, fourcc, video_fps, (width, height))
                # escreve frames pré-logo
                for buf_frame in buffer_frames:
                    out.write(buf_frame)
                flag_gravando = True
                print(f"🎯 Logo detectada! Gravando clip: {output_path}")

        # Se estiver gravando, escreve o frame atual
        if flag_gravando:
            out.write(frame)
            # Para gravação se não detectar logo por um tempo de tolerância
            if time.time() - last_detect_time > logo_missing_tolerance:
                out.release()
                flag_gravando = False
                buffer_frames.clear()
                print("✅ Gravação finalizada.")

threading.Thread(target=detect_and_record_continuous, daemon=True).start()

# === Loop principal apenas para manter o script vivo ===
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Captura interrompida pelo usuário")
finally:
    with process_lock:
        if process:
            process.terminate()
