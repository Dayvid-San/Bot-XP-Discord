import discord
from discord.ext import commands
# Importa o gerenciador de dados
from utils.data_manager import load_knowledge_data 

class Knowledge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # --- CARREGAMENTO DOS DADOS NO INÍCIO ---
        self.cargos_relevantes, self.knowledge_base = load_knowledge_data()
        
        # Cria um mapeamento reverso para obter o nome do cargo a partir do nível
        self.level_to_role = {v: k for k, v in self.cargos_relevantes.items()}
        self.knowledge_keys = list(self.knowledge_base.keys())

    def get_user_access_level(self, member: discord.Member) -> int:
        """Calcula o nível de acesso mais alto do membro com base em seus cargos."""
        max_level = 0
        
        for role in member.roles:
            # Usa o dicionário carregado
            level = self.cargos_relevantes.get(role.name, 0)
            if level > max_level:
                max_level = level
        return max_level

    # ----------------------------------------------------------------------
    # COMANDOS (Quase idêntico, mas usando self.knowledge_base)
    # ----------------------------------------------------------------------

    @commands.command(
        name="oraculo", 
        aliases=['conhecimento', 'info'],
        help="Consulta informações da empresa. Use 'ty: oraculo lista' para ver as opções."
    )
    async def oracle_cmd(self, ctx, key: str = None):
        user_level = self.get_user_access_level(ctx.author)
        
        # --- Caso 1: Usuário pede a lista de informações acessíveis ---
        if key is None or key.lower() == "lista":
            accessible_keys = []
            
            # Filtra o dicionário carregado
            for k, data in self.knowledge_base.items():
                if user_level >= data["acesso_min"]:
                    accessible_keys.append(f"• `{k}` ({self.level_to_role.get(data['acesso_min'], 'N/A')})")

            # ... (Resto da lógica de listagem do Embed)
            
            embed = discord.Embed(
                title="🔮 Catálogo de Conhecimento Empresarial",
                description=f"Seu nível de acesso atual: **{self.level_to_role.get(user_level, 'Recruta')}** (Nível {user_level})",
                color=discord.Color.dark_purple()
            )
            if accessible_keys:
                embed.add_field(
                    name="Informações Acessíveis (Use: ty: oraculo <chave>)",
                    value="\n".join(accessible_keys),
                    inline=False
                )
            else:
                embed.add_field(name="Acesso Negado", value="Você não tem permissão para acessar nenhuma informação no catálogo.", inline=False)
            
            await ctx.send(embed=embed)
            return

        # --- Caso 2: Usuário pede uma informação específica ---
        key = key.lower()
        # Busca a informação no dicionário carregado
        data = self.knowledge_base.get(key)
        
        if not data:
            await ctx.send(f"❌ A chave de conhecimento `{key}` não foi encontrada no catálogo. Use `ty: oraculo lista`.")
            return

        required_level = data["acesso_min"]
        
        # 3. Verificação de Permissão (sem alterações)
        if user_level < required_level:
            required_role = self.level_to_role.get(required_level, 'Cargo Desconhecido')
            
            embed = discord.Embed(
                title=f"🔒 Acesso Negado: {data.get('titulo', 'Informação Confidencial')}",
                description=f"Seu cargo mais alto (**{self.level_to_role.get(user_level, 'Recruta')}**) não possui o nível de autorização necessário.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Nível mínimo exigido: {required_role} (Nível {required_level})")
            await ctx.send(embed=embed)
            return

        # 4. Acesso Concedido (sem alterações)
        embed = discord.Embed(
            title=f"✅ {data['titulo']}",
            description=data["info"],
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Acesso concedido (Nível {user_level}) | Requer: {self.level_to_role.get(required_level)}")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Knowledge(bot))