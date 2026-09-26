import pandas as pd
import numpy as np
import json
import os

print("Iniciando ETL: Processamento de Dados do Sofascore...")

POSITION_MAP = {
    'GK': 'GL',
    'ST': 'ATA',
    'CF': 'ATA',
    'LW': 'PE',
    'RW': 'PD',
    'AM': 'MEI',
    'CM': 'MC',
    'DM': 'VOL',
    'LB': 'LE',
    'LWB': 'LE',
    'RB': 'LD',
    'RWB': 'LD',
    'CB': 'ZAG'
}

def map_position(row_details):
    if not row_details:
        return "N/D"
    
    detailed = row_details.get('positionsDetailed', [])
    if detailed:
        # Pega a primeira posição detalhada que conseguirmos mapear
        for pos in detailed:
            if pos in POSITION_MAP:
                return POSITION_MAP[pos]
    
    # Fallback para o geral
    general = row_details.get('position')
    if general == 'G': return 'GL'
    if general == 'D': return 'ZAG' # Fallback seguro
    if general == 'M': return 'MC'
    if general == 'F': return 'ATA'
    
    return "N/D"

def load_category(category):
    file_path = f"data/raw_{category}.json"
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return pd.DataFrame()

    with open(file_path, "r") as f:
        data = json.load(f)

    if not data:
        return pd.DataFrame()

    records = []
    for row in data:
        player = row.get('player', {})
        team = row.get('team', {})

        record = {
            'player_id': player.get('id'),
            'player_name': player.get('name'),
            'team_name': team.get('name'),
        }

        # Estatísticas no primeiro nível
        for k, v in row.items():
            if k not in ['player', 'team'] and not isinstance(v, dict):
                record[k] = v

        records.append(record)

    df = pd.DataFrame(records)
    df = df.drop_duplicates(subset=['player_id'])

    # Adicionar sufixo de categoria (exceto colunas base)
    if category != 'attack':
        base_cols = ['player_id', 'player_name', 'team_name']
        rename_dict = {col: f"{col}_{category}" for col in df.columns if col not in base_cols}
        df = df.rename(columns=rename_dict)

    return df

categories = ['attack', 'defence', 'passing', 'goalkeeping', 'detailed']
base_df = load_category('attack')

if base_df.empty:
    print("ERRO: Dados de Attack vazios. O Scraper pode ter falhado.")
else:
    for cat in categories[1:]:
        df_cat = load_category(cat)
        if not df_cat.empty:
            base_df = base_df.merge(df_cat, on=['player_id', 'player_name', 'team_name'], how='outer')

    # --- Resolver detalhes (Posição e Valor de Mercado) ---
    details_path = 'data/player_details.json'
    if os.path.exists(details_path):
        with open(details_path) as f:
            details_map = json.load(f)
        
        # Mapear Posição Detalhada
        base_df['position'] = base_df['player_id'].map(
            lambda pid: map_position(details_map.get(str(pid)) or details_map.get(pid))
        )
        
        # Inserir Valor de Mercado
        base_df['market_value'] = base_df['player_id'].map(
            lambda pid: (details_map.get(str(pid)) or details_map.get(pid, {})).get('marketValue')
        )

        # Inserir Idade
        import time
        now_ts = time.time()
        def get_age(pid):
            info = details_map.get(str(pid)) or details_map.get(pid, {})
            dob_ts = info.get('dateOfBirthTimestamp')
            if dob_ts:
                try:
                    return round((now_ts - float(dob_ts)) / (365.25 * 86400), 1)
                except (ValueError, TypeError):
                    return None
            return None

        base_df['age'] = base_df['player_id'].map(get_age)
        
        # Inserir Estatísticas Específicas de Goleiro
        gk_fields = ['saves', 'cleanSheet', 'goalsConceded', 'goalsPrevented', 'penaltySave', 'highClaims', 'punches']
        for gk_f in gk_fields:
            col_name = f"{gk_f}_goalkeeping"
            base_df[col_name] = base_df['player_id'].map(
                lambda pid: (details_map.get(str(pid)) or details_map.get(pid, {})).get('gk_stats', {}).get(gk_f, 0)
            )

        print(f"Detalhes de posição, valor, idade e estatísticas de goleiro integrados para {len(base_df)} jogadores.")
    else:
        base_df['position'] = "N/D"
        base_df['market_value'] = 0
        base_df['age'] = None
        print("Aviso: player_details.json não encontrado.")

    # Cálculo do GxG (Eficiência Real: Gols - expectedGoals)
    if 'expectedGoals' in base_df.columns:
        base_df['expectedGoals'] = base_df['expectedGoals'].fillna(0)
        base_df['goals'] = base_df.get('goals', pd.Series(0, index=base_df.index)).fillna(0)
        base_df['GxG'] = (base_df['goals'] - base_df['expectedGoals']).round(2)
    
    # Renomear algumas colunas de 'detailed' para nomes mais amigáveis antes do processamento final se necessário
    # mas o app.py cuida disso via COLUMN_LABELS.

    # Salvar
    output_path = "data/dataset_brasileirao_2026.parquet"
    base_df.to_parquet(output_path, engine='pyarrow')
    print(f"Pipeline ETL concluído: {output_path} ({len(base_df)} jogadores)")
