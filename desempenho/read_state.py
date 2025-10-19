import json
import os

def load_data(filename):
    """Carrega e retorna o conteúdo JSON do arquivo."""
    if not os.path.exists(filename):
        print(f"⚠️  O arquivo '{filename}' não existe.")
        return []

    try:
        with open(filename, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        print(f"❌ Erro: o arquivo '{filename}' está vazio ou corrompido.")
        return []

def show_data(filename):
    """Lê e exibe os dados formatados no terminal."""
    data = load_data(filename)

    if not data:
        print("📭 Nenhum dado encontrado.")
        return

    print(f"\n📄 Dados armazenados em '{filename}':\n")
    for i, item in enumerate(data, 1):
        print(f"🔹 Registro {i}:")
        if isinstance(item, dict):
            for key, value in item.items():
                print(f"   {key}: {value}")
        else:
            print(f"   {item}")
        print()  # linha em branco entre registros

# Executa se o arquivo for rodado diretamente
if __name__ == "__main__":
    FILENAME = "data.json"  # nome do arquivo a ser lido
    show_data(FILENAME)
