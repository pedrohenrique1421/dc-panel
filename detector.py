import numpy as np
import threading
import sys
import time
import psutil
import cv2
from ultralytics import YOLO
from utils import safe_log, spinner
from audio import play_alarm
from config import *

def detect_yolo(model, frame_queue):
    logo_true_count = 0
    logo_false_count = 0
    prev_logo_state = False
    saving_frames = False
    detect_every_n = 2
    base_detect_every_n = 2

    frame_count = 0
    fps_count = 0
    last_fps_time = time.time()
    fps = 0

    while True:
        try:
            cpu_load = psutil.cpu_percent(interval=None)
            if cpu_load > 90:
                time.sleep(0.1)
                continue

            try:
                raw_frame = frame_queue.get(timeout=1)
            except:
                continue

            frame_count += 1
            fps_count += 1

            elapsed = time.time() - last_fps_time
            if elapsed >= 1.0:
                fps = fps_count / elapsed
                fps_count = 0
                last_fps_time = time.time()

                if cpu_load > 85:
                    detect_every_n = 5
                elif cpu_load > 70:
                    detect_every_n = 3
                else:
                    detect_every_n = base_detect_every_n

            if frame_count % detect_every_n != 0:
                continue

            frame = np.frombuffer(raw_frame, np.uint8).reshape((HEIGHT, WIDTH, 3))
            results = model(frame, verbose=False, conf=YOLO_CONF)
            logo_detected = len(results[0].boxes) > 0

            if logo_detected:
                logo_true_count += 1
                logo_false_count = 0
            else:
                logo_false_count += 1
                logo_true_count = 0

            if logo_true_count >= LOGO_APPEAR_THRESHOLD and not prev_logo_state:
                print(f"\n🎯 Logo apareceu! - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                prev_logo_state = True
                saving_frames = False
                threading.Thread(target=play_alarm, daemon=True).start()

            elif logo_false_count >= LOGO_DISAPPEAR_THRESHOLD and prev_logo_state:
                print(f"\n❌ Logo desapareceu! - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                prev_logo_state = False
                saving_frames = True

            # if saving_frames and not prev_logo_state and frame_count % 10 == 0:
            #     filename = os.path.join(SAVE_FOLDER, f"frame_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jpg")
            #     cv2.imwrite(filename, frame)
            #     print(f"\r🖼️ Frame salvo: {filename}")

            sys.stdout.write(f"\r{spinner()} FPS: {fps:5.1f} | CPU: {cpu_load:5.1f}% | Logo: {'V' if prev_logo_state else 'F'}   ")
            sys.stdout.flush()

        except Exception as e:
            safe_log("Erro na detecção YOLO", e)
            time.sleep(0.5)
