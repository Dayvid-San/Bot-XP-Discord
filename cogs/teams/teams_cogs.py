from discord.ext import commands
import discord
from utils.data_manager import (
    team_points_data, 
    create_team, 
    add_member_to_team, 
    add_team_points, 
    get_user_team
)


class Teams(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addteam", help="Cria uma nova equipe (Admin). Uso: ty: addteam <nome>")
    @commands.has_permissions(administrator=True)
    async def create_team_cmd(self, ctx, *, team_name: str):
        
        if create_team(team_name):
            await ctx.send(f"✅ Equipe **'{team_name}'** criada com sucesso!")
        else:
            await ctx.send(f"❌ A equipe **'{team_name}'** já existe.")

    @commands.command(name="addmember", help="Adiciona um membro a uma equipe. Uso: ty: addmember <nome> @membro")
    @commands.has_permissions(administrator=True)
    async def add_member_to_team_cmd(self, ctx, team_name: str, member: discord.Member):
        """Adiciona um usuário a uma equipe específica."""
        
        if add_member_to_team(team_name, member.id):
            await ctx.send(f"👥 {member.mention} foi adicionado à equipe **{team_name}**!")
        else:
            await ctx.send(
                f"❌ Erro ao adicionar {member.mention} à equipe **{team_name}**. "
                "Verifique se a equipe existe ou se o usuário já é membro."
            )

    # Note: O help text ainda usa "darpontosequipe", mas o nome do comando é "addpontosequipe"
    @commands.command(name="addxpteam", help="Adiciona pontos a uma equipe. Uso: ty: addxpteam <nome> <quantidade>")
    @commands.has_permissions(administrator=True)
    async def add_team_points_cmd(self, ctx, team_name: str, points_to_add: int):
        
        if team_name in team_points_data:
            add_team_points(team_name, points_to_add)
            await ctx.send(f"⚔️ **{points_to_add} pontos** foram adicionados à equipe **{team_name}**!")
        else:
            await ctx.send(f"❌ A equipe **{team_name}** não foi encontrada.")


    @commands.command(name="myteam", help="Mostra sua equipe e os pontos dela.")
    async def my_team_cmd(self, ctx):
        
        user_team = get_user_team(ctx.author.id)
        
        if user_team:
            team_points = team_points_data[user_team]["points"]
            await ctx.send(f"Você pertence à equipe **{user_team}** com **{team_points}** pontos.")
        else:
            await ctx.send("Você não pertence a nenhuma equipe ainda.")

    @commands.command(name="rankingteams", help="Mostra o ranking das equipes.")
    async def team_ranking_cmd(self, ctx):
        
        ranking = sorted(
            team_points_data.items(), 
            key=lambda item: item[1]["points"], 
            reverse=True
        )
        
        if not ranking:
            await ctx.send("Nenhuma equipe foi registrada ainda.")
            return
        
        ranking_message = "**🏆 Ranking de Equipes**:\n"
        for i, (team_name, data) in enumerate(ranking[:10], start=1):
            ranking_message += f"{i}. **{team_name}**: {data['points']} pontos\n"
            
        await ctx.send(ranking_message)


async def setup(bot):
    await bot.add_cog(Teams(bot))
