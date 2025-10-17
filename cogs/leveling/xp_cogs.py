from discord.ext import commands
import discord
import re
from catalog import catalog_xp
from utils.data_manager import (
    get_user_xp, add_xp, user_xp_data, save_xp_data
)


class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.catalog = catalog_xp


    def find_xp_in_catalog(self, category: str, item_name: str) -> int:
        category_data = self.catalog.get(category)
        if not category_data:
            return 0
        
        for item in category_data:
            for key, value in item.items():
                if isinstance(value, str) and value.lower() == item_name.lower():
                    return item.get("XP", 0) 
        return 0
    
    async def check_for_rank_up(self, member, user_xp):
        xp_roles = [
            ("👑 Dominador", 12202803200),
            ("👑 Rei", 1743257600),
            ("👑 Duque", 435814400),
            ("👑 Conde", 108973600),
            ("👑 Barão", 27238400),
            ("👑 Lorde", 6809600),
            ("⚜️ Nobre", 1702400),
            ("🛡️ Cavalaria", 425600),
            ("⚔️ Oficiais", 106400),
            ("💰 Soldado de aluguel", 25600),
            ("Mestre de armas", 6400),
            ("🛠️ Armeiro", 1600),
            ("🧑‍🎓 Escudeiro", 400),
            ("🖊️ Neófito", 200)
        ]

        for role_name, required_xp in xp_roles:
            if user_xp >= required_xp:
                role = discord.utils.get(member.guild.roles, name=role_name)
                if role and role not in member.roles:
                    await member.add_roles(role)
                    await member.send(
                        f"Parabéns, {member.mention}! Você alcançou um novo nível de experiência e agora é **{role.name}**!"
                    )
                    break 

    
    @commands.command(name="xp", help="Mostra seu XP ou o de outro usuário.")
    async def xp_lookup(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_xp = get_user_xp(member.id)
        await ctx.send(f"XP de {member.mention}: {user_xp} XP")

    @commands.command(name="ranking", help="Mostra o ranking dos 10 usuários com mais XP.")
    async def ranking_cmd(self, ctx):
        ranking = sorted(user_xp_data.items(), key=lambda x: x[1], reverse=True)
        ranking_message = "**Ranking de XP**:\n"
        for i, (user_id, xp) in enumerate(ranking[:10], start=1):
            try:
                user = await self.bot.fetch_user(user_id)
                ranking_message += f"{i}. {user.name}: {xp} XP\n"
            except Exception:
                ranking_message += f"{i}. ID {user_id}: {xp} XP\n"
        await ctx.send(ranking_message)

    @commands.command(name="addxp", help="Adiciona XP a um usuário.")
    @commands.has_permissions(administrator=True)
    async def add_xp_cmd(self, ctx, member: discord.Member, xp_to_add: int, *, justificativa: str = "Sem justificativa."):
        add_xp(member.id, xp_to_add)
        
        updated_xp = get_user_xp(member.id)
        await self.check_for_rank_up(member, updated_xp)
        
        await ctx.send(
            f"🎖️ **{xp_to_add} XP** foram adicionados para o usuário {member.mention}!"
            f"\n**Motivo:** {justificativa}"
        )

    @commands.command(name="addxpcatalog", help="Adiciona XP do catálogo para um usuário.")
    @commands.has_permissions(administrator=True)
    async def dar_catalog_xp_cmd(self, ctx, member: discord.Member, category: str, item_name: str):
        xp_to_add = self.find_xp_in_catalog(category, item_name)
        
        if xp_to_add > 0:
            add_xp(member.id, xp_to_add)
            await self.check_for_rank_up(member, get_user_xp(member.id))
            await ctx.send(f"🎖️ {xp_to_add} XP foram adicionados para {member.mention} por '{category} - {item_name}'!")
        else:
            await ctx.send(f"Não foi possível encontrar XP para '{category} - {item_name}' no catálogo.")
            
    
    @commands.command(name="listarxp", help="Lista todas as categorias e itens disponíveis no Catálogo de XP.")
    async def list_xp_catalog_cmd(self, ctx):
        """Lista o catálogo de XP em um formato fácil de ler."""
        
        embed = discord.Embed(
            title="📚 Catálogo de Recompensas de XP",
            description="Use **`ty: darxp @membro \"Categoria\" \"Item\"`** para atribuir XP.",
            color=discord.Color.blue()
        )
        
        for category_name, items in catalog_xp.items():
            
            field_value = []
            
            for item in items:
                item_key = next(iter(k for k in item if k not in ['XP', 'Observações']), 'Item')
                item_name = item.get(item_key, "N/A")
                xp_value = item.get("XP", 0)
                field_value.append(line)
                
            if field_value:
                embed.add_field(
                    name=f"🔸 {category_name}",
                    value="\n".join(field_value),
                    inline=True
                )
        if not embed.fields:
            await ctx.send("O Catálogo de XP está vazio.")
        else:
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(XP(bot))
