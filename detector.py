import numpy as np
import threading
import sys
import time
import queue
import psutil
import cv2
from ultralytics import YOLO
from utils import safe_log
from audio import play_alarm, play_standby, play_standon
from config import *
from colorama import Style, Fore, Back # type: ignore

def detect_yolo_thread(frame_queue, thread_id, status_dict, status_lock):
    """Cada thread YOLO cria seu próprio modelo"""
    model = YOLO(MODEL_PATH)
    detect_yolo(model, frame_queue, status_dict, status_lock, thread_id)

def detect_yolo(model, frame_queue, status_dict, status_lock, thread_id=1):

    # Variáveis
    logo_true_count = 0
    logo_false_count = 0
    prev_logo_state = False
    saved = False

    last_standby_time = 0
    standby_alerted = False

    cpu_load_time = 0.043
    last_fps_time = time.time()

    # Loop principal
    while True:
        try:
            t0 = time.time()

            cpu_load = psutil.cpu_percent(interval=0.025)
            if cpu_load > 90:
                time.sleep(cpu_load_time)
                continue

            try:
                # --- tempo de leitura da fila ---
                raw_frame = frame_queue.get(timeout=0.3)
                t1 = time.time()
                if standby_alerted:
                    play_standon()
                    print(f"🟢 {Fore.LIGHTWHITE_EX}Thread #{thread_id}{Fore.RESET} On-line\n")
                standby_alerted = False
                last_standby_time = time.time()
            except:
                if not standby_alerted and time.time() - last_standby_time > 3:
                    standby_alerted = True
                    play_standby()
                    print(f"🔴 {Fore.LIGHTWHITE_EX}Thread #{thread_id}{Fore.RESET} em standby\n")
                continue

            # Limitador de uso
            elapsed = time.time() - last_fps_time

            # Inferência da YOLO
            frame = np.frombuffer(raw_frame, np.uint8).reshape((HEIGHT, WIDTH, 3))

            results = model(frame, verbose=False, conf=YOLO_CONF)
            t2 = time.time()
            logo_detected = len(results[0].boxes) > 0

            # Calculo de desempenho em ms
            read_time = t1 - t0
            infer_time = t2 - t1
            total_time = t2 - t0
            fps_real = 1.0 / total_time if total_time > 0 else 0

            if logo_detected:
                logo_true_count += 1
                logo_false_count = 0
            else:
                logo_false_count += 1
                logo_true_count = 0

            if logo_true_count >= LOGO_APPEAR_THRESHOLD and not prev_logo_state:
                prev_logo_state = True
                saved = False
                threading.Thread(target=play_alarm, daemon=True).start()

            elif logo_false_count >= LOGO_DISAPPEAR_THRESHOLD and prev_logo_state:
                prev_logo_state = False

            # Salvar frames positivos
            # if not saved and prev_logo_state:
            #     filename = os.path.join(SAVE_FOLDER, f"frame_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jpg")
            #     cv2.imwrite(filename, frame)
            #     print(f"\r🖼️ Frame salvo: {filename}")
            #     saved = True

            # Imprimindo dados
            # === Atualiza status global ===
            with status_lock:
                status_dict[thread_id] = {
                    "fps": fps_real,
                    "cpu": cpu_load,
                    "yolo_time": infer_time,
                    "logo": prev_logo_state,
                    "cpu_load_time": cpu_load_time # Variavel DEV
                }

        except Exception as e:
            safe_log(f"{Back.RED}{Fore.LIGHTWHITE_EX} Erro na detecção (Thread #{Fore.LIGHTBLACK_EX}{thread_id})", e)
            time.sleep(0.5)
