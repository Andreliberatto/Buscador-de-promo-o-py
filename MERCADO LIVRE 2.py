import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import webbrowser
from time import sleep

# Nome do Desenvolvedor
DESENVOLVEDOR = "Desenvolvido por André Amorim Liberatto"

# Função principal para a criação do app
def criar_app():
    global janela, loja_selecionada, mostrar_somente_promocoes, resultados_por_pagina, pagina_atual

    # Configuração da Interface Gráfica
    janela = tk.Tk()
    janela.title("Comparador de Preços")
    janela.geometry("1000x700")
    janela.configure(bg="#f7f7f7")

    # Variáveis globais
    loja_selecionada = tk.StringVar(value="Mercado Livre")
    mostrar_somente_promocoes = tk.BooleanVar(value=False)
    pagina_atual = 0
    resultados_por_pagina = 10  # Defina o número de resultados por página

    # Funções para buscar e exibir resultados
    def buscar_produtos_mercadolivre(nome_produto):
        """
        Busca produtos no Mercado Livre usando sua API.
        """
        resultados = []
        url_ml = f"https://api.mercadolibre.com/sites/MLB/search?q={nome_produto}"
        response_ml = requests.get(url_ml)
        if response_ml.status_code == 200:
            dados_ml = response_ml.json()
            for item in dados_ml.get('results', []):
                resultados.append({
                    'nome': item['title'],
                    'preco': item['price'],
                    'link': item['permalink'],
                    'imagem': item['thumbnail'],
                    'condicao': item['condition'],
                    'promocao': 'Frete grátis' if item.get('shipping', {}).get('free_shipping') else 'Sem promoção',
                    'loja': 'Mercado Livre'
                })

        return resultados

    def abrir_link(link):
        """
        Abre o link do produto no navegador padrão.
        """
        webbrowser.open(link)

    def exibir_resultados(resultados, frame):
        """
        Exibe os resultados encontrados na interface gráfica com paginação.
        """
        global pagina_atual, resultados_por_pagina

        for widget in frame.winfo_children():
            widget.destroy()

        inicio = pagina_atual * resultados_por_pagina
        fim = inicio + resultados_por_pagina
        pagina_resultados = resultados[inicio:fim]

        if not pagina_resultados:
            label = tk.Label(frame, text="Nenhum produto encontrado.", font=("Arial", 14), fg="#999")
            label.pack()
            return

        for produto in pagina_resultados:
            frame_produto = tk.Frame(frame, padx=10, pady=10, relief=tk.RAISED, borderwidth=3, bg="#ffffff")
            frame_produto.pack(fill=tk.X, pady=10)

            imagem_url = produto['imagem']
            try:
                response = requests.get(imagem_url, stream=True)
                imagem = Image.open(response.raw)
                imagem = imagem.resize((100, 100))
                foto = ImageTk.PhotoImage(imagem)
            except:
                foto = None

            if foto:
                label_imagem = tk.Label(frame_produto, image=foto, bg="#ffffff")
                label_imagem.image = foto
                label_imagem.grid(row=0, column=0, rowspan=2, padx=10)

            nome = tk.Label(frame_produto, text=produto['nome'], font=("Arial", 12, "bold"), wraplength=400, justify="left", bg="#ffffff")
            nome.grid(row=0, column=1, sticky="w")

            preco_text = f"Preço: R${produto['preco']:.2f}"
            if produto['promocao'] == 'Frete grátis':
                preco_text = f"Promoção: Frete grátis! - R${produto['preco']:.2f}"

            preco = tk.Label(frame_produto, text=preco_text, font=("Arial", 12), bg="#ffffff", fg="green")
            preco.grid(row=1, column=1, sticky="w")

            loja = tk.Label(frame_produto, text=f"Loja: {produto['loja']}", font=("Arial", 12), bg="#ffffff", fg="#666")
            loja.grid(row=2, column=1, sticky="w")

            link = tk.Button(frame_produto, text="Ver Produto", command=lambda url=produto['link']: abrir_link(url), bg="#0078d7", fg="white", font=("Arial", 10, "bold"))
            link.grid(row=0, column=2, padx=10)

    def atualizar_resultados():
        """
        Atualiza os resultados exibidos na interface com base nos filtros e paginação.
        """
        global resultados_atual

        # Filtro: Exibe apenas produtos com promoção se o Checkbutton estiver marcado
        resultados_filtrados = [
            produto for produto in resultados_atual
            if (not mostrar_somente_promocoes.get() or produto['promocao'] != 'Sem promoção')
        ]

        exibir_resultados(resultados_filtrados, frame_interno)

    def realizar_busca():
        """
        Realiza a busca pelo produto digitado no campo de entrada.
        """
        global resultados_atual, pagina_atual
        # Exibe uma mensagem de carregamento
        label_loading.pack()
        janela.update_idletasks()  # Atualiza a interface gráfica para exibir o carregamento

        nome_produto = entrada_produto.get()
        if not nome_produto:
            messagebox.showwarning("Atenção", "Digite o nome de um produto para pesquisar.")
            label_loading.pack_forget()
            return

        # Busca os resultados
        resultados_atual = buscar_produtos_mercadolivre(nome_produto)
        pagina_atual = 0
        sleep(1)  # Simula o tempo de carregamento
        atualizar_resultados()

        label_loading.pack_forget()  # Remove a mensagem de carregamento

    def proxima_pagina():
        """
        Avança para a próxima página de resultados.
        """
        global pagina_atual
        pagina_atual += 1
        atualizar_resultados()

    def pagina_anterior():
        """
        Volta para a página anterior de resultados.
        """
        global pagina_atual
        if pagina_atual > 0:
            pagina_atual -= 1
        atualizar_resultados()

    # Interface de busca e filtros
    frame_busca = tk.Frame(janela, padx=10, pady=10, bg="#f7f7f7")
    frame_busca.pack(fill=tk.X)

    label_produto = tk.Label(frame_busca, text="Produto:", font=("Arial", 14), bg="#f7f7f7")
    label_produto.pack(side=tk.LEFT, padx=5)

    entrada_produto = tk.Entry(frame_busca, font=("Arial", 14), width=40)
    entrada_produto.pack(side=tk.LEFT, padx=5)

    label_loja = tk.Label(frame_busca, text="Loja:", font=("Arial", 14), bg="#f7f7f7")
    label_loja.pack(side=tk.LEFT, padx=5)

    opcoes_lojas = ["Mercado Livre"]
    menu_loja = ttk.OptionMenu(frame_busca, loja_selecionada, *opcoes_lojas)
    menu_loja.pack(side=tk.LEFT, padx=5)

    checkbox_promocao = ttk.Checkbutton(frame_busca, text="Somente promoções", variable=mostrar_somente_promocoes, onvalue=True, offvalue=False, command=atualizar_resultados)
    checkbox_promocao.pack(side=tk.LEFT, padx=5)

    botao_buscar = tk.Button(frame_busca, text="Buscar", command=realizar_busca, bg="#0078d7", fg="white", font=("Arial", 12, "bold"))
    botao_buscar.pack(side=tk.LEFT, padx=5)

    label_loading = tk.Label(janela, text="Buscando...", font=("Arial", 14, "italic"), bg="#f7f7f7", fg="#999")
    label_loading.pack_forget()  # Inicialmente invisível

    # Frame com barra de rolagem para os resultados
    frame_resultados = tk.Frame(janela, padx=10, pady=10, bg="#ffffff")
    canvas_resultados = tk.Canvas(frame_resultados)
    scrollbar = tk.Scrollbar(frame_resultados, orient="vertical", command=canvas_resultados.yview)
    canvas_resultados.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas_resultados.pack(side="left", fill="both", expand=True)

    frame_interno = tk.Frame(canvas_resultados)
    canvas_resultados.create_window((0, 0), window=frame_interno, anchor="nw")
    
    frame_resultados.pack(fill=tk.BOTH, expand=True)

    # Navegação para próximo/anteior
    frame_navegacao = tk.Frame(janela, padx=10, pady=10, bg="#f7f7f7")
    frame_navegacao.pack(fill=tk.X)

    botao_anterior = tk.Button(frame_navegacao, text="Anterior", command=pagina_anterior, bg="#0078d7", fg="white", font=("Arial", 12, "bold"))
    botao_anterior.pack(side=tk.LEFT, padx=5)

    botao_proximo = tk.Button(frame_navegacao, text="Próximo", command=proxima_pagina, bg="#0078d7", fg="white", font=("Arial", 12, "bold"))
    botao_proximo.pack(side=tk.RIGHT, padx=5)

    # Rodapé com informações
    label_desenvolvedor = tk.Label(janela, text=DESENVOLVEDOR, font=("Arial", 10), bg="#f7f7f7", anchor="e")
    label_desenvolvedor.pack(fill=tk.X, pady=5)

    janela.mainloop()

# Chama a função para iniciar o aplicativo
criar_app()
