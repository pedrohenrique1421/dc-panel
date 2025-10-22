import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import os
import webbrowser
import datetime
from tkvideo import tkvideo
from moviepy.video.io.VideoFileClip import VideoFileClip

# --- Variáveis Globais ---
tabela = None
player_video = None
ocorrencias_data = []

# --- Funções de Ajuda ---
def get_video_duration_moviepy(file_path):
    """Obtém a duração de um arquivo de vídeo usando a biblioteca moviepy."""
    try:
        with VideoFileClip(file_path) as clip:
            return clip.duration
    except Exception as e:
        messagebox.showerror("Erro de Dependência", f"Ocorreu um erro ao obter a duração com moviepy: {e}")
        return None


def format_duration(seconds):
    """Converte a duração em segundos para um formato legível (ex: '1m 2s')."""
    if seconds is None:
        return "N/A"

    total_seconds = int(round(seconds))

    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        minutes, remaining_seconds = divmod(total_seconds, 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"


# --- Funções de Upload ---
def adicionar_ocorrencia_na_tabela(nome_arquivo, tempo_video, data_ocorrencia_arquivo):
    """
    Adiciona uma nova ocorrência à lista de dados e atualiza a tabela,
    usando a data de ocorrência fornecida (data do arquivo).
    """
    global tabela

    # Usa a data de ocorrência do arquivo passada como argumento
    nova_ocorrencia = {
        "data": data_ocorrencia_arquivo,
        "tipo": "Automático",
        "tempo": tempo_video,
        "link": nome_arquivo
    }
    ocorrencias_data.append(nova_ocorrencia)

    mudar_pagina("Ocorrências", "Conteúdo da página de ocorrências.", "ocorrencias")


def upload_arquivo_ocorrencia():
    """
    Abre um diálogo para o usuário selecionar um arquivo, calcula a duração real,
    obtém a data de modificação do arquivo e o adiciona à tabela.
    """
    try:
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo de ocorrência",
            filetypes=[("Arquivos de Vídeo", "*.mp4;*.avi;*.mov"),
                       ("Todos os arquivos", "*.*")]
        )
        if filepath:
            nome_do_arquivo = os.path.basename(filepath)

            # Obtém o timestamp de modificação do arquivo
            timestamp_modificacao = os.path.getmtime(filepath)
            
            # Converte o timestamp para o formato de string desejado
            data_ocorrencia_arquivo = datetime.datetime.fromtimestamp(timestamp_modificacao).strftime("%Y-%m-%d %H:%M:%S")

            duration_seconds = get_video_duration_moviepy(filepath)
            tempo_formatado = format_duration(duration_seconds)
            
            # Chama a função de adição de ocorrência com a data do arquivo
            adicionar_ocorrencia_na_tabela(nome_do_arquivo, tempo_formatado, data_ocorrencia_arquivo)
            
            messagebox.showinfo(
                "Upload Selecionado",
                f"Arquivo selecionado e adicionado à tabela:\n{filepath}\n\nTempo do vídeo: {tempo_formatado}\nData da Ocorrência (Arquivo): {data_ocorrencia_arquivo}"
            )
        else:
            messagebox.showinfo("Nenhum Arquivo Selecionado", "O upload foi cancelado.")
    except Exception as e:
        messagebox.showerror("Erro de Upload", f"Ocorreu um erro: {e}")


# --- Funções de Impressão ---
def imprimir_pagina():
    """Simula a impressão de uma página."""
    messagebox.showinfo("Imprimir", "A função de impressão foi acionada!")


# --- Função para abrir o link do corte ---
def abrir_link_corte(event):
    """Abre o arquivo de vídeo associado à linha da tabela clicada."""
    item_selecionado = tabela.focus()
    if item_selecionado:
        valores = tabela.item(item_selecionado, 'values')
        link_do_corte = valores[3]
        caminho_completo = os.path.join(os.getcwd(), "corte", link_do_corte)
        if os.path.exists(caminho_completo):
            mudar_pagina("Reprodução do Vídeo", f"Reproduzindo: {link_do_corte}", "video", caminho_completo)
        else:
            messagebox.showerror("Arquivo Não Encontrado", f"O arquivo não foi encontrado:\n{caminho_completo}")


