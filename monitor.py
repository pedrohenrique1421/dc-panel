import sys
import time
from colorama import Back, Fore, Style # type: ignore

def monitor_status(status_dict, status_lock):
    while True:
        with status_lock:
            if not status_dict:
                time.sleep(0.5)
                continue

            # Somar e calcular médias
            total_fps = sum(st['fps'] for st in status_dict.values())
            avg_cpu = sum(st['cpu'] for st in status_dict.values()) / len(status_dict)
            avg_yolo = sum(st['yolo_time'] for st in status_dict.values()) / len(status_dict)
            logo_on = any(st['logo'] for st in status_dict.values())  # se alguma thread detectar logo

            combined = (
                f"🧠 Threads: {len(status_dict)} | "
                f"{Fore.LIGHTYELLOW_EX}FPS:{Style.RESET_ALL} {total_fps:5.1f} | "
                f"{Fore.LIGHTCYAN_EX}CPU:{Style.RESET_ALL} {avg_cpu:5.1f}% | "
                f"{Fore.MAGENTA}YOLO:{Style.RESET_ALL} {avg_yolo*1000:6.1f} ms | "
                f"{Fore.LIGHTWHITE_EX}Logo:{Style.RESET_ALL} {'🟢 ON' if logo_on else '🔴 OFF'}   "
            )

        sys.stdout.write("\r" + combined)
        sys.stdout.flush()
        time.sleep(0.5)