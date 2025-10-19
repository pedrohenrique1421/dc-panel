import itertools
import traceback
from colorama import Fore, Back # type: ignore
from status_manager import status_dict, status_lock
import subprocess

spinner_cycle = itertools.cycle(['◻', '◼'])

def spinner():
    return next(spinner_cycle)

def safe_log(msg, err=None):
    print(f"\n⚠️{Fore.LIGHTRED_EX} {Back.WHITE} {msg}")
    if err:
        traceback.print_exception(type(err), err, err.__traceback__, limit=1)

def any_thread_logo_active():
    # Verifica se alguma thread YOLO ainda detecta logo
    with status_lock:
        return any(st['logo'] for st in status_dict.values())


def cortar_video(arquivo_principal, start, end, pasta_saida):
    duracao = (end + 2) - (start - 2)
    saida = f"{pasta_saida}/corte_{int(start)}_{int(end)}"
    cmd = [
        "ffmpeg",
        "-ss", str(max(0, start - 2)),
        "-i", arquivo_principal,
        "-t", str(duracao),
        "-c", "copy",
        f"{saida}.mp4"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Erro ao cortar vídeo:")
        print(result.stderr)
    else:
        print(f"🎬 Corte gerado com sucesso: {saida}")

def stop_recording(process):
    """Interrompe o processo de gravação FFmpeg."""
    if process and process.poll() is None:
        process.terminate()
        print("\n\n🛑 Gravação interrompida.\n\n")
