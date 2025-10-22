import threading

# === Status global das threads ===
status_dict = {}
status_lock = threading.Lock()