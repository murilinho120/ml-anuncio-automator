import requests
import json
from tkinter import Tk, Label, Entry, Button, Text, Frame, END, W, E, CENTER, filedialog, N, messagebox

# Defina seu client_id, client_secret e refresh_token aqui
CLIENT_ID1 = ''  # Substitua com seu Client ID
CLIENT_SECRET1 = ''  # Substitua com seu Client Secret
REFRESH_TOKEN1 = ''  # Substitua com seu Refresh Token

imagens_selecionadas = []
urls_por_operacao = []

def limpar_lista():

    # Exibe uma caixa de confirmação antes de limpar a lista
    confirmar = messagebox.askyesno("Confirmar Limpeza", "Tem certeza de que deseja limpar a lista?")
    if confirmar:
        lista_produtos.delete(1.0, END)  # Remove todo o conteúdo do campo de texto



def refresh_access_token(CLIENT_ID1, CLIENT_SECRET1, REFRESH_TOKEN1):
    url = "https://api.imgur.com/oauth2/token"
    payload = {
        'client_id': CLIENT_ID1,
        'client_secret': CLIENT_SECRET1,
        'refresh_token': REFRESH_TOKEN1,
        'grant_type': 'refresh_token'
    }
    
    response = requests.post(url, data=payload)
    

    if response.status_code == 200:
        new_access_token = response.json()['access_token']
        print("Access token atualizado com sucesso!")
        return new_access_token
    else:
        print("Erro ao atualizar o access token:", response.status_code, response.text)
        return None
ACCESS_IMGUR = refresh_access_token(CLIENT_ID1, CLIENT_SECRET1, REFRESH_TOKEN1)
print (f'staff 1 {ACCESS_IMGUR}')
# Lista de produtos
produtos = []


def selecionar_imagens(CLIENT_ID1, CLIENT_SECRET1, REFRESH_TOKEN1):
    # Obter o access token usando o refresh token
    access_token1 = refresh_access_token(CLIENT_ID1, CLIENT_SECRET1, REFRESH_TOKEN1)
    if not access_token1:
        print("Falha ao obter o access token.")
        return
    
    # Cria a interface de seleção de arquivo
    Tk().withdraw()  # Oculta a janela principal
    novos_caminhos = filedialog.askopenfilenames(
        title="Selecione até 5 imagens",
        filetypes=[("Imagens", "*.jpg;*.jpeg;*.png")],
    ) 

    # Adiciona os novos caminhos à lista global, verificando o limite
    for caminho in novos_caminhos:
        if len(imagens_selecionadas) < 5:
            imagens_selecionadas.append(caminho)
        else:
            print("Limite de 5 imagens alcançado.")
            break
    
    # Exibe as imagens selecionadas
    print("Imagens selecionadas:", imagens_selecionadas)


    # Função para fazer o upload da imagem para o Imgur e retornar a URL

def salvar_imagens(imagens_selecionadas):
    global CLIENT_ID1, CLIENT_SECRET1, REFRESH_TOKEN1
    client_id = "4db796e9e10d66c"  # Substitua pelo seu Client ID do Imgur
    headers = {
        'Authorization': f'Client-ID {client_id}'
    }

    urls = []
    for imagem in imagens_selecionadas:
        headers = {
            'Authorization': f'Bearer {ACCESS_IMGUR}'
        }
        with open(imagem, 'rb') as img:
            response = requests.post(
                "https://api.imgur.com/3/image",
                headers=headers,
                files={"image": img}
            )
        if response.status_code == 200:
            url = response.json()['data']['link']
            urls.append(url)
        else:
            print(f"Erro ao enviar a imagem {imagem}: {response.text}")
        
    # Adiciona as URLs geradas para a lista principal
    if urls:
        urls_por_operacao.append(urls)
        print(f"Operação concluída. URLs salvas: {urls}")
    else:
        print("Nenhuma URL foi gerada nesta operação.")
    
    return urls

# Adicione aqui sua lógica para seleção das imagens
#imagens_selecionadas = ["caminho/para/imagem1.jpg", "caminho/para/imagem2.png"]  # Exemplo
#salvar_imagens(imagens_selecionadas)
#--------------------------------------------------------------
# Função para atualizar o token de acesso usando o refresh token
def refresh_token():
    refresh_token_value = ''

    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        'grant_type': 'refresh_token',
        'client_id': '',
        'client_secret': '',
        'refresh_token': refresh_token_value
    }
    headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        print("Token atualizado com sucesso.")
        return access_token
    else:
        print(f"Erro ao atualizar o token: {response.status_code}")
        print(response.json())
        return None

# Chamada da função para obter o token atualizado
ACCESS_TOKEN = refresh_token()

if ACCESS_TOKEN is None:
    raise Exception("Não foi possível atualizar o access token. Verifique as credenciais.")

