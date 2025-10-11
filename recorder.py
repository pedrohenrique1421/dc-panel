import cv2
import os
import time
import threading
from collections import deque
from config import SAVE_FOLDER, WIDTH, HEIGHT

# Variáveis globais de controle
record_lock = threading.Lock()
recording_active = False
frame_buffer = deque(maxlen=60)  # 2s de buffer (~30fps)

def buffer_frame(frame):
    """Mantém buffer dos últimos 2s."""
    frame_buffer.append(frame.copy())

def _save_video(frames_after, fps=30):
    """Thread real de gravação."""
    global recording_active
    with record_lock:
        if recording_active:
            return
        recording_active = True

    try:
        os.makedirs(SAVE_FOLDER, exist_ok=True)
        filename = os.path.join(SAVE_FOLDER, f"det_{time.strftime('%H%M%S')}.mp4")
        out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*"mp4v"), fps, (WIDTH, HEIGHT))

        # 2s antes
        for f in list(frame_buffer):
            out.write(f)

        # durante
        for f in frames_after:
            out.write(f)

        # 2s depois
        time.sleep(2)
        for f in list(frame_buffer):
            out.write(f)

        out.release()
        print(f"💾 Corte salvo: {filename}")

    finally:
        recording_active = False

def start_recording(frames_during):
    """Inicia gravação em thread separada."""
    if not recording_active:
        threading.Thread(target=_save_video, args=(frames_during,), daemon=True).start()
