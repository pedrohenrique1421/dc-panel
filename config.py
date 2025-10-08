import os

# === Configurações ===
STREAM_URL = "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16"
WIDTH, HEIGHT = 640, 360 # Tamanho dos frames
MODEL_PATH = r"C:\DC panel v1.0.0\runs\detect\train\weights\best.pt" # caminho do modelo da I.A.
YOLO_CONF = 0.5 # Valor de Confiança da I.A.
ALARM_FILE, STANDBY_FILE, STANDON_FILE = "sounds/alarm.mp3", "sounds/standby.mp3", "sounds/standon.mp3"
SAVE_FOLDER = "frames_sem_logo" # Pasta para salvar frames selecionados
VOLUME = 60 # Volume das notificações

os.makedirs(SAVE_FOLDER, exist_ok=True) # Garante que a pasta existe

LOGO_APPEAR_THRESHOLD = 3 # Quantidade de frames para confirmar que a logo apareceu
LOGO_DISAPPEAR_THRESHOLD = 10 # Quantidade de frames para confirmar que a logo desapareceu