# Função para adicionar produto à lista e atualizar o campo de texto
def adicionar_produto():
    imagens = salvar_imagens(imagens_selecionadas)

    title = entrada.get()
    
    # Verifique o comprimento do título
    if len(title) > 60:
        erro_titulo_label.config(text="Título deve ter no máximo 60 caracteres")
        return  # Interrompe a função se o limite for excedido
    else:
        erro_titulo_label.config(text="")  # Limpa a mensagem de erro se estiver dentro do limite
    
    price = valor.get()
    brand = marca.get()
    part_number = cod.get()
    car_name = car.get()
    car_year = ano_car.get()

    #alterar , por . no valor
    price = valor.get().replace(',', '.')  # Substitui vírgula por ponto

    category_suggestion_url = f'https://api.mercadolibre.com/sites/MLB/domain_discovery/search?limit=1&q={title}'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    
    category_response = requests.get(category_suggestion_url, headers=headers)
    if category_response.status_code == 200 and category_response.json():
        category_id = category_response.json()[0]["category_id"]
        print(f"Categoria sugerida obtida: {category_id}")
    else:
        print("Erro ao obter a categoria sugerida.")
        category_id = "MLB116012"  # ID de categoria padrão

    produto = {
        "Título": title,
        "Preço": price,
        "Marca": brand,
        "Código": part_number,
        "Carro": car_name,
        "Ano": car_year,
        "Categoria": category_id,
        "Imagens": imagens  # Adiciona as URLs de imagens ao produto
    }
    produtos.append(produto)
    atualizar_lista()

    entrada.delete(0, END)
    valor.delete(0, END)
    marca.delete(0, END)
    cod.delete(0, END)
    car.delete(0, END)
    ano_car.delete(0, END)

# Função para atualizar exibição da lista de produtos
def atualizar_lista():
    lista_produtos.delete(1.0, END)
    for idx, produto in enumerate(produtos):
        item_texto = f"{idx} - Título: {produto['Título']}, Preço: {produto['Preço']}, Marca: {produto['Marca']}, Código: {produto['Código']}, Carro: {produto['Carro']}, Ano: {produto['Ano']}\n"
        lista_produtos.insert(END, item_texto)

# Função para excluir produto com base no índice
def excluir_produto():
    try:
        index = int(indice_entry.get())
        if 0 <= index < len(produtos):
            produtos.pop(index)
            atualizar_lista()
            erro_excluir_label.config(text="Produto excluído com sucesso.", fg="green")
        else:
            erro_excluir_label.config(text="Índice inválido.", fg="red")
    except ValueError:
        erro_excluir_label.config(text="Digite um índice numérico.", fg="red")

# Função para criar anúncios para todos os itens na lista de produtos
def criar_anuncios():
    for produto in produtos:
        title = produto["Título"]
        price = produto["Preço"]
        brand = produto["Marca"]
        part_number = produto["Código"]
        car_name = produto["Carro"]
        car_year = produto["Ano"]
        category_id = produto["Categoria"]
        imagens = produto["Imagens"]

        pictures = [{"source": url} for url in imagens]  # Constrói a lista de URLs

        data = {
            "site_id": "MLB",
            "title": title,
            "category_id": category_id,
            "price": float(price),
            "available_quantity": 1,
            "currency_id": "BRL",
            "condition": "used",
            "listing_type_id": "gold_pro",
            "pictures": pictures,
            "attributes": [
                {"id": "PART_NUMBER", "value_name": part_number},
                {"id": "BRAND", "value_name": brand},
                {"id": "ORIGIN", "value_name": "Brasil"}
            ],
            "shipping": {
                "mode": "me2",
                "local_pick_up": True,
                "free_shipping": False,
                "logistic_type": "not_specified",
                "store_pick_up": True
            },
            "sale_terms": [
                {
                    "id": "WARRANTY_TYPE",
                    "name": "Tipo de garantia",
                    "value_id": "2230280",
                    "value_name": "Garantia do vendedor"
                },
                {
                    "id": "WARRANTY_TIME",
                    "name": "Tempo de garantia",
                    "value_id": None,
                    "value_name": "30 dias",
                    "value_struct": {"number": 30, "unit": "dias"}
                }
            ],
            "description": {
                "plain_text": 'RVC AUTO PEÇAS'  # Adicione a descrição aqui
            }
        }

        url = 'https://api.mercadolibre.com/items'
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print(f"Anúncio '{title}' criado com sucesso!")
        else:
            print(f"Erro ao criar o anúncio '{title}': {response.status_code} - {response.text}")

# Interface gráfica
menu = Tk()
menu.title("Anúncio de Produto")
menu.geometry("1200x600")
menu.configure(bg="#f0f0f5")  # Cor de fundo clara

# Título principal
Label(menu, text="MERCADO LIVRE", font=("Helvetica", 18, "bold"), bg="#f0f0f5", fg="#0052cc").grid(column=0, row=0, columnspan=8, pady=20)

