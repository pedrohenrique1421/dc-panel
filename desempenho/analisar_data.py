import json
from collections import defaultdict
from statistics import mean
from colorama import Fore, Style # type: ignore

FILENAME = "data.json"

def carregar_dados(filename):
    with open(filename, "r") as f:
        return json.load(f)

def analisar_por_cpu_load(dados):
    grupos = defaultdict(list)

    # Agrupa registros pelo valor de cpu_load_time
    for item in dados:
        cpu_val = float(item.get("cpu_load_time", 0))
        grupos[cpu_val].append(item)

    # Calcula médias e exibe resultados
    for cpu_val, items in sorted(grupos.items()):
        media_fps = mean(float(i["fps"]) for i in items)
        media_cpu = mean(float(i["avg_cpu"]) for i in items)
        media_yolo = mean(float(i["avg_yolo"]) for i in items)
        media_logo = any(i["logo_on"] for i in items)
        data = items[-1]["date_time"]  # pega a data do último registro

        print(f"\n{Fore.CYAN}cpu_load_time = {cpu_val:.3f}:{Style.RESET_ALL}")
        print(f"   média_fps:       {media_fps:6.2f}")
        print(f"   média_avg_cpu:   {media_cpu:6.2f}")
        print(f"   média_avg_yolo:  {media_yolo:6.2f}")
        print(f"   média_logo_on:   {media_logo}")
        print(f"   date_time:       {data}")
        print(f"   cpu_load_time:   {cpu_val:.3f}")
        print(Style.RESET_ALL)

if __name__ == "__main__":
    dados = carregar_dados(FILENAME)
    analisar_por_cpu_load(dados)
