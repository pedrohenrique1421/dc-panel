import subprocess
import numpy as np
import threading
import queue
import sys
import time
import cv2
from ultralytics import YOLO
import itertools
import pygame
import os

# === Configurações ===
stream_url = "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16"
width, height = 640, 360
model_path = r"C:\DC panel v1.0.0\runs\detect\train\weights\best.pt"
detect_every_n = 2
yolo_conf = 0.5
alarm_file = "alarm.mp3"
output_dir = "gravacoes"

# cria pasta de saída se não existir
os.makedirs(output_dir, exist_ok=True)

# === Inicializa YOLO ===
model = YOLO(model_path)

# === Inicializa Pygame para som ===
pygame.mixer.init()
pygame.mixer.music.load(alarm_file)
pygame.mixer.music.set_volume(1.0)

# === Fila de frames ===
frame_queue = queue.Queue(maxsize=10)

# === Variáveis globais ===
process = None
process_lock = threading.Lock()
reconnecting = False

spinner_cycle = itertools.cycle(['|', '/', '-', '\\'])

# === Suavização temporal ===
LOGO_APPEAR_THRESHOLD = 3
LOGO_DISAPPEAR_THRESHOLD = 10
logo_true_count = 0
logo_false_count = 0
prev_logo_state = False

# === Variáveis de gravação ===
video_writer = None
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps_gravacao = 25  # taxa de gravação estimada

# === Função para iniciar/reiniciar FFmpeg ===
def start_ffmpeg():
    global process, reconnecting
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
            print("\n🔄 FFmpeg iniciado")
        except Exception as e:
            print(f"\n⚠️ Falha ao iniciar FFmpeg: {e}")
            process = None
            time.sleep(2)

# === Thread de leitura de frames ===
def read_frames():
    global process, reconnecting
    frame_size = width * height * 3
    while True:
        try:
            if not process:
                start_ffmpeg()
            raw_frame = process.stdout.read(frame_size)
            if len(raw_frame) != frame_size:
                raise RuntimeError("Stream incompleto")
            if frame_queue.full():
                try:
                    frame_queue.get_nowait()
                except queue.Empty:
                    pass
            frame_queue.put_nowait(raw_frame)
        except Exception as e:
            print(f"\n⚠️ Erro na leitura do stream: {e}, reiniciando FFmpeg...")
            with process_lock:
                if process:
                    try:
                        process.kill()
                    except:
                        pass
                    process = None
            reconnecting = True
            time.sleep(2)

threading.Thread(target=read_frames, daemon=True).start()

# === Função para tocar alarme ===
def play_alarm():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()

# === Thread de detecção YOLO + gravação ===
def detect_yolo_with_recording():
    global logo_true_count, logo_false_count, prev_logo_state, video_writer

    frame_count = 0
    fps_count = 0
    last_fps_time = time.time()
    fps = 0

    while True:
        raw_frame = None
        try:
            try:
                raw_frame = frame_queue.get(timeout=1)
            except queue.Empty:
                continue

            frame_count += 1
            fps_count += 1

            current_time = time.time()
            elapsed = current_time - last_fps_time
            if elapsed >= 1.0:
                fps = fps_count / elapsed
                fps_count = 0
                last_fps_time = current_time

            frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3))

            if frame_count % detect_every_n == 0:
                results = model(frame, verbose=False, conf=yolo_conf)
                logo_detected = len(results[0].boxes) > 0

                if logo_detected:
                    logo_true_count += 1
                    logo_false_count = 0
                else:
                    logo_false_count += 1
                    logo_true_count = 0

                # transições
                if logo_true_count >= LOGO_APPEAR_THRESHOLD and not prev_logo_state:
                    print(f"\n🎯 Logo apareceu! - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    prev_logo_state = True
                    threading.Thread(target=play_alarm, daemon=True).start()

                    # inicia gravação
                    ts = time.strftime("%Y-%m-%d_%H-%M-%S")
                    filename = os.path.join(output_dir, f"deteccao_{ts}.mp4")
                    video_writer = cv2.VideoWriter(filename, fourcc, fps_gravacao, (width, height))
                    print(f"🎥 Gravando vídeo: {filename}")

                elif logo_false_count >= LOGO_DISAPPEAR_THRESHOLD and prev_logo_state:
                    print(f"\n❌ Logo desapareceu! - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    prev_logo_state = False

                    # finaliza gravação
                    if video_writer:
                        video_writer.release()
                        video_writer = None
                        print("💾 Vídeo salvo!")

            # grava frame se logo está presente
            if prev_logo_state and video_writer:
                video_writer.write(frame)

            spinner = next(spinner_cycle)
            sys.stdout.write(f"\r{spinner} FPS: {fps:5.1f} | Logo: {'V' if prev_logo_state else 'F'}   ")
            sys.stdout.flush()

        except Exception as e:
            print(f"\n⚠️ Erro na detecção: {e}")
            time.sleep(0.5)

threading.Thread(target=detect_yolo_with_recording, daemon=True).start()

# === Mantém vivo ===
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Interrompido pelo usuário")
finally:
    if video_writer:
        video_writer.release()
    with process_lock:
        if process:
            process.terminate()
