import numpy as np
import threading
import sys
import time
import psutil
import cv2
from ultralytics import YOLO
from utils import safe_log, spinner
from audio import play_alarm, play_standby, play_standon
from config import *
from colorama import Style, Fore, Back # type: ignore

def detect_yolo(model, frame_queue):
    logo_true_count = 0
    logo_false_count = 0
    prev_logo_state = False
    saving_frames = False
    detect_every_n = 2
    base_detect_every_n = 2

    last_standby_time = 0
    standby_alerted = False

    frame_count = 0
    fps_count = 0
    last_fps_time = time.time()
    fps = 0

    while True:
        try:
            cpu_load = psutil.cpu_percent(interval=1)
            if cpu_load > 90:
                time.sleep(0.1)
                continue

            try:
                raw_frame = frame_queue.get(timeout=0.3)
                if standby_alerted:
                    play_standon()
                    print(f"\n🟢 {Fore.LIGHTWHITE_EX}Thread{Fore.RESET} On-line")
                standby_alerted = False
                last_standby_time = time.time()
            except:
                if not standby_alerted and time.time() - last_standby_time > 3:
                    standby_alerted = True
                    play_standby()
                    print(f"\n🔴 {Fore.LIGHTWHITE_EX}Thread{Fore.RESET} em standby")
                continue

            frame_count += 1
            fps_count += 1

            elapsed = time.time() - last_fps_time
            if elapsed >= 1.0:
                fps = fps_count / elapsed
                fps_count = 0
                last_fps_time = time.time()

                if cpu_load > 90:
                    detect_every_n = 5
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
                print(f"\n🎯 {Back.GREEN}{Fore.LIGHTWHITE_EX} Logo apareceu! {Style.RESET_ALL} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                prev_logo_state = True
                saving_frames = False
                threading.Thread(target=play_alarm, daemon=True).start()

            elif logo_false_count >= LOGO_DISAPPEAR_THRESHOLD and prev_logo_state:
                print(f"\n❌ {Back.LIGHTRED_EX}{Fore.LIGHTWHITE_EX} Logo desapareceu! {Back.RESET} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                prev_logo_state = False
                saving_frames = True

            # if saving_frames and not prev_logo_state and frame_count % 10 == 0:
            #     filename = os.path.join(SAVE_FOLDER, f"frame_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jpg")
            #     cv2.imwrite(filename, frame)
            #     print(f"\r🖼️ Frame salvo: {filename}")

            sys.stdout.write(f"\r{spinner()} {Fore.LIGHTYELLOW_EX}FPS: {fps:5.1f}{Style.RESET_ALL} | {Fore.LIGHTCYAN_EX}CPU: {cpu_load:5.1f}%{Style.RESET_ALL} | {Fore.LIGHTWHITE_EX}Logo: {'On' if prev_logo_state else 'Off'}   ")
            sys.stdout.flush()

        except Exception as e:
            safe_log(f"{Back.RED}{Fore.LIGHTWHITE_EX} Erro na detecção YOLO ", e)
            time.sleep(0.5)
