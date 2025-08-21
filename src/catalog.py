class catalog:
    def __init__(self):
        self.catalog_xp = {
        "Desafios de Programação": [
            {"Nível": "Fácil", "XP": 200, "Observações": "Algoritmos simples, lógica básica"},
            {"Nível": "Médio", "XP": 400, "Observações": "Estruturas de dados, recursão"},
            {"Nível": "Difícil", "XP": 800, "Observações": "Grafos, programação dinâmica"},
        ],
        "Feats de Projeto": [
            {"Escopo": "Pequena", "XP": 400, "Observações": "Bugfix, ajuste de layout, endpoint simples"},
            {"Escopo": "Média", "XP": 1600, "Observações": "Feature com front+back, integração"},
            {"Escopo": "Grande", "XP": 6400, "Observações": "Módulo completo, refatoração ampla"},
        ],
        "Participação em Eventos": [
            {"Tipo": "Inscrição/presença", "XP": 200, "Observações": "Meetup, workshop, palestra (sem apresentar)"},
            {"Tipo": "Contribuição ativa", "XP": 800, "Observações": "Apresentação de case, mini-palestra"},
        ],
        "Competições de Programação": [
            {"Colocação": "1º lugar", "XP": 6400, "Observações": "“Mestre de armas”"},
            {"Colocação": "2º lugar", "XP": 3200, "Observações": ""},
            {"Colocação": "3º lugar", "XP": 1600, "Observações": ""},
            {"Colocação": "4º–10º lugar", "XP": 800, "Observações": ""},
            {"Colocação": "Participação", "XP": 200, "Observações": ""},
        ],
        "Contratos Assinados": [
            {"Tamanho": "Pequeno (R$ 500–1 500)", "XP": 3200, "Observações": "Equivale a 2º lugar em competição"},
            {"Tamanho": "Médio (R$ 1 500–5 000)", "XP": 6400, "Observações": "Equivale a feat grande"},
            {"Tamanho": "Grande (> R$ 5 000/rec.)", "XP": 25600, "Observações": "Permite alcançar “Desafiante”"},
        ],
        "Palestras & Apresentações": [
            {"Tipo": "Slide único", "XP": 200, "Observações": "Igual a um desafio fácil"},
            {"Tipo": "Deck básico", "XP": 800, "Observações": "Equivale a desafio difícil"},
            {"Tipo": "Deck avançado", "XP": 1600, "Observações": "Design customizado, gráficos, infográficos"},
            {"Tipo": "Pitch completo", "XP": 3200, "Observações": "Storytelling, protótipos, animações leves"},
            {"Tipo": "Roadshow master", "XP": 6400, "Observações": "Templates próprios, Q&A"},
        ],
        "Documentação Estratégica & Técnica": [
            {"Tipo": "One-pager estratégico", "XP": 400, "Observações": "Visão geral numa única página"},
            {"Tipo": "Plano de projeto curto", "XP": 800, "Observações": "Roadmap 1 mês, cronograma simples"},
            {"Tipo": "Documento estratégico", "XP": 1600, "Observações": "Roadmap 3–6 meses, OKRs, KPIs"},
            {"Tipo": "Whitepaper / Business Plan", "XP": 3200, "Observações": "Mercado, SWOT, projeções"},
            {"Tipo": "Plano estratégico anual", "XP": 6400, "Observações": "Business case, orçamento, riscos"},
        ],
        "Gestão de Mídias Sociais": [
            {"Atividade": "Post simples", "XP": 200, "Observações": "Feed ou story"},
            {"Atividade": "Reel curto", "XP": 400, "Observações": "Edição leve"},
            {"Atividade": "Reel médio/longo", "XP": 800, "Observações": "Roteiro + edição elaborada"},
            {"Atividade": "Roteiro de vídeo/posts", "XP": 400, "Observações": "Apenas planejamento"},
            {"Atividade": "Planejamento mensal", "XP": 1600, "Observações": "Visão estratégica"},
            {"Atividade": "Campanha temática", "XP": 3200, "Observações": "Ex: Tech week"},
            {"Atividade": "Lançamento de produto/evento", "XP": 6400, "Observações": "Comunicação oficial"},
            {"Atividade": "Análise + relatório", "XP": 1600, "Observações": "Métricas mensais"},
        ],
        "Bônus por Engajamento": [
            {"+100 curtidas ou +20 comentários": {"XP Bônus": 200, "Limite": "Máx. 2x/semana"}},
            {"+1 000 visualizações em reels": {"XP Bônus": 400, "Limite": "Máx. 2x/semana"}},
            {"Conteúdo viral (> 10 000 views)": {"XP Bônus": 1600, "Limite": "Máx. 1x/semana"}},
        ]
    }

    def getCatalog(self):
        return catalog

    def checkCatalog(self, categoria):
        if categoria in self.catalog_xp:
            for item in self.catalog_xp[categoria]:
                print(item)
        else:
            print("Categoria não encontrada.")

