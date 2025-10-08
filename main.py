import threading
import time
from ultralytics import YOLO
from stream_reader import read_frames, frame_queue
from detector import detect_yolo
from audio import init_audio
from config import ALARM_FILE, MODEL_PATH

print("🚀 Iniciando sistema DC Panel...")

# Inicializa o som e o modelo
init_audio(ALARM_FILE)
model = YOLO(MODEL_PATH)

# Threads
threading.Thread(target=read_frames, daemon=True).start()
threading.Thread(target=detect_yolo, args=(model, frame_queue), daemon=True).start()

# Mantém o programa ativo
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Interrompido pelo usuário")
