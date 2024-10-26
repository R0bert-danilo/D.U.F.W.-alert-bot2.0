import asyncio
import json
import os
from datetime import datetime
import discord
import requests
import pyfiglet
from colorama import Fore, Style, init

init()

CONFIG_FILE = "config.json"


# Função para carregar configurações
def carregar_configuracoes():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


# Função para salvar configurações
def salvar_configuracoes(bot_token, chat_id_alertas, chat_id_relatorio, discord_token, config_nome):
    configurations = {
        "telegram_bot_token": bot_token,
        "telegram_chat_id_alertas": chat_id_alertas,
        "telegram_chat_id_relatorio": chat_id_relatorio,
        "discord_token": discord_token,
        "nome_config": config_nome
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(configurations, f, indent=4)


# Função para excluir configurações
def excluir_configuracoes():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        print("Configurações excluídas com sucesso!")
    else:
        print("Nenhuma configuração encontrada para excluir.")


# Carregar configurações
configuracoes = carregar_configuracoes()
telegram_bot_token = configuracoes.get("telegram_bot_token", '')
telegram_chat_id_alertas = configuracoes.get("telegram_chat_id_alertas", '')
telegram_chat_id_relatorio = configuracoes.get("telegram_chat_id_relatorio", '')
global_token = configuracoes.get("discord_token", '')
global_nome_configuracao = configuracoes.get("nome_config", '')


# Função para enviar mensagem para o Telegram
def enviar_mensagem_telegram(mensagem, chat_id):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': mensagem,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Falha ao enviar mensagem para o Telegram: {response.status_code} - {response.text}")


# Função para configurar o bot
def configurar_bot():
    global telegram_bot_token, telegram_chat_id_alertas, telegram_chat_id_relatorio, global_token, global_nome_configuracao
    print("\n--- Configuração do Bot ---")
    telegram_bot_token = input("Digite o Token do Bot do Telegram: ")
    telegram_chat_id_alertas = input("Digite o ID do Chat do Telegram para alertas de palavras proibidas: ")
    telegram_chat_id_relatorio = input("Digite o ID do Chat do Telegram para recebimento de relatórios: ")
    global_token = input("Digite o Token do Bot do Discord: ")
    global_nome_configuracao = input("Digite um nome para salvar as configurações: ")
    salvar_configuracoes(telegram_bot_token, telegram_chat_id_alertas, telegram_chat_id_relatorio, global_token,
                         global_nome_configuracao)
    print("\nConfigurações salvas com sucesso!\n")
    clear_screen()


# Função para ver configurações
def ver_configuracoes():
    global telegram_bot_token, telegram_chat_id_alertas, telegram_chat_id_relatorio, global_token, global_nome_configuracao
    if not telegram_bot_token or not telegram_chat_id_alertas or not global_token:
        print("Nenhuma configuração salva.")
    else:
        print("\n--- Configurações Salvas ---")
        print(f"Nome da Configuração: {global_nome_configuracao}")
        print(f"Token do Bot do Telegram: {telegram_bot_token}")
        print(f"ID do Chat do Telegram para alertas: {telegram_chat_id_alertas}")
        print(f"ID do Chat do Telegram para relatórios: {telegram_chat_id_relatorio}")
        print(f"Token do Bot do Discord: {global_token}\n")
        excluir = input("Deseja excluir as configurações? (s/n): ").strip().lower()
        if excluir == 's':
            excluir_configuracoes()
            telegram_bot_token = ''
            telegram_chat_id_alertas = ''
            telegram_chat_id_relatorio = ''
            global_token = ''
            global_nome_configuracao = ''
    clear_screen()


# Função para limpar a tela
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# Função para apresentação
async def apresentacao():
    letras = ['D . U . F . W . alert']
    cores = [Fore.RED]
    for i, letra in enumerate(letras):
        result = pyfiglet.figlet_format(letra)
        print(cores[i] + result + Style.RESET_ALL)
        await asyncio.sleep(2)
        clear_screen()
    print(Fore.MAGENTA + "Bem-vindo ao bot de monitoramento!" + Style.RESET_ALL)
    await asyncio.sleep(2)
    clear_screen()


# Função para exibir o menu
async def exibir_menu():
    while True:
        print("\n=== Menu Principal ===")
        print("1. Configurar Bot (Tokens e IDs)")
        print("2. Ver Configurações Salvas")
        print("3. Excluir Configurações")
        print("4. Criar Relatório")
        print("5. Iniciar Monitoramento")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")
        if opcao == '1':
            configurar_bot()
        elif opcao == '2':
            ver_configuracoes()
        elif opcao == '3':
            excluir_configuracoes()
            clear_screen()
        elif opcao == '4':
            await criar_relatorio()
            clear_screen()
        elif opcao == '5':
            await iniciar_monitoramento()
            clear_screen()
        elif opcao == '6':
            print("Saindo...")
            break
        else:
            print("Opção inválida, tente novamente.")


# Função para criar o relatório
async def criar_relatorio():
    global global_token
    if not global_token:
        print("Você precisa configurar o bot antes de criar o relatório!")
        return
    print("\n--- Criando Relatório ---")
    intents = discord.Intents.default()
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        # Inicia a criação do relatório
        for guild in client.guilds:  # Percorrendo todos os servidores
            texto_relatorio = f"🔹 **Servidor**: {guild.name}\n\n"

            # Adicionar administradores
            admins = [member for member in guild.members if member.guild_permissions.administrator]
            if admins:
                for admin in admins:
                    texto_relatorio += f"👑 **Administrador**: {admin.name} - ID: {admin.id}\n"
            else:
                texto_relatorio += "👑 **Administrador**: Não encontrado\n"

            # Adicionar o bot
            texto_relatorio += f"\n🤖 **Bot**: {client.user.name} - ID: {client.user.id}\n\n"

            # Adicionar membros (incluindo bots e aplicativos)
            texto_relatorio += "👥 **Usuários**:\n"
            for member in guild.members:
                if member.bot:  # Inclui bots
                    texto_relatorio += f"🤖 Bot: {member.name} - ID: {member.id}\n"
                else:
                    texto_relatorio += f"Usuário: {member.name} - ID: {member.id}\n"

            # Enviar o relatório como mensagem separada para cada servidor
            enviar_mensagem_telegram(texto_relatorio, telegram_chat_id_relatorio)
            print(f"Relatório do servidor {guild.name} enviado para o Telegram!")

        await client.close()

    await client.start(global_token)


# Função para iniciar o monitoramento
async def iniciar_monitoramento():
    global global_token
    if not global_token:
        print("Você precisa configurar o bot antes de iniciar o monitoramento!")
        return
    print("Iniciando o monitoramento...")
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Bot conectado como {client.user}!")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        palavras_proibidas = ["palavra proibida", "exemplo", "graça"]
        mensagem_lower = message.content.lower()
        for palavra in palavras_proibidas:
            if palavra in mensagem_lower:
                # Gerar mensagem de alerta para o Telegram
                alerta = (
                    f"⚠️ Alerta de Palavra Proibida ⚠️\n"
                    f"Usuário: {message.author.name}\n"
                    f"Palavra(s) detectada(s): {palavra}\n"
                    f"Mensagem: {message.content}\n"
                    f"ID: {message.author.id}\n"  # Adiciona o ID do usuário
                    f"Canal: {message.channel.name}\n"
                    f"Servidor: {message.guild.name}\n"
                    f"Data e Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                enviar_mensagem_telegram(alerta, telegram_chat_id_alertas)

    await client.start(global_token)


async def main():
    await apresentacao()
    await exibir_menu()


if __name__ == "__main__":
    asyncio.run(main())
