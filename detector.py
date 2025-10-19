import numpy as np
import time
import psutil
from ultralytics import YOLO
#from recorder import buffer_frame, start_recording, recording_active
from utils import *
from audio import play_standby, play_standon
from config import *
from main import a
from colorama import Fore, Back # type: ignore


def detect_yolo_thread(frame_queue, thread_id, status_dict, status_lock):
    """Cada thread YOLO cria seu próprio modelo"""
    model = YOLO(MODEL_PATH)
    detect_yolo(model, frame_queue, status_dict, status_lock, thread_id)

def detect_yolo(model, frame_queue, status_dict, status_lock, thread_id=1):

    # Variáveis de BUFFER
    logo_true_count = 0
    logo_false_count = 0

    # Variaveis de GRAVAÇÃO

    logo_start = None
    logo_end = None
    logo_active = False
    event_log = []

    # Variáveis de ALERT
    last_standby_time = 0
    standby_alerted = False

    # Variáveis de DESEMPENHO
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
                # === Tempo de leitura da fila ===
                raw_frame = frame_queue.get(timeout=0.3)
                t1 = time.time()
                if standby_alerted:
                    play_standon()
                    print(f"\n🟢 {Fore.LIGHTWHITE_EX}Thread #{thread_id}{Fore.RESET} On-line")
                standby_alerted = False
                last_standby_time = time.time()
            except:
                if not standby_alerted and time.time() - last_standby_time > 3:
                    standby_alerted = True
                    play_standby()
                    print(f"\n🔴 {Fore.LIGHTWHITE_EX}Thread #{thread_id}{Fore.RESET} em standby")
                continue

            # Limitador de uso
            elapsed = time.time() - last_fps_time

            # Inferência da YOLO
            frame = np.frombuffer(raw_frame, np.uint8).reshape((HEIGHT, WIDTH, 3))
            FRAME_BUFFER.append(frame.copy())

            results = model(frame, verbose=False, conf=YOLO_CONF)
            t2 = time.time()
            logo_detected = any(r.boxes for r in results)

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

            # --- NOVA LÓGICA DE COMUNICAÇÃO COM A THREAD DE GRAVAÇÃO ---

            if logo_detected and not logo_active:
                logo_start = time.time()
                logo_active = True

            # Quando a logo some
            elif not logo_detected and logo_active:
                logo_end = time.time()
                logo_active = False
                event_log.append((logo_start, logo_end))
                print(f"🎬 Evento registrado: {logo_start:.2f}s -> {logo_end:.2f}s")
                if not a or not os.path.exists(a):
                    print(f"⚠️ Arquivo principal ainda não existe: {a}")
                else:
                    cortar_video(a, logo_start, logo_end, SAVE_FOLDER)

            # Imprimindo dados
            # === Atualiza status global ===
            with status_lock:
                status_dict[thread_id] = {
                    "fps": fps_real,
                    "cpu": cpu_load,
                    "yolo_time": infer_time,
                    "logo": logo_active,
                    "datetime": {time.time()} # Variavel DEV
                }

        except Exception as e:
            safe_log(f"{Back.RED}{Fore.LIGHTWHITE_EX} Erro na detecção (Thread #{Fore.LIGHTBLACK_EX}{thread_id})", e)
            time.sleep(0.5)
