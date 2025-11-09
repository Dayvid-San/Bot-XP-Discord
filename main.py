import os
from dotenv import load_dotenv
from discord.ext import commands
import discord
from utils.data_manager import load_xp_data, load_teams_data
import traceback


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "ty: "

COGS_TO_LOAD = [
    "cogs.leveling.xp_cogs",
    "cogs.teams.teams_cogs",
    "cogs.media.download_cogs",
    "cogs.knowledge.knowledge_cogs",
    "cogs.scheduler.scheduler_cogs",
    "cogs.music.music_cogs",
]

class AthenaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        
        # O bot de comandos requer o prefixo
        super().__init__(command_prefix=PREFIX, intents=intents)

    async def setup_hook(self):
        # 1. Carrega os dados persistentes ANTES de carregar os cogs
        load_xp_data()
        load_teams_data()
        print("Dados de XP e Equipes carregados.")
        
        # 2. Carrega os Cogs
        for extension in COGS_TO_LOAD:
            try:
                await self.load_extension(extension)
                print(f"Carregado: {extension}")
            except Exception as e:
                # MUDANÇA AQUI: Imprima o erro com rastreio de pilha completo
                print(f"---------- ERRO AO CARREGAR COG: {extension} ----------")
                traceback.print_exc() 
                print("----------------------------------------------------------")
        
        # 3. Sincroniza comandos de barra (se for usar)
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logado como {self.user} (ID: {self.user.id})')

    # Você pode manter o on_member_join aqui ou movê-lo para um Cog de Core/Events
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        if guild.system_channel:
            await guild.system_channel.send(f'Bem-vindo {member.mention} ao {guild.name}!')

if __name__ == "__main__":
    bot = AthenaBot()
    bot.run(TOKEN)
