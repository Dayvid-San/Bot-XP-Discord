from discord.ext import commands, tasks
import discord
from utils.data_manager import *


class Agenda(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.event_checker.start() 

    def cog_unload(self):
        self.event_checker.cancel()

    @tasks.loop(minutes=1)
    async def event_checker(self):
        # 1. Carregar a lista de eventos (agenda_data.json)
        # 2. Obter a hora atual
        # 3. Iterar sobre todos os eventos:
        #    Se (event_time - current_time) <= 10 minutos:
        #        - Enviar o lembrete para o canal/usuário
        #        - Marcar o evento como 'lembrado' ou removê-lo
        pass

    @event_checker.before_loop
    async def before_event_checker(self):
        await self.bot.wait_until_ready() 

    @commands.command(name="createagenda", help="Agende um novo evento. Uso: ty: createagenda [DD/MM/AAAA HH:MM] [Título]")
    @commands.has_permissions(manage_events=True)
    async def create_event_cmd(self, ctx, datetime_str: str, *, title: str):
        
        # 1. Tratar a data e hora (Requer a biblioteca 'datetime' para parsear)
        # 2. Salvar o evento em agenda_data.json (com ID, timestamp, título, etc.)
        
        # await ctx.send(f"✅ Evento **'{title}'** agendado para {datetime_str}!")
        await ctx.send("O comando de criação de eventos na agenda ainda está indisponível.")
        
        
async def setup(bot):
    await bot.add_cog(Agenda(bot))
