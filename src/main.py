import discord
from discord import Client, Intents
from discord.member import Member
from discord.message import Message
from dotenv import load_dotenv
import os
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
botName = 'Athena'
XP_DATA_FILE = "xp_data.json"

# Dicionário para armazenar o XP dos usuários em memória
user_xp_data = {}

def load_xp_data():
    """Carrega os dados de XP do arquivo JSON para o dicionário."""
    global user_xp_data
    try:
        with open(XP_DATA_FILE, "r") as file:
            data = json.load(file)
            # Converter as chaves para int, pois o JSON armazena como string
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
        json.dump(team_points_data, file, indent=4) # indent=4 para melhor legibilidade

def add_team_points(team_name: str, points: int):
    """Adiciona pontos a uma equipe e atualiza o arquivo JSON."""
    if team_name in team_points_data:
        team_points_data[team_name]["points"] += points
    else:
        # Se a equipe não existe, inicializa com os pontos e uma lista vazia de membros
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

    async def xp_command(self, message: Message):
        # Ignora mensagens enviadas pelo próprio bot
        if message.author == self.client.user:
            return

        user_xp = get_user_xp(message.author.id)

        # Comando: ty: xp
        if message.content.lower() == "ty: xp":
            await message.channel.send(f"XP do usuário {message.author.mention}: {user_xp} XP")
            return

        # Comando: ty: guardião
        if message.content.lower() == "ty: guardião":
            await message.channel.send(
                f"Olá, {message.author.mention}! Eu sou {botName}, a coruja sábia que se tornou a mascote orgulhosa desta incrível comunidade.\n\n"
                "Eu represento o compromisso da TYTO.code com a excelência em administração, suporte aos desenvolvedores e organização de projetos. "
                "Se você tiver ideias para aprimorar a minha atuação ou sugestões para a TYTO.code, ficarei encantada em ouvir."
            )
            return

        # Comando: ty: xp <menção>
        if message.content.lower().startswith("ty: xp"):
            if message.mentions:
                mentioned_user = message.mentions[0]
                mentioned_xp = get_user_xp(mentioned_user.id)
                await message.channel.send(f"XP de {mentioned_user.mention}: {mentioned_xp}")
            else:
                await message.channel.send("Usuário não catalogado!")
            return

        # Comando: ty: addxp <menção> <quantidade>
        if message.content.lower().startswith("ty: addxp"):
            await self.add_xp_command(message)

    async def add_xp_command(self, message: Message):
        if message.author.bot:
            return

        # Apenas administradores podem adicionar XP
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Você não tem permissão para usar este comando.")
            return

        try:
            # Exemplo de comando: ty: addxp @usuario 100
            # Usar message.mentions para extrair o usuário mencionado
            mentioned_user = message.mentions[0]
            # A quantidade de XP é o último argumento
            xp_to_add = int(message.content.split()[-1])
            add_xp(mentioned_user.id, xp_to_add)
            await message.channel.send(f"{xp_to_add}xp foram adicionados para o usuário {mentioned_user.mention}!")
        except (IndexError, ValueError):
            await message.channel.send("Use o comando assim: `ty: addxp @usuario [quantidade]`.")

    async def ranking_command(self, message: Message):
        # Ignora mensagens do bot
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
        # Verifica se a mensagem é do tipo esperado e ignora bots
        if isinstance(message, discord.Message):
            if message.author.bot:
                return
        else:
            print("Mensagem não é do tipo esperado:", type(message))

        user_xp = get_user_xp(message.author.id)
        xp_roles = [
            ("👑 Lorde", 6809600),
            ("⚜️ Nobre", 1702400),
            ("🛡️ Cavalaria", 425600),
            ("⚔️ Oficiais", 106400),
            ("💰 Soldado de aluguel", 25600),
            ("✝️ Monge", 6400),
            ("🛠️ Armeiro", 1600),
            ("🧑‍🎓 Escudeiro", 400),
        ]
        
        for role_name, required_xp in xp_roles:
            if user_xp >= required_xp:
                # Procura o cargo pelo nome
                role = discord.utils.get(message.guild.roles, name=role_name)
                # Se o cargo existir e o usuário ainda não o tiver, adiciona-o
                if role and role not in message.author.roles:
                    await message.author.add_roles(role)
                    await message.channel.send(
                        f"Parabéns, {message.author.mention}! Você ganhou o cargo de {role.name}!"
                    )


    async def team_commands(self, message: Message):
        if message.author.bot:
            return

        # Comando: ty: criarequipe <nome_da_equipe>
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

        # Comando: ty: adicionarmembro <nome_da_equipe> <menção>
        if message.content.lower().startswith("ty: adicionarmembro"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send("Você não tem permissão para adicionar membros a equipes.")
                return
            
            try:
                parts = message.content.split()
                team_name = " ".join(parts[2:-1]) # Pegar o nome da equipe, pode ter espaços
                mentioned_user = message.mentions[0]

                if add_member_to_team(team_name, mentioned_user.id):
                    await message.channel.send(f"{mentioned_user.mention} foi adicionado à equipe '{team_name}'!")
                else:
                    await message.channel.send(f"Erro ao adicionar {mentioned_user.mention} à equipe '{team_name}'. Verifique se a equipe existe ou se o usuário já é membro.")
            except (IndexError, ValueError):
                await message.channel.send("Use o comando assim: `ty: adicionarmembro [nome da equipe] @membro`.")
            return
            
        # Comando: ty: darpontosequipe <nome_da_equipe> <quantidade>
        if message.content.lower().startswith("ty: darpontosequipe"):
            if not message.author.guild_permissions.administrator:
                await message.channel.send("Você não tem permissão para dar pontos a equipes.")
                return
            
            try:
                parts = message.content.split()
                # A quantidade é o último elemento, o nome da equipe é o restante
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

        # Comando: ty: rankingequipes
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

        # Comando: ty: minhaequipe
        if message.content.lower() == "ty: minhaequipe":
            user_team = get_user_team(message.author.id)
            if user_team:
                team_points = team_points_data[user_team]["points"]
                await message.channel.send(f"Você pertence à equipe **{user_team}** com {team_points} pontos.")
            else:
                await message.channel.send("Você não pertence a nenhuma equipe ainda.")
            return


class Minerva(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.experience = ExperienceManager(self)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        load_xp_data()  # Carrega os dados de XP ao iniciar o bot

    async def on_member_join(self, member: Member):
        guild = member.guild
        if guild.system_channel:
            await guild.system_channel.send(f'Welcome {member.mention} to {guild.name}!')

    async def on_message(self, message: Message):
        await self.experience.xp_command(message)
        await self.experience.ranking_command(message)
        await self.experience.ranking_hierarchy(message)

intents = Intents.default()
intents.members = True
intents.message_content = True

client = Minerva(intents=intents)
client.run(TOKEN)
