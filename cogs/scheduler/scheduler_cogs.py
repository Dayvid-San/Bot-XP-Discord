import discord
from discord.ext import commands
import re # Usado para validar menções de canais ou URLs

# Se o seu bot tiver o prefixo 'ty:'
# Exemplo de uso:
# ty: agendar "Reunião de Planejamento" amanhã 14:30 1h30m meet https://meet.google.com/abc-xyz-def @Membro1 @Membro2

class MeetingScheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="agendar_reuniao",
        aliases=['agendar', 'reuniao'],
        help="Agenda uma reunião no seu calendário. O local pode ser 'meet' (com link) ou 'discord' (com canal). Ex: ty: agendar 'Reunião de Planejamento' amanhã 14:30 1h30m meet https://meet.google.com/abc-xyz-def @Membro1 @Membro2"
    )
    async def schedule_meeting(self, 
        ctx, 
        titulo: str, 
        data: str, 
        hora: str, 
        duracao: str, 
        local_tipo: str, 
        local_valor: str, 
        participantes: commands.Greedy[discord.Member] = None
    ):
        """
        Agenda uma reunião com título, data, hora, duração, tipo de local e participantes.
        
        Args:
            titulo (str): O título da reunião (coloque entre aspas).
            data (str): A data (ex: "amanhã", "próxima sexta", "25/12").
            hora (str): A hora (ex: "10:00", "4pm").
            duracao (str): A duração (ex: "1h30m", "30m"). O formato deve ser como "1h30m".
            local_tipo (str): O tipo de local ("meet" ou "discord").
            local_valor (str): O link do Meet ou a menção do canal Discord (#canal-de-voz).
            participantes (Greedy[discord.Member]): Menções de membros do Discord.
        """
        
        # --- 1. Processamento e Validação do Local ---
        
        location = ""
        description = ""
        local_tipo_low = local_tipo.lower()
        
        if local_tipo_low == "meet":
            if not re.match(r'https?://[^\s/$.?#].[^\s]*$', local_valor):
                return await ctx.send("❌ Erro: O valor do local 'meet' deve ser um link (URL) válido.")
            location = local_valor
            description = f"Link da Reunião (Meet): {local_valor}"
            
        elif local_tipo_low == "discord":
            # Tenta converter a menção do canal em um link interno ou nome
            if re.match(r'<#\d+>', local_valor):
                channel_id = local_valor.strip('<#>')
                channel = self.bot.get_channel(int(channel_id))
                
                if channel and isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                    # O campo 'location' do calendário é otimizado para endereços. 
                    # Usamos o nome do canal e colocamos o link na descrição.
                    location = f"Discord | #{channel.name}"
                    description = f"Reunião agendada no canal Discord: {local_valor}"
                else:
                    return await ctx.send("❌ Erro: Mencione um canal de texto ou voz válido do Discord (ex: #geral).")
            else:
                 return await ctx.send("❌ Erro: O valor do local 'discord' deve ser a menção de um canal (#canal).")

        else:
            return await ctx.send("❌ Tipo de local inválido. Use 'meet' ou 'discord'.")

        # --- 2. Processamento dos Participantes ---

        attendee_list = []
        if participantes:
            # A API de calendário aceita nomes (strings), mas o ideal são e-mails.
            # Usaremos o display_name do Discord para referência.
            attendee_list = [member.display_name for member in participantes]
            description += "\n\n**Participantes (Discord):** " + ", ".join(attendee_list)

        # --- 3. Chamada da API de Calendário ---
        
        # Chamamos a ferramenta de calendário
        # As APIs farão a conversão de data/hora (ex: "amanhã", "14:30")
        try:
            await generic_calendar.create_calendar_event(
                title=titulo,
                start_date=data,
                start_time_of_day=hora,
                duration=duracao,
                location=location,
                description=description,
                attendees=attendee_list,
                start_am_pm_or_unknown="UNKNOWN" # Deixa a API inferir AM/PM
            )
            # O retorno da API já inclui a confirmação e o evento
            
        except Exception as e:
            # Em caso de falha na API (ex: data/hora inválida), a API geralmente pede o dado
            # Caso contrário, retorne uma mensagem de erro genérica.
            await ctx.send(f"❌ Ocorreu um erro ao agendar a reunião. Verifique se a data, hora e duração estão no formato correto (ex: `1h30m`). Detalhes: {e}")


async def setup(bot):
    await bot.add_cog(MeetingScheduler(bot))