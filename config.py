import os
from collections import deque
import subprocess
import time

# === Configurações ===
STREAM_URL = "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16"
WIDTH, HEIGHT = 640, 360 # Tamanho dos frames
MODEL_PATH = r"C:\DC panel v1.0.0\weights\best.pt" # caminho do modelo da I.A.
YOLO_CONF = 0.70 # Valor de Confiança da I.A.
ALARM_FILE, STANDBY_FILE, STANDON_FILE = "sounds/alarm.mp3", "sounds/standby.mp3", "sounds/standon.mp3"
SAVE_FOLDER = f"cortes/{time.strftime('%d%m%Y')}" # Pasta para salvar frames selecionados
VOLUME = 60 # Volume das notificações

# === Configurações do corte ===

BUFFER_SECONDS = 2
FPS_ESTIMATED = 30  # ajuste para seu fps real
FRAME_BUFFER = deque(maxlen=BUFFER_SECONDS * FPS_ESTIMATED)

FILENAME = "data.json"

os.makedirs(SAVE_FOLDER, exist_ok=True) # Garante que a pasta existe

LOGO_APPEAR_THRESHOLD = 1 # Quantidade de frames para confirmar que a logo apareceu
LOGO_DISAPPEAR_THRESHOLD = 5 # Quantidade de frames para confirmar que a logo desapareceu