# --- Função para criar a tabela de ocorrências com paginação ---
def criar_tabela_ocorrencias(frame_pai):
    """Cria e preenche uma tabela (Treeview) com dados de ocorrências e paginação."""
    global tabela

    itens_por_pagina = 10
    pagina_atual = tk.IntVar(value=1)

    tabela_frame = ttk.Frame(frame_pai)
    tabela_frame.pack(fill='both', expand=True)

    colunas = ("data", "tipo", "tempo", "link")
    tabela = ttk.Treeview(tabela_frame, columns=colunas, show="headings")
    tabela.heading("data", text="Data da Ocorrência")
    tabela.heading("tipo", text="Tipo")
    tabela.heading("tempo", text="Tempo")
    tabela.heading("link", text="Link do Corte")

    tabela.column("data", width=180, anchor="center")
    tabela.column("tipo", width=100, anchor="center")
    tabela.column("tempo", width=100, anchor="center")
    tabela.column("link", width=250, anchor="center")

    scroll_y = ttk.Scrollbar(tabela_frame, orient="vertical", command=tabela.yview)
    tabela.configure(yscroll=scroll_y.set)
    scroll_y.pack(side="right", fill="y")
    tabela.pack(side="left", fill="both", expand=True)
    tabela.bind("<Double-1>", abrir_link_corte)

    paginacao_frame = ttk.Frame(frame_pai)
    paginacao_frame.pack(side="bottom", pady=10)

    # 🔹 Criar estilo de botão menor
    style = ttk.Style()
    style.configure("Small.TButton", padding=2, font=("Arial", 8))

    def atualizar_tabela():
        tabela.delete(*tabela.get_children())
        total_itens = len(ocorrencias_data)
        total_paginas = (total_itens + itens_por_pagina - 1) // itens_por_pagina
        pagina = pagina_atual.get()

        inicio = (pagina - 1) * itens_por_pagina
        fim = inicio + itens_por_pagina
        dados_pagina = ocorrencias_data[inicio:fim]

        for item in dados_pagina:
            tabela.insert("", "end", values=(item["data"], item["tipo"], item["tempo"], item["link"]))

        for widget in paginacao_frame.winfo_children():
            widget.destroy()

        ttk.Button(
            paginacao_frame,
            text="⟨ Anterior",
            command=lambda: mudar_pagina_atual(-1),
            style="Small.TButton",
            state="normal" if pagina > 1 else "disabled"
        ).pack(side="left", padx=2)

        total_paginas = max(total_paginas, 1) # Garante que haja pelo menos 1 página
        for i in range(1, total_paginas + 1):
            btn = ttk.Button(
                paginacao_frame,
                text=str(i),
                command=lambda i=i: ir_para_pagina(i),
                style="Small.TButton"
            )
            if i == pagina:
                btn.state(["disabled"])
            btn.pack(side="left", padx=2)

        ttk.Button(
            paginacao_frame,
            text="Próximo ⟩",
            command=lambda: mudar_pagina_atual(1),
            style="Small.TButton",
            state="normal" if pagina < total_paginas else "disabled"
        ).pack(side="left", padx=2)

    def mudar_pagina_atual(delta):
        nova_pagina = pagina_atual.get() + delta
        total_itens = len(ocorrencias_data)
        total_paginas = (total_itens + itens_por_pagina - 1) // itens_por_pagina
        if 1 <= nova_pagina <= total_paginas:
            pagina_atual.set(nova_pagina)
            atualizar_tabela()

    def ir_para_pagina(p):
        pagina_atual.set(p)
        atualizar_tabela()

    atualizar_tabela()
    return tabela


# --- Função para mudar o conteúdo da página ---
def mudar_pagina(titulo, texto, pagina_id=None, video_path=None):
    """Limpa o conteúdo anterior e exibe um novo conteúdo no frame principal."""
    global player_video

    if player_video:
        try:
            player_video.stop()
        except Exception:
            pass

    for widget in main_content_frame.winfo_children():
        widget.destroy()

    header_video_frame = ttk.Frame(main_content_frame)
    header_video_frame.pack(fill='x', pady=(10, 0))

    ttk.Label(header_video_frame, text=titulo, font=('Arial', 16, 'bold')).pack(side="left", padx=10)

    if pagina_id == "ocorrencias":
        header_video_frame.destroy()
        ttk.Label(main_content_frame, text=titulo, font=('Arial', 16, 'bold')).pack(pady=10)
        criar_tabela_ocorrencias(main_content_frame)

    elif pagina_id == "video" and video_path:
        ttk.Button(header_video_frame, text="X",
                   command=lambda: mudar_pagina("Ocorrências", "Conteúdo da página de ocorrências.", "ocorrencias")
                   ).pack(side="right", padx=10)
        video_label = ttk.Label(main_content_frame)
        video_label.place(relx=0.5, rely=0.5, anchor='center')
        try:
            player_video = tkvideo(video_path, video_label, loop=1, size=(600, 400))
            player_video.play()
        except Exception as e:
            messagebox.showerror("Erro de Reprodução", f"Ocorreu um erro ao reproduzir o vídeo: {e}")

    else:
        header_video_frame.destroy()
        ttk.Label(main_content_frame, text=texto, wraplength=500).pack(padx=20, pady=10)


