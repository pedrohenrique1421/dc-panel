import itertools
import traceback
from colorama import Fore, Back # type: ignore
from status_manager import status_dict, status_lock

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
