import json
import os # Importar o módulo os para checagem de arquivos

# --- CONSTANTES DE ARQUIVO ---
XP_DATA_FILE = "xp_data.json"
TEAMS_DATA_FILE = "teams_data.json"
KNOWLEDGE_DATA_FILE = "data/knowledge_data.json" # Novo arquivo de conhecimento

# --- VARIÁVEIS GLOBAIS EM TEMPO DE EXECUÇÃO (CACHE) ---
user_xp_data = {}
team_points_data = {}
knowledge_data = {} # Novo cache para o conhecimento

# --- FUNÇÕES UTILITÁRIAS GENÉRICAS ---

def load_json(filepath: str) -> dict:
    """Carrega dados de um arquivo JSON. Retorna {} se o arquivo não existir."""
    if not os.path.exists(filepath):
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"ERRO: O arquivo {filepath} está corrompido ou vazio.")
        return {}
        
def save_json(filepath: str, data: dict, indent: int = 4):
    """Salva dados em um arquivo JSON."""
    # Garante que o diretório exista antes de salvar
    dir_path = os.path.dirname(filepath)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)

    with open(filepath, "w", encoding='utf-8') as file:
        json.dump(data, file, indent=indent)

# --- LÓGICA DE CONHECIMENTO (ORÁCULO) ---

def load_knowledge_data():
    """Carrega os dados do Oráculo de Conhecimento e armazena no cache."""
    global knowledge_data
    
    # Usa a função utilitária genérica
    data = load_json(KNOWLEDGE_DATA_FILE)
    knowledge_data = data 
    
    # Retorna os dois dicionários principais para o serviço/cog
    return (
        data.get("cargos_relevantes", {}),
        data.get("knowledge_base", {})
    )

# --- LÓGICA DE XP (Suas funções existentes, adaptadas para usar a função save_json) ---

def load_xp_data():
    """Carrega os dados de XP do arquivo JSON para o dicionário."""
    global user_xp_data
    data = load_json(XP_DATA_FILE) # Usa a função utilitária genérica
    
    # Garante que as chaves sejam ints, não strings
    user_xp_data = {int(user_id): xp for user_id, xp in data.items()}

def save_xp_data():
    """Salva os dados de XP no arquivo JSON."""
    save_json(XP_DATA_FILE, user_xp_data) # Usa a função utilitária genérica

def get_user_xp(user_id: int) -> int:
    """Retorna o XP atual do usuário ou 0 se ainda não existir."""
    return user_xp_data.get(user_id, 0)

def add_xp(user_id: int, xp: int):
    """Adiciona XP ao usuário e atualiza o arquivo JSON."""
    user_xp_data[user_id] = user_xp_data.get(user_id, 0) + xp
    save_xp_data()

# --- LÓGICA DE EQUIPES (Suas funções existentes, adaptadas para usar a função save_json) ---

def load_teams_data():
    """Carrega os dados de pontos das equipes."""
    global team_points_data
    team_points_data = load_json(TEAMS_DATA_FILE) # Usa a função utilitária genérica

def save_teams_data():
    """Salva os dados de pontos das equipes no arquivo JSON."""
    save_json(TEAMS_DATA_FILE, team_points_data) # Usa a função utilitária genérica

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