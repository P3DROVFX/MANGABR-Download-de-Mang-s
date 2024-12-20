import os
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
from io import BytesIO


#CONVERTER IMAGENS EM WEBP PARA JPEG
def converterImagem(url_imagem, caminho_destino):
    try:
        response = requests.get(url_imagem) #get da url da pagina
        response.raise_for_status()  #verifica se terá erro http e vai retornar
        
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGB")
        
        caminho_destino = os.path.splitext(caminho_destino)[0] + ".jpg"
        img.save(caminho_destino, "JPEG")
        
        print(f"[LOG][CONVERSION] Imagem CONVERTIDA e salva em {caminho_destino}")
        return caminho_destino
        
    except Exception as e:
        print(f"[LOG][ERROR] Erro ao converter imagem: {e}")
        return None

def extrair_cap_titulo(soup): #FUNÇÃO PARA EXTRAIR O NÚMERO DO CAP DO TÍTULO DO HTML, NÃO USE SE O NOME DO MANGÁ TIVER NÚMEROS
    #Extrair a string do titulo
    
    titulo = soup.title.string.strip()
    
    if titulo:
        #Regex que busca somente números
        match = re.search(r'\d+', titulo)
        if match:
            return str(match.group())  #Devemos retornar como string
    return "Cap S/N"  # Retorna o texto se o título não existir ou não contiver número, seráusado como nome da pasta, deve ser renomeado depois


def downloadMangabr(base_url, pasta_destino):
    # Pasta para salvar as imagens
    if not os.path.exists(pasta_destino): #Criar pasta se ela não existir
        os.makedirs(pasta_destino)
    
        # Itera sobre o intervalo de páginas
    for pagina in range(inicio, fim + 1):
        url = f"{base_url}/{pagina}"  #formatando a string com o padrão do site, que é a url base / a página, que geralmente está apenas com um número começando do 1

        try:
            # Faz a requisição à página
            response = requests.get(url) #get da url da pagina
            response.raise_for_status()  #verifica se terá erro http e vai retornar
            soup = BeautifulSoup(response.text, 'html.parser')  #O primeiro parametro do método vai pegar o url e retornar seu conteúdo, o segundo irá interpretar o código html usando parser, que é do python

            #COMENTAR ESSA PARTE SE ESTIVER COM PROBLEMAS NO NÚMERO DO CAP, USAR A PARTE COMENTADA LA DE CIMA
            cap = extrair_cap_titulo(soup)  #Chamada da função

            # MUDAR O NOME DO SERVIDOR QUE FICA ARMAZENADO AS IMAGENS, PROCURAR EM FONTES NO MENU INSPECIONAR
            img_tag = soup.find("img", src=lambda src: src and servidorMangaBr in src) #o método find retorna apenas o primeiro elemento a encontrar, se quiser todos usar find_all que retornna um array
            #Passamos a tag img para pegarmos apenas imagens // usamos uma função que filtra as fontes das imagens, ele apenas retorna o que eses filtro encontra
            if not img_tag:
                print(f"[LOG][ERROR] Nenhuma Imagem encontrada na página {pagina}")
                continue
            
            img_url = img_tag["src"] #Pega a url da imagem
            print(f"[LOG][FOUND] Imagem encontrada: {img_url}") #Exibe no terminal
            
            subpasta = os.path.join(pasta_destino, cap)  #Criando a subpasta com o nome do cap que já extraimos
            os.makedirs(subpasta, exist_ok=True)  #Cria o dir
            nome_arquivo = os.path.join(subpasta, f"P{pagina}.jpg") #Criaremos o nome do arquivo, Join junta dois caminhos que será a localização da pasta e página, que está em ordem crescente

            response = requests.get(img_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))

            if (img.format == "WEBP"):
                print("[LOG][FOUND] Imagem em WEBP detectada")
                converterImagem(img_url, nome_arquivo)
            else:
                img = img.save(nome_arquivo, "JPEG")
                print(f"[LOG][SAVE]: Imagem salva em {nome_arquivo}") #exibe no terminal a resposta
                
        except Exception as e:  #Para qualquer erro encontrado
            print(f"[LOG][ERROR] Erro ao processar a página {pagina}: {e}") #Exibimos qual a página e sua exception


def downloadMangajikan(base_url, pasta_destino):
    print("[LOG][DEBUG] entrou na def")
    # Cria a pasta de destino se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    try:
        # Faz a requisição à página do capítulo
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrai o número do capítulo da URL ou título (se necessário)
        capitulo = extrair_cap_titulo(soup)
        subpasta = os.path.join(pasta_destino, f"Capítulo_{capitulo}")
        os.makedirs(subpasta, exist_ok=True)

        # Encontra todas as imagens no HTML
        imagens = soup.find_all("li", class_="img")
        if not imagens:
            print("[LOG][ERROR] Nenhuma imagem encontrada no capítulo.")
            return

        # Itera pelas imagens encontradas
        for img_tag in imagens:
            img_url = img_tag.find("img")["src"]
            data_index = img_tag["data-index"]
            nome_arquivo = os.path.join(subpasta, f"P{data_index}.jpg")

            try:
                print(f"[LOG][FOUND] Baixando imagem: {img_url}")
                response = requests.get(img_url)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))

                # Verifica o formato da imagem e converte se necessário
                if img.format == "WEBP":
                    print("[LOG][FOUND] Imagem em WEBP detectada")
                    converterImagem(img_url, nome_arquivo)
                else:
                    img.save(nome_arquivo, "JPEG")
                    print(f"[LOG][SAVE]: Imagem salva em {nome_arquivo}")

            except Exception as e:
                print(f"[LOG][ERROR] Erro ao baixar ou salvar a imagem {data_index}: {e}")

    except Exception as e:
        print(f"[LOG][ERROR] Erro ao acessar a página do capítulo: {e}")
        
def downloadSenManga(base_url, pasta_destino):
    # Pasta para salvar as imagens
    if not os.path.exists(pasta_destino): #Criar pasta se ela não existir
        os.makedirs(pasta_destino)
    
        # Itera sobre o intervalo de páginas
    for pagina in range(inicio, fim + 1):
        url = f"{base_url}/{pagina}"  #formatando a string com o padrão do site, que é a url base / a página, que geralmente está apenas com um número começando do 1

        try:
            # Faz a requisição à página
            response = requests.get(url) #get da url da pagina
            response.raise_for_status()  #verifica se terá erro http e vai retornar
            soup = BeautifulSoup(response.text, 'html.parser')  #O primeiro parametro do método vai pegar o url e retornar seu conteúdo, o segundo irá interpretar o código html usando parser, que é do python

            #COMENTAR ESSA PARTE SE ESTIVER COM PROBLEMAS NO NÚMERO DO CAP, USAR A PARTE COMENTADA LA DE CIMA
            cap = extrair_cap_titulo(soup)  #Chamada da função

            # MUDAR O NOME DO SERVIDOR QUE FICA ARMAZENADO AS IMAGENS, PROCURAR EM FONTES NO MENU INSPECIONAR
            img_tag = soup.find("img", src=lambda src: src and servidorSenManga in src) #o método find retorna apenas o primeiro elemento a encontrar, se quiser todos usar find_all que retornna um array
            #Passamos a tag img para pegarmos apenas imagens // usamos uma função que filtra as fontes das imagens, ele apenas retorna o que eses filtro encontra
            if not img_tag:
                print(f"[LOG][ERROR] Nenhuma Imagem encontrada na página {pagina}")
                continue
            
            img_url = img_tag["src"] #Pega a url da imagem
            print(f"[LOG][FOUND] Imagem encontrada: {img_url}") #Exibe no terminal
            
            subpasta = os.path.join(pasta_destino, cap)  #Criando a subpasta com o nome do cap que já extraimos
            os.makedirs(subpasta, exist_ok=True)  #Cria o dir
            nome_arquivo = os.path.join(subpasta, f"P{pagina}.jpg") #Criaremos o nome do arquivo, Join junta dois caminhos que será a localização da pasta e página, que está em ordem crescente

            response = requests.get(img_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))

            if (img.format == "WEBP"):
                print("[LOG][FOUND] Imagem em WEBP detectada")
                converterImagem(img_url, nome_arquivo)
            else:
                img = img.save(nome_arquivo, "JPEG")
                print(f"[LOG][SAVE]: Imagem salva em {nome_arquivo}") #exibe no terminal a resposta
                
        except Exception as e:  #Para qualquer erro encontrado
            print(f"[LOG][ERROR] Erro ao processar a página {pagina}: {e}") #Exibimos qual a página e sua exception
        

#SERVIDORES DE CADA SITE
servidorMangaBr = "manga-brazil.b-cdn.net"
servidorSenManga = "cdn.kumacdn.club"

#NOME DE PASTA QUE FICARÁ SALVA
diretorio = "Capítulos Baixados"

#Intervalo de páginas, deixar fim maior para garantir que irá baixar todas
inicio = 1
fim = 18
fila = []


while(True):
    try:
        print("--------- SCRIPT DE DOWNLOAD DE MANGÁS ---------")
        print("""
            1 - DEFINIR CAPÍTULOS QUE IRÁ BAIXAR
            2 - INICIAR SCRIPT
            3 - ALTERAR DIRETÓRIO DE SALVAMENTO
            
            0 - SAIR
            """)
        entrada = int(input("DIGITE UMA ENTRADA: "))
        if (entrada == 1):
            base_url = input(str("Url do cap a ser baixado: ")) #Input da url do capítulo
            fila.append(base_url)
            print("URL ADICIONADA A FILA, ADICIONE MAIS URLS(1) OU EXECUTE O SCRIPT(2)")
            
        elif (entrada == 2):
            if not fila:
                print("Fila está vazia, adicione urls com o comando 1")
            else:
                print("[LOG][START] SCRIPT INICIADO")
                while fila:
                    base_url = fila.pop(0)
                    if (base_url.startswith("https://www.mangajikan.com")):
                        downloadMangajikan(base_url, diretorio)
                    elif (base_url.startswith("https://mangabr.net/")):
                        downloadMangabr(base_url, diretorio)
                    elif (base_url.startswith("https://raw.senmanga.com")):
                        downloadSenManga(base_url, diretorio)
                    else: 
                        print(f"[LOG][ERROR] URL inválida: {base_url}")
                print("[LOG][OFF] SCRIPT FINALIZADO")
        
        elif(entrada == 3):
            entrada_diretorio = input(str("Novo diretório de salvamento: "))
            diretorio = entrada_diretorio + "\Capítulos Baixados"
            print("Diretório de salvamento alterado!")
            
        elif(entrada == 0):
            break
        
        else:
            print("ENTRADA INVÁLIDA")
    except Exception as e:
        print(f"[LOG][ERROR] Entrada inválida: {e}")


# EM CASO DE O TÍTULO DA OBRA TER NÚMEROS NO NOME, USAR ISSO NO LUGAR DA FUNÇÃO QUE AUTOMATIZA
# cap = input(str("Número do cap sendo baixado: ")) #ENTRAR COM O NÚMERO DO CAP




    