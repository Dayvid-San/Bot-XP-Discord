import discord
from discord import Client, Intents
from discord.member import Member
from discord.message import Message
from dotenv import load_dotenv
from catalog import catalog_xp
import os
import json
import re

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
botName = 'Athena'
XP_DATA_FILE = "xp_data.json"
TEAMS_DATA_FILE = "teams_data.json" # Corrigido: Adicionado aqui!

# Dicionário para armazenar o XP dos usuários em memória
user_xp_data = {}
team_points_data = {} # Corrigido: Adicionado aqui!

def load_xp_data():
    """Carrega os dados de XP do arquivo JSON para o dicionário."""
    global user_xp_data
    try:
        with open(XP_DATA_FILE, "r") as file:
            data = json.load(file)
            user_xp_data = {int(user_id): xp for user_id, xp in data.items()}
    except FileNotFoundError:
        user_xp_data = {}

def save_xp_data():
    """Salva os dados de XP no arquivo JSON."""
    with open(XP_DATA_FILE, "w") as file:
        json.dump(user_xp_data, file)

def get_user_xp(user_id: int) -> int:
    """Retorna o XP atual do usuário ou 0 se ainda não existir."""
    return user_xp_data.get(user_id, 0)

def add_xp(user_id: int, xp: int):
    """Adiciona XP ao usuário e atualiza o arquivo JSON."""
    if user_id in user_xp_data:
        user_xp_data[user_id] += xp
    else:
        user_xp_data[user_id] = xp
    save_xp_data()

def load_teams_data():
    """Carrega os dados de pontos das equipes do arquivo JSON para o dicionário."""
    global team_points_data
    try:
        with open(TEAMS_DATA_FILE, "r") as file:
            team_points_data = json.load(file)
    except FileNotFoundError:
        team_points_data = {}

def save_teams_data():
    """Salva os dados de pontos das equipes no arquivo JSON."""
    with open(TEAMS_DATA_FILE, "w") as file:
        json.dump(team_points_data, file, indent=4) 

def add_team_points(team_name: str, points: int):
    """Adiciona pontos a uma equipe e atualiza o arquivo JSON."""
    if team_name in team_points_data:
        team_points_data[team_name]["points"] += points
    else:
        team_points_data[team_name] = {"points": points, "members": []}
    save_teams_data()

def create_team(team_name: str):
    """Cria uma nova equipe."""
    if team_name not in team_points_data:
        team_points_data[team_name] = {"points": 0, "members": []}
        save_teams_data()
        return True
    return False

def add_member_to_team(team_name: str, member_id: int):
    """Adiciona um membro a uma equipe."""
    if team_name in team_points_data:
        if member_id not in team_points_data[team_name]["members"]:
            team_points_data[team_name]["members"].append(member_id)
            save_teams_data()
            return True
    return False

def get_user_team(user_id: int) -> str | None:
    """Retorna o nome da equipe de um usuário, ou None se não pertencer a nenhuma."""
    for team_name, data in team_points_data.items():
        if user_id in data["members"]:
            return team_name
    return None
    
