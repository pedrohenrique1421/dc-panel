import threading
import time
import sys
from ultralytics import YOLO
from stream_reader import read_frames, frame_queue
from detector import detect_yolo_thread
from audio import init_audio
from config import ALARM_FILE, MODEL_PATH, STANDBY_FILE, STANDON_FILE
from monitor import monitor_status
from colorama import init, Back, Fore, Style # type: ignore
from status_manager import *


# Inicializa o som e o modelo
init_audio(ALARM_FILE, STANDBY_FILE, STANDON_FILE)
model = YOLO(MODEL_PATH)

# Inicaliza a coloração dos prints
# Reseta a cor automaticamente
init(autoreset=True)

print(
    f"🚀 {Back.GREEN}{Fore.LIGHTWHITE_EX} Iniciando"
    f"{Style.RESET_ALL} sistema DC Panel..."
)

# Threads
threading.Thread(
    target=read_frames,
    daemon=True
).start() # PipeLine

threading.Thread(
    target=monitor_status,
    args=(status_dict, status_lock),
    daemon=True
).start() # Monitor

# Threads YOLO
NUM_THREADS = 3  # Numero de Threads
for i in range(NUM_THREADS):
    t = threading.Thread(
        target=detect_yolo_thread,
        args=(frame_queue, i+1, status_dict, status_lock),
        daemon=True
    )
    t.start()
    print(f"🧠 Thread YOLO #{i+1} iniciada")


# Mantém o programa ativo
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\n🛑 {Back.RED}{Fore.LIGHTWHITE_EX} Interrompido {Style.RESET_ALL} pelo usuário")
