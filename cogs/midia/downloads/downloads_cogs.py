import yt_dlp
import os
import discord
from discord.ext import commands
import asyncio
import traceback


TEMP_DIR = "temp_downloads"

class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(TEMP_DIR, exist_ok=True)

    def get_output_path(self, title, ext):
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).rstrip()
        return os.path.join(TEMP_DIR, f"{safe_title}.{ext}")

    async def run_download(self, ctx, url: str, is_audio: bool):
        if 'youtu.be' not in url and 'youtube.com' not in url:
            await ctx.send("🚫 Por razões de segurança, o download é limitado a URLs do YouTube.")
            return

        message = await ctx.send(f"⏳ Iniciando download de **{'áudio' if is_audio else 'vídeo'}**... Isso pode demorar.")
        
        loop = asyncio.get_event_loop()
        
        temp_file_base = self.get_output_path("temp_file", "%(ext)s")
        
        ydl_opts = {
            'outtmpl': temp_file_base,
            'quiet': True,
            'noplaylist': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]' if not is_audio else 'bestaudio/best',
            'progress_hooks': [lambda d: self.capture_info(d, ctx)], 
        }

        if is_audio:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }, {'key': 'FFmpegMetadata'}]
            ydl_opts['outtmpl'] = self.get_output_path("%(title)s", "mp3") 

        try:
            info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(url, download=True))
            
            final_ext = 'mp3' if is_audio else 'mp4'
            final_title = info.get('title', 'arquivo_desconhecido')
            final_filepath = self.get_output_path(final_title, final_ext)
            

            file_size = os.path.getsize(final_filepath)
            
            if file_size > ctx.guild.filesize_limit:
                await message.edit(content=f"⚠️ O arquivo `{final_title}.{final_ext}` tem {round(file_size / (1024*1024), 2)}MB, excedendo o limite de upload do Discord ({round(ctx.guild.filesize_limit / (1024*1024), 2)}MB).")
                return

            await ctx.send(
                f"🎉 Download de **{final_title}** completo! Enviando...", 
                file=discord.File(final_filepath)
            )

        except Exception as e:
            error_message = f"❌ Ocorreu um erro ao processar a URL: {e}"
            await ctx.send(error_message)
            traceback.print_exc()

        finally:
            try:
                os.remove(final_filepath)
            except:
                pass

    def capture_info(self, d, ctx):
        if d['status'] == 'finished':
            pass



    @commands.command(name="downloadmusica", aliases=['dmp3'], help="Baixa o áudio (MP3) de uma URL (principalmente YouTube) e envia.")
    async def download_audio_cmd(self, ctx, url: str):
        await self.run_download(ctx, url, is_audio=True)

    @commands.command(name="downloadvideo", aliases=['dv'], help="Baixa o vídeo (MP4) de uma URL (principalmente YouTube) e envia.")
    async def download_video_cmd(self, ctx, url: str):
        await self.run_download(ctx, url, is_audio=False)


async def setup(bot):
    await bot.add_cog(Media(bot))