import itertools
import traceback

spinner_cycle = itertools.cycle(['#', '+'])

def spinner():
    return next(spinner_cycle)

def safe_log(msg, err=None):
    print(f"\n⚠️ {msg}")
    if err:
        traceback.print_exception(type(err), err, err.__traceback__, limit=1)
