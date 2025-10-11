import json
import os

def save_data(obj, filename):
    if not filename or obj is None:
        return False

    # Se o arquivo não existe, cria com lista vazia
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump([], f)

    # Tenta carregar o conteúdo atual
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            # Se não for uma lista, converte para lista
            if not isinstance(data, list):
                data = [data]
    except json.JSONDecodeError:
        data = []

    # Adiciona o novo objeto
    data.append(obj)

    # Salva de volta
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return True
