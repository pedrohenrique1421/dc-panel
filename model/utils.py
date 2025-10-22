import itertools
import traceback
from colorama import Fore, Back # type: ignore
from model.status_manager import status_dict, status_lock
from audio import play_alarm
import subprocess
from model.recorder import RECORD_START_TIME

RECORDING = False

def safe_log(msg, err=None):
    print(f"\n⚠️{Fore.LIGHTRED_EX} {Back.WHITE} {msg}")
    if err:
        traceback.print_exception(type(err), err, err.__traceback__, limit=1)

def any_thread_logo_active():
    # Verifica se alguma thread YOLO ainda detecta logo
    with status_lock:
        return any(st['logo'] for st in status_dict.values())


def cortar_video(arquivo_principal, start, end, pasta_saida):

    global RECORDING

    if RECORDING == True:
        return

    if RECORD_START_TIME is None:
        print("⚠️ Gravação ainda não iniciada")
        return

    RECORDING = True

    # 🔹 Converte tempos absolutos para relativos
    start = max(0, start - RECORD_START_TIME - 2)
    duracao = (end - start) + 4

    saida = f"{pasta_saida}/corte_{int(start)}_{int(end)}"
    cmd = [
        "ffmpeg",
        "-ss", str(max(0, start - 2)),
        "-i", arquivo_principal,
        "-t", str(duracao),
        "-c", "copy",
        f"{saida}.ts"
    ]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if result.returncode != 0:
        print("❌ Erro ao cortar vídeo:")
        print(result.stderr)
        RECORDING = False
    else:
        play_alarm()
        print(f"⭕ Corte feito")
        RECORDING = False

def stop_recording(process):
    """Interrompe o processo de gravação FFmpeg."""
    if process and process.poll() is None:
        process.terminate()
        print("\n\n🛑 Gravação interrompida.\n\n")