class ExperienceManager:
    def __init__(self, client: Client):
        self.client = client
        self.catalog = catalog_xp
        # Adicionado: Definição dos comandos aqui
        self.commands = {
            "Comandos Gerais": [
                {"comando": "ty: xp", "desc": "Mostra seu XP."},
                {"comando": "ty: xp @usuario", "desc": "Mostra o XP de outro usuário."},
                {"comando": "ty: ranking", "desc": "Mostra o ranking dos 10 usuários com mais XP."},
                {"comando": "ty: guardião", "desc": "Mensagem sobre o bot."},
                {"comando": "ty: ajuda", "desc": "Mostra esta lista de comandos."},
            ],
            "Comandos de Equipe": [
                {"comando": "ty: minhaequipe", "desc": "Mostra a sua equipe e os pontos."},
                {"comando": "ty: rankingequipes", "desc": "Mostra o ranking das equipes."},
            ],
            "Comandos de Admin (apenas para administradores)": [
                {"comando": "ty: addxp @usuario <quantidade>", "desc": "Adiciona XP a um usuário."},
                {"comando": "ty: listarxp", "desc": "Lista todas as categorias e XP do catálogo."},
                {"comando": "ty: darxp @usuario \"Categoria\" \"Item\"", "desc": "Adiciona XP do catálogo para um usuário."},
                {"comando": "ty: criarequipe <nome>", "desc": "Cria uma nova equipe."},
                {"comando": "ty: adicionarmembro <nome> @membro", "desc": "Adiciona um membro a uma equipe."},
                {"comando": "ty: darpontosequipe <nome> <quantidade>", "desc": "Adiciona pontos a uma equipe."},
            ]
        }

    def find_xp_in_catalog(self, category: str, item_name: str) -> int:
        """Procura o XP correspondente a uma categoria e item no catálogo."""
        category_data = self.catalog.get(category)
        if not category_data:
            return 0
        
        for item in category_data:
            for key, value in item.items():
                if isinstance(value, str) and value.lower() == item_name.lower():
                    return item.get("XP", 0) 
        return 0

    async def xp_command(self, message: Message):
        if message.author == self.client.user:
            return

        user_xp = get_user_xp(message.author.id)

        if message.content.lower() == "ty: xp":
            await message.channel.send(f"XP do usuário {message.author.mention}: {user_xp} XP")
            return

        if message.content.lower() == "ty: guardião":
            await message.channel.send(
                f"Olá, {message.author.mention}! Eu sou {botName}, a coruja sábia que se tornou a mascote orgulhosa desta incrível comunidade.\n\n"
                "Eu represento o compromisso da TYTO.code com a excelência em administração, suporte aos desenvolvedores e organização de projetos. "
                "Se você tiver ideias para aprimorar a minha atuação ou sugestões para a TYTO.code, ficarei encantada em ouvir."
            )
            return

        if message.content.lower().startswith("ty: xp"):
            if message.mentions:
                mentioned_user = message.mentions[0]
                mentioned_xp = get_user_xp(mentioned_user.id)
                await message.channel.send(f"XP de {mentioned_user.mention}: {mentioned_xp}")
            else:
                await message.channel.send("Usuário não catalogado!")
            return

        if message.content.lower().startswith("ty: addxp"):
            await self.add_xp_command(message)

    async def add_xp_command(self, message: Message):
        # Verifica se o autor da mensagem é um bot
        if message.author.bot:
            return

        # Verifica se o usuário tem permissões de administrador
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Você não tem permissão para usar este comando.")
            return

        # Garante que há uma menção na mensagem
        if not message.mentions:
            await message.channel.send("Por favor, mencione um usuário. Use: `ty: addxp @usuario [quantidade] [justificativa]`.")
            return

        try:
            # Obtém o objeto do usuário mencionado
            mentioned_user = message.mentions[0]
            
            # Remove o comando e a menção do conteúdo da mensagem
            # Ex: "ty: addxp <@!123...> 10 teste" -> "10 teste"
            content_without_mention = message.content.lower().replace(f"<@!{mentioned_user.id}>", "").replace(f"<@{mentioned_user.id}>", "").replace("ty: addxp", "").strip()
            
            # Divide o restante da mensagem
            parts = content_without_mention.split(' ', 1)
            
            # A primeira parte é o valor de XP, a segunda (se existir) é a justificativa
            xp_to_add = int(parts[0])
            justificativa = parts[1] if len(parts) > 1 else "Sem justificativa."

            # Adiciona o XP e envia a confirmação
            add_xp(mentioned_user.id, xp_to_add)
            
            await message.channel.send(
                f"🎉 **{xp_to_add} XP** foram adicionados para o usuário {mentioned_user.mention}!"
                f"\n**Motivo:** {justificativa}"
            )
            
        except (IndexError, ValueError):
            await message.channel.send("Formato inválido. Use: `ty: addxp @usuario [quantidade] [justificativa]`.")


            
    async def add_catalog_xp_command(self, message: Message):
        if message.author.bot:
            return
        
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Você não tem permissão para usar este comando.")
            return
            
        try:
            mentioned_user = message.mentions[0]
            command_text = message.content.lower().replace("ty: darxp", "").replace(mentioned_user.mention.lower(), "").strip()
            
            quoted_strings = re.findall(r'"([^"]*)"', command_text)

            if len(quoted_strings) != 2:
                await message.channel.send("Formato inválido. Use: `ty: darxp @usuario \"Categoria\" \"Item\"`")
                return
            
            category = quoted_strings[0]
            item_name = quoted_strings[1]

            xp_to_add = self.find_xp_in_catalog(category, item_name)
            
            if xp_to_add > 0:
                add_xp(mentioned_user.id, xp_to_add)
                await message.channel.send(
                    f"🏆 {xp_to_add} XP foram adicionados para o usuário {mentioned_user.mention} por '{category} - {item_name}'!"
                )
            else:
                await message.channel.send(
                    f"Não foi possível encontrar XP para '{category} - {item_name}' no catálogo."
                )

        except (IndexError, ValueError):
            await message.channel.send("Formato inválido. Use: `ty: darxp @usuario \"Categoria\" \"Item\"`")

    async def ranking_command(self, message: Message):
        if message.author == self.client.user:
            return

        if message.content.lower() == "ty: ranking":
            ranking = sorted(user_xp_data.items(), key=lambda x: x[1], reverse=True)
            ranking_message = "**Ranking de XP**:\n"
            for i, (user_id, xp) in enumerate(ranking[:10], start=1):
                try:
                    user = await self.client.fetch_user(user_id)
                    ranking_message += f"{i}. {user.name}: {xp} XP\n"
                except Exception:
                    ranking_message += f"{i}. ID {user_id}: {xp} XP\n"
            await message.channel.send(ranking_message)

    async def ranking_hierarchy(self, message: Message):
        if isinstance(message, discord.Message):
            if message.author.bot:
                return
        else:
            print("Mensagem não é do tipo esperado:", type(message))

        user_xp = get_user_xp(message.author.id)
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
            ("Neófito", 200)
        ]
        
        for role_name, required_xp in xp_roles:
            if user_xp >= required_xp:
                role = discord.utils.get(message.guild.roles, name=role_name)
                if role and role not in message.author.roles:
                    await message.author.add_roles(role)
                    await message.channel.send(
                        f"Parabéns, {message.author.mention}! Você ganhou o cargo de {role.name}!"
                    )

    async def team_commands(self, message: Message):
        if message.author.bot:
            return

        if message.content.lower().startswith("ty: criarequipe"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send("Você não tem permissão para criar equipes.")
                return
            
            try:
                team_name = " ".join(message.content.split()[2:])
                if create_team(team_name):
                    await message.channel.send(f"Equipe '{team_name}' criada com sucesso!")
                else:
                    await message.channel.send(f"A equipe '{team_name}' já existe.")
            except IndexError:
                await message.channel.send("Use o comando assim: `ty: criarequipe [nome da equipe]`.")
            return

        if message.content.lower().startswith("ty: adicionarmembro"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send("Você não tem permissão para adicionar membros a equipes.")
                return
            
            try:
                parts = message.content.split()
                team_name = " ".join(parts[2:-1])
                mentioned_user = message.mentions[0]

                if add_member_to_team(team_name, mentioned_user.id):
                    await message.channel.send(f"{mentioned_user.mention} foi adicionado à equipe '{team_name}'!")
                else:
                    await message.channel.send(f"Erro ao adicionar {mentioned_user.mention} à equipe '{team_name}'. Verifique se a equipe existe ou se o usuário já é membro.")
            except (IndexError, ValueError):
                await message.channel.send("Use o comando assim: `ty: adicionarmembro [nome da equipe] @membro`.")
            return
            
        if message.content.lower().startswith("ty: darpontosequipe"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send("Você não tem permissão para dar pontos a equipes.")
                return
            
            try:
                parts = message.content.split()
                points_to_add = int(parts[-1])
                team_name = " ".join(parts[2:-1]) 

                if team_name in team_points_data:
                    add_team_points(team_name, points_to_add)
                    await message.channel.send(f"{points_to_add} pontos foram adicionados à equipe '{team_name}'!")
                else:
                    await message.channel.send(f"A equipe '{team_name}' não foi encontrada.")
            except (IndexError, ValueError):
                await message.channel.send("Use o comando assim: `ty: darpontosequipe [nome da equipe] [quantidade]`.")
            return

        if message.content.lower() == "ty: rankingequipes":
            ranking = sorted(team_points_data.items(), key=lambda item: item[1]["points"], reverse=True)
            if not ranking:
                await message.channel.send("Nenhuma equipe foi registrada ainda.")
                return
            
            ranking_message = "**Ranking de Equipes**:\n"
            for i, (team_name, data) in enumerate(ranking[:10], start=1):
                ranking_message += f"{i}. {team_name}: {data['points']} pontos\n"
            await message.channel.send(ranking_message)
            return

        if message.content.lower() == "ty: minhaequipe":
            user_team = get_user_team(message.author.id)
            if user_team:
                team_points = team_points_data[user_team]["points"]
                await message.channel.send(f"Você pertence à equipe **{user_team}** com {team_points} pontos.")
            else:
                await message.channel.send("Você não pertence a nenhuma equipe ainda.")
            return

    async def list_catalog_command(self, message: discord.Message):
        if message.author.bot:
            return

        if message.content.lower() == "ty: listarxp":
            catalog_message = "**Catálogo de XP**\n\n"
            
            for category, items in self.catalog.items():
                catalog_message += f"**{category}**\n"
                for item in items:
                    item_name = ""
                    for key, value in item.items():
                        if key != "XP" and key != "Observações":
                            item_name = f"{key}: {value}"
                            break
                    
                    xp_value = item.get("XP", "N/A")
                    catalog_message += f"`{item_name}` - {xp_value} XP\n"
                
                catalog_message += "\n"
            
            if len(catalog_message) > 2000:
                chunks = [catalog_message[i:i + 2000] for i in range(0, len(catalog_message), 2000)]
                for chunk in chunks:
                    await message.channel.send(chunk)
            else:
                await message.channel.send(catalog_message)


    async def help_command(self, message: Message):
        if message.author.bot:
            return

        if message.content.lower() == "ty: ajuda":
            help_message = "**Lista de Comandos de " + botName + "**\n\n"
            for category, commands in self.commands.items():
                help_message += f"**{category}**\n"
                for cmd in commands:
                    help_message += f"`{cmd['comando']}` - {cmd['desc']}\n"
                help_message += "\n" 

            await message.channel.send(help_message)



class Minerva(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.experience = ExperienceManager(self)
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        load_xp_data()
        load_teams_data()

    async def on_member_join(self, member: Member):
        guild = member.guild
        if guild.system_channel:
            await guild.system_channel.send(f'Bem-vindo {member.mention} ao {guild.name}!')

    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.content.lower().startswith("ty: darxp"):
            await self.experience.add_catalog_xp_command(message)
            return 

        if message.content.lower().startswith("ty: listarxp"):
            await self.experience.list_catalog_command(message)
            return 
        
        if message.content.lower() == "ty: ajuda":
            await self.experience.help_command(message)
            return

        await self.experience.xp_command(message)
        await self.experience.ranking_command(message)
        await self.experience.ranking_hierarchy(message)
        await self.experience.team_commands(message)

intents = Intents.default()
intents.members = True
intents.message_content = True

client = Minerva(intents=intents)
client.run(TOKEN)