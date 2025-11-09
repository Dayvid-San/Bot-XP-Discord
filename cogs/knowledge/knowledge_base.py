CARGOS_RELEVANTES = {
    "CEO": 5,      # Nível mais alto
    "Diretor": 4,
    "Gerente": 3,
    "Coordenador": 2,
    "Membro": 1,   # Nível base
    "Recruta": 0
}

# BASE DE CONHECIMENTO
# Chave: Nome da Informação (que será o argumento do comando)
# Valor: Dicionário contendo a descrição (o dado) e o nível mínimo de acesso.

KNOWLEDGE_BASE = {
    # Nível 1: Membro
    "missao": {
        "acesso_min": CARGOS_RELEVANTES["Membro"],
        "info": "Nossa missão é desenvolver soluções inovadoras e sustentáveis que transformem o mercado de tecnologia na América Latina.",
        "titulo": "Missão Empresarial",
    },
    "visao": {
        "acesso_min": CARGOS_RELEVANTES["Membro"],
        "info": "Ser a empresa líder em IA e Blockchain até 2028, com foco em impacto social.",
        "titulo": "Visão de Futuro",
    },
    
    # Nível 2: Coordenador
    "metas_q3": {
        "acesso_min": CARGOS_RELEVANTES["Coordenador"],
        "info": "Aumentar a base de usuários em 30% e lançar o Produto Alpha 2.0. Foco em otimização de custos em 15%.",
        "titulo": "Metas Estratégicas - Q3 2025",
    },
    
    # Nível 3: Gerente
    "budget_marketing": {
        "acesso_min": CARGOS_RELEVANTES["Gerente"],
        "info": "O orçamento total de marketing para o segundo semestre é de R$ 450.000, dividido igualmente entre digital e eventos.",
        "titulo": "Orçamento do Departamento de Marketing",
    },

    # Nível 5: CEO (Acesso Restrito)
    "aquisicoes_em_negociacao": {
        "acesso_min": CARGOS_RELEVANTES["CEO"],
        "info": "Não autorizado. Informação de alta confidencialidade sobre possíveis aquisições no setor de FinTech.",
        "titulo": "Estratégia de Aquisições",
    },
    
    # Adicione mais informações aqui, mapeando os cargos
}