# --- Janela Principal ---
janela = ThemedTk(theme="adapta")
janela.title("Globo.com")
janela.geometry("800x600")

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 10), padding=10)
style.configure('TLabel', font=('Helvetica', 10))

# --- Estrutura de Layout ---
header_frame = ttk.Frame(janela, style='TFrame')
header_frame.pack(fill='x', side='top', pady=5)
header_frame.grid_rowconfigure(0, weight=1)
header_frame.grid_columnconfigure(0, weight=1)  # Coluna do Logo
header_frame.grid_columnconfigure(1, weight=5)  # Coluna de Expansão (Título Secundário)
header_frame.grid_columnconfigure(2, weight=1)  # Coluna dos Botões

main_layout_frame = ttk.Frame(janela, style='TFrame')
main_layout_frame.pack(fill='both', expand=True, padx=10, pady=10)

sidebar_frame = ttk.Frame(main_layout_frame, style='TFrame', width=200)
sidebar_frame.pack(fill='y', side='left', padx=10, pady=10)

main_content_frame = ttk.Frame(main_layout_frame, style='TFrame')
main_content_frame.pack(fill='both', expand=True, padx=10, pady=10)

# --- Carregar Imagem ---
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_dir, "img", "globosf.png")
    
    # Tentativa de carregar a imagem real
    # Como não podemos garantir que a imagem existe no seu ambiente, 
    # faremos uma simulação ou usaremos um placeholder seguro.
    img = Image.open(img_path) 
    img = img.resize((80, 80), Image.LANCZOS)
    logo_globo = ImageTk.PhotoImage(img)
    
    logo_label = tk.Label(header_frame, image=logo_globo)
    logo_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')
    logo_label.image = logo_globo
    janela.iconphoto(False, logo_globo)
except Exception as e:
    # Caso a imagem falhe (provavelmente por FileNotFoundError), exibe um texto temporário
    # para não quebrar o layout, mas a ênfase é que a IMAGEM deve estar aqui.
    logo_label = ttk.Label(header_frame, text="GLOBO - Logo Placeholder", font=("Arial", 10, 'bold'), foreground="#453CF3")
    logo_label.grid(row=0, column=0, padx=10, pady=5, sticky='w')

# --- Cabeçalho (Área Central) ---
# REMOÇÃO: O title_label original foi removido para dar espaço ao logo.
# REPOSIÇÃO: Adicionamos um rótulo secundário discreto na coluna 1.
secondary_title_label = ttk.Label(header_frame, text="Sistema de Ocorrências", font=("Arial", 12), foreground="gray")
secondary_title_label.grid(row=0, column=1, pady=(5, 0), sticky='w') 

header_buttons_frame = ttk.Frame(header_frame, style='TFrame')
header_buttons_frame.grid(row=0, column=2, padx=10, pady=5, sticky='e')

ttk.Button(header_buttons_frame, text="IMPRIMIR RELATÓRIO", command=imprimir_pagina).pack(side="left", padx=5)
ttk.Button(header_buttons_frame, text="ENVIAR CLIP OCORRÊNCIA", command=upload_arquivo_ocorrencia).pack(side="left", padx=5)

# --- Sidebar ---
menu_opcoes = [
    ("Menu Principal", lambda: mudar_pagina("Página Principal", "Conteúdo principal da Globo.com.")),
    ("Ocorrências", lambda: mudar_pagina("Ocorrências", "Conteúdo da página de ocorrências.", "ocorrencias")),
    ("Relatórios", lambda: mudar_pagina("Relatórios", "Conteúdo da página de relatórios.")),
    ("Documentação", lambda: mudar_pagina("Documentação", "Conteúdo da página de documentação."))
]

for texto, comando in menu_opcoes:
    ttk.Button(sidebar_frame, text=texto, command=comando, width=25).pack(pady=5, padx=10)

# --- Página Inicial ---
mudar_pagina("Página Principal", "Conteúdo inicial da Globo.com.")

# --- Loop Principal ---
janela.mainloop()