# Frame de entrada de dados
frame_dados = Frame(menu, bg="#f0f0f5")
frame_dados.grid(column=0, row=1, columnspan=8, padx=20, pady=10, sticky=W)

# Campos de entrada
Label(frame_dados, text="Título do Produto:", bg="#f0f0f5").grid(column=0, row=1, pady=5, padx=5, sticky=E)
entrada = Entry(frame_dados, width=30)
entrada.grid(column=1, row=1, padx=5, pady=5)

# Erro do título
erro_titulo_label = Label(frame_dados, text="", fg="red", bg="#f0f0f5")
erro_titulo_label.grid(column=1, row=0, padx=5, pady=5)

Label(frame_dados, text="Valor $$$:", bg="#f0f0f5").grid(column=2, row=1, pady=5, padx=5, sticky=E)
valor = Entry(frame_dados, width=15)
valor.grid(column=3, row=1, padx=5, pady=5)

Label(frame_dados, text="Marca:", bg="#f0f0f5").grid(column=4, row=1, pady=5, padx=5, sticky=E)
marca = Entry(frame_dados, width=20)
marca.grid(column=5, row=1, padx=5, pady=5)

Label(frame_dados, text="Código do Produto:", bg="#f0f0f5").grid(column=6, row=1, pady=5, padx=5, sticky=E)
cod = Entry(frame_dados, width=20)
cod.grid(column=7, row=1, padx=5, pady=5)

# Botão de Adicionar Produto
Button(frame_dados, text="Adicionar", command=adicionar_produto, bg="#4CAF50", fg="white", width=12).grid(column=8, row=1, padx=15, pady=5)

# Campo extra de informações do carro
Label(frame_dados, text="Nome do carro:", bg="#f0f0f5").grid(column=0, row=2, pady=5, padx=5, sticky=E)
car = Entry(frame_dados, width=30)
car.grid(column=1, row=2, padx=5, pady=5)

Label(frame_dados, text="Ano do carro:", bg="#f0f0f5").grid(column=2, row=2, pady=5, padx=5, sticky=E)
ano_car = Entry(frame_dados, width=15)
ano_car.grid(column=3, row=2, padx=5, pady=5)

# Lista de Produtos
Label(menu, text="Lista de Produtos:", font=("Helvetica", 12, "bold"), bg="#f0f0f5").grid(column=0, row=3, padx=5, pady=5, sticky=W)
lista_produtos = Text(menu, height=5, width=75, bg="#ffffff", fg="black", font=("Helvetica", 10))
lista_produtos.grid(column=0, row=4, columnspan=1, padx=5, pady=5)

# Frame de exclusão ao lado direito da lista
frame_excluir = Frame(menu, bg="#f0f0f5")
frame_excluir.grid(column=1, row=4, padx=10, pady=10, sticky=N)  # Alinhado ao topo para manter a altura consistente

Label(frame_excluir, text="Índice para excluir:", font=("Helvetica", 11, "bold"), bg="#f0f0f5").grid(column=0, row=0, pady=5, padx=5)
indice_entry = Entry(frame_excluir, width=10)
indice_entry.grid(column=0, row=1, padx=5, pady=5)

Button(frame_excluir, text="Excluir Item", command=excluir_produto, bg="#ff4d4d", fg="white", width=10).grid(column=0, row=2, pady=0, padx=5)
erro_excluir_label = Label(frame_excluir, text="", fg="red", bg="#f0f0f5")
erro_excluir_label.grid(column=0, row=3, pady=5, padx=5)

Button(frame_excluir, text="Limpar Lista", command=limpar_lista, bg="#ff4d4d", fg="white", width=12).grid(column=4, row=0, pady=0, padx=150)

# Botão de Criar Anúncios
Button(frame_excluir, text="Criar Anúncios", command=criar_anuncios, bg="#0052cc", fg="white", font=("Helvetica", 12, "bold"), width=15).grid(column=4, row=2, padx=150)

# Campo de seleção de imagens
Label(menu, text="Selecionar Imagens:", font=("Helvetica", 12, "bold"), bg="#f0f0f5").grid(column=0, row=5, padx=5, pady=10, sticky=W)
lista_imagens = [Entry(menu, width=80) for _ in range(5)]
for i, entry in enumerate(lista_imagens):
    entry.grid(column=0, row=6 + i, columnspan=1, padx=5, pady=5)
# Botão para selecionar imagens
Button(menu, text="Selecionar Imagens", command=lambda: selecionar_imagens(CLIENT_ID1, CLIENT_SECRET1, REFRESH_TOKEN1), bg="#4CAF50", fg="white", width=20).grid(column=1, row=6, padx=15, pady=5, sticky=W)


# Botão para upload das imagens
#Button(menu, text="Upload Imagens", command=upload_imagens, bg="#0052cc", fg="white", font=("Helvetica", 12, "bold"), width=15).grid(column=0, row=15, columnspan=1, pady=20)

menu.mainloop()