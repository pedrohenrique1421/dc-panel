import itertools
import traceback
from colorama import Fore, Back # type: ignore

spinner_cycle = itertools.cycle(['◻', '◼'])

def spinner():
    return next(spinner_cycle)

def safe_log(msg, err=None):
    print(f"\n⚠️{Fore.LIGHTRED_EX} {Back.WHITE} {msg}")
    if err:
        traceback.print_exception(type(err), err, err.__traceback__, limit=1)
