import threading
import time
from ultralytics import YOLO
from stream_reader import read_frames, frame_queue
from detector import detect_yolo
from audio import init_audio
from config import ALARM_FILE, MODEL_PATH, STANDBY_FILE, STANDON_FILE
from colorama import init, Back, Fore, Style # type: ignore

# Inicializa o som e o modelo
init_audio(ALARM_FILE, STANDBY_FILE, STANDON_FILE)
model = YOLO(MODEL_PATH)

# Inicaliza a coloração dos prints

init(autoreset=True)  # reseta a cor automaticamente após cada print

print(f"🚀 {Back.GREEN}{Fore.LIGHTWHITE_EX} Iniciando {Style.RESET_ALL} sistema DC Panel...")

# Threads
threading.Thread(target=read_frames, daemon=True).start()
threading.Thread(target=detect_yolo, args=(model, frame_queue), daemon=True).start()

# Mantém o programa ativo
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\n🛑 {Back.RED}{Fore.LIGHTWHITE_EX} Interrompido {Style.RESET_ALL} pelo usuário")
