import os

# === Configurações ===
STREAM_URL = "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16"
WIDTH, HEIGHT = 640, 360
MODEL_PATH = r"C:\DC panel v1.0.0\runs\detect\train\weights\best.pt"
YOLO_CONF = 0.5
ALARM_FILE = "alarm.mp3"
SAVE_FOLDER = "frames_sem_logo"

os.makedirs(SAVE_FOLDER, exist_ok=True)

LOGO_APPEAR_THRESHOLD = 3
LOGO_DISAPPEAR_THRESHOLD = 10
