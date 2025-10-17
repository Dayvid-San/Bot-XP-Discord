import json

# Mantenha as constantes de arquivo aqui ou mova para um config/
XP_DATA_FILE = "xp_data.json"
TEAMS_DATA_FILE = "teams_data.json"

# Variáveis globais em tempo de execução para cache
user_xp_data = {}
team_points_data = {}

# --- Lógica de XP ---

def load_xp_data():
    """Carrega os dados de XP do arquivo JSON para o dicionário."""
    global user_xp_data
    try:
        with open(XP_DATA_FILE, "r") as file:
            data = json.load(file)
            # Garante que as chaves sejam ints, não strings
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
    user_xp_data[user_id] = user_xp_data.get(user_id, 0) + xp
    save_xp_data()

# --- Lógica de Equipes ---

def load_teams_data():
    """Carrega os dados de pontos das equipes."""
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
# ... Ficam aqui, exatamente como no seu código original ...