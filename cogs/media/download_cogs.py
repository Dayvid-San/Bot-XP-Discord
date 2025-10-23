import yt_dlp
import os
import discord
from discord.ext import commands
import asyncio
import traceback
import time

TEMP_DIR = "temp_downloads"

class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(TEMP_DIR, exist_ok=True)
        self._last_update = {}  # Para evitar flood no progresso

    def get_safe_filename(self, title):
        """Remove caracteres inválidos do título."""
        return "".join(c for c in title if c.isalnum() or c in (' ', '_', '-', '()')).rstrip()

    async def run_download(self, ctx, url: str, is_audio: bool):
        if 'youtu.be' not in url and 'youtube.com' not in url:
            await ctx.send("Por razões de segurança, apenas URLs do YouTube são permitidas.")
            return

        status_message = await ctx.send(f"Iniciando download de **{'áudio' if is_audio else 'vídeo'}**...")
        loop = self.bot.loop
        final_filepath = None
        download_id = f"{ctx.author.id}_{int(time.time())}"

        ydl_opts = {
            'quiet': False,  # Para debug, permite logs
            'no_warnings': True,
            'noplaylist': True,
            'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: self.progress_hook(d, status_message, loop, download_id)],
            'logger': MyLogger(),  # Logger personalizado para debug
        }

        if is_audio:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [
                    {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                    {'key': 'FFmpegMetadata'},
                ],
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })

        try:
            info = await loop.run_in_executor(
                None,
                lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True)
            )

            # Tenta obter o caminho do arquivo
            final_filepath = info.get('filepath')
            ext = 'mp3' if is_audio else 'mp4'

            # Fallback: usar o título do vídeo para prever o nome do arquivo
            if not final_filepath or not os.path.exists(final_filepath):
                title = info.get('title', 'unknown')
                safe_title = self.get_safe_filename(title)
                final_filepath = os.path.join(TEMP_DIR, f"{safe_title}.{ext}")

            # Último fallback: verifica arquivos recentes no diretório
            if not os.path.exists(final_filepath):
                files = [f for f in os.listdir(TEMP_DIR) if f.endswith(f".{ext}")]
                if files:
                    # Pega o arquivo mais recente
                    final_filepath = os.path.join(TEMP_DIR, max(
                        files,
                        key=lambda x: os.path.getctime(os.path.join(TEMP_DIR, x))
                    ))
                    print(f"[DEBUG] Fallback usado: {final_filepath}")
                else:
                    raise FileNotFoundError(f"Nenhum arquivo .{ext} encontrado em {TEMP_DIR}")

            filename = os.path.basename(final_filepath)
            file_size = os.path.getsize(final_filepath)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            limit_mb = round(ctx.guild.filesize_limit / (1024 * 1024), 2)

            if file_size > ctx.guild.filesize_limit:
                await status_message.edit(
                    content=f"Arquivo `{filename}` tem **{file_size_mb} MB** (limite: **{limit_mb} MB**)."
                )
                return

            await status_message.edit(content=f"Enviando `{filename}` ({file_size_mb} MB)...")
            await ctx.send(file=discord.File(final_filepath))
            await status_message.edit(content="Aqui está o seu arquivo. Faça bom proveito :)")

        except Exception as e:
            error_msg = f"Ocorreu um erro: `{str(e)}`"
            try:
                await status_message.edit(content=error_msg)
            except:
                await ctx.send(error_msg)
            print(f"[ERRO] {traceback.format_exc()}")
        finally:
            if final_filepath and os.path.exists(final_filepath):
                try:
                    os.remove(final_filepath)
                    print(f"[DEBUG] Arquivo removido: {final_filepath}")
                except Exception as e:
                    print(f"[AVISO] Falha ao remover: {e}")
            self._last_update.pop(download_id, None)

    def progress_hook(self, d, message, loop, download_id):
        now = time.time()
        last = self._last_update.get(download_id, 0)

        if now - last < 1.0:  # Evita flood
            return
        self._last_update[download_id] = now

        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', '?/s').strip()
            eta = d.get('_eta_str', '?').strip()
            content = f"Baixando... **{percent}** | **{speed}** | ETA: **{eta}**"
            loop.call_soon_threadsafe(
                lambda: asyncio.create_task(message.edit(content=content))
            )
        elif d['status'] == 'finished':
            loop.call_soon_threadsafe(
                lambda: asyncio.create_task(message.edit(content="Download concluído! Processando..."))
            )

    @commands.command(name="dsongs", aliases=['dmp3'], help="Baixa o áudio em MP3.")
    async def download_audio_cmd(self, ctx, url: str):
        await self.run_download(ctx, url, is_audio=True)

    @commands.command(name="dvideos", aliases=['dv'], help="Baixa o vídeo em MP4.")
    async def download_video_cmd(self, ctx, url: str):
        await self.run_download(ctx, url, is_audio=False)


class MyLogger:
    def debug(self, msg):
        print(f"[yt_dlp DEBUG] {msg}")

    def warning(self, msg):
        print(f"[yt_dlp WARNING] {msg}")

    def error(self, msg):
        print(f"[yt_dlp ERROR] {msg}")


async def setup(bot):
    await bot.add_cog(Media(bot))
