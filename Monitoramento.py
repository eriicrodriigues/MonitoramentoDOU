import os
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
URL = os.environ["URL"]
SELECTOR = "search-total-label text-default"
ULTIMO_VALOR_ARQUIVO = "ultimo_valor.txt"

def obter_conteudo():
    """ Obtém o conteúdo do site e retorna o texto da classe monitorada """
    try:
        resposta = requests.get(URL, timeout=10)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.text, "html.parser")
        elemento = soup.find(class_=SELECTOR)
        return elemento.text.strip() if elemento else None
    except Exception as e:
        print(f"Erro ao acessar o site: {e}")
        return None

def enviar_notificacao(mensagem):
    """ Envia uma mensagem no Telegram """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
        response = requests.post(url, params=params)
        if response.status_code == 200:
            print("Mensagem enviada com sucesso!")
        else:
            print(f"Erro ao enviar mensagem: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def verificar_mudanca():
    """ Verifica se houve mudança no conteúdo do site """
    novo_conteudo = obter_conteudo()

    if not novo_conteudo:
        print("❌ Não foi possível obter o conteúdo.")
        return

    if os.path.exists(ULTIMO_VALOR_ARQUIVO):
        with open(ULTIMO_VALOR_ARQUIVO, "r", encoding="utf-8") as f:
            ultimo_valor = f.read().strip()
    else:
        ultimo_valor = ""

    if novo_conteudo != ultimo_valor:
        print("🔔 Alteração detectada!")
        mensagem = (
            "⚠️ O site do DOU foi atualizado!\n\n"
            f"Novo valor: {novo_conteudo}\n\n"
            f"🔗 Veja aqui: {URL}"
        )
        enviar_notificacao(mensagem)

        with open(ULTIMO_VALOR_ARQUIVO, "w", encoding="utf-8") as f:
            f.write(novo_conteudo)
    else:
        print("✅ Nenhuma alteração detectada.")

verificar_mudanca()
