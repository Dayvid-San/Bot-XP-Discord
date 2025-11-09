# cogs/music/music_cogs.py

import discord
from discord.ext import commands
import yt_dlp
import asyncio

# Configurações para extração de áudio do yt-dlp
# O 'before_options' é crucial para garantir que a transmissão seja contínua e silenciosa
YTDL_OPTIONS = {
    # ⬇️ CHAVE CRUCIAL: 'bestaudio[ext=webm]/bestaudio' prioriza o formato OPUS (WebM), 
    # que é o codec nativo do Discord, oferecendo a melhor qualidade e menor latência.
    'format': 'bestaudio[ext=webm]/bestaudio', 
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# Cria um extrator de áudio
ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

# Classe para o recurso de áudio
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        
        # O loop 'run_in_executor' permite que a operação síncrona do yt-dlp 
        # não bloqueie o loop assíncrono do bot.
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)

        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -acodec libopus -b:a 128k
        }

        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ----------------------------------------------------------------------
    # COMANDOS DE VOZ
    # ----------------------------------------------------------------------

    @commands.command(name='join', aliases=['entrar'], help='Faz o bot entrar no seu canal de voz.')
    async def join(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("❌ Você precisa estar em um canal de voz para me chamar.")

        channel = ctx.author.voice.channel
        
        if ctx.voice_client is not None:
            # Se já estiver em um canal, move
            return await ctx.voice_client.move_to(channel)

        await channel.connect()
        await ctx.send(f"Olá! Entrei no {channel.name}")

    @commands.command(name='leave', aliases=['sair', 'parar'], help='Faz o bot sair do canal de voz.')
    async def leave(self, ctx):
        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Desconectado do canal de voz.")
        else:
            await ctx.send("❌ Não estou em um canal de voz.")

    @commands.command(name='play', aliases=['tocar'], help='Toca música a partir de um link do YouTube.')
    async def play(self, ctx, url: str):
        if not ctx.voice_client:
            # Garante que o bot esteja no canal
            await ctx.invoke(self.join)

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        try:
            # Usa a classe YTDLSource para extrair o stream
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            
            # Toca o stream
            ctx.voice_client.play(player, after=lambda e: print(f'Erro ao tocar: {e}') if e else None)
            
            embed = discord.Embed(
                title="▶️ Tocando Agora",
                description=f"**[{player.title}]({url})**",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Requisitado por {ctx.author.display_name}")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro ao processar o link. Certifique-se de que é uma URL de vídeo válida.\nDetalhes: `{e}`")

    # ----------------------------------------------------------------------
    # TRATAMENTO DE ERROS (Opcional, mas recomendado)
    # ----------------------------------------------------------------------

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("❌ Você não está em um canal de voz.")
                raise commands.CommandError("Autor não está conectado em um canal de voz.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


async def setup(bot):
    await bot.add_cog(Music(bot))