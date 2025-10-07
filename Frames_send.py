import cv2
import requests

# URL gerada pelo ngrok no Colab (mude se reiniciar o túnel!)
API_URL = "https://streaky-mafalda-neological.ngrok-free.dev/predict"

# sua URL SRT
STREAM_URL = "srt://168.90.225.116:6053?mode=caller&latency=2000&transtype=live&passphrase=yKz585@354&pbkeylen=16"

# abre stream de vídeo
cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print("❌ Não foi possível abrir o stream")
    exit()

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Erro ao ler frame")
        break

    frame_count += 1

    # opcional: manda só 1 em cada 5 frames (para não sobrecarregar Colab)
    if frame_count % 5 != 0:
        continue

    # codifica frame para JPEG
    _, img_encoded = cv2.imencode(".jpg", frame)
    files = {"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}

    try:
        response = requests.post(API_URL, files=files, timeout=30)
        if response.status_code == 200:
            print("✅ Resposta:", response.json())
        else:
            print("⚠️ Erro:", response.status_code, response.text)
    except Exception as e:
        print("❌ Falha ao enviar frame:", e)
        break

cap.release()
