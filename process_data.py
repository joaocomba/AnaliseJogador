import pandas as pd
import json
import os

print("Iniciando ETL: Processamento de Dados do Sofascore...")

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

    # Adicionar sufixo de categoria (exceto attack e colunas base)
    if category != 'attack':
        base_cols = ['player_id', 'player_name', 'team_name']
        rename_dict = {col: f"{col}_{category}" for col in df.columns if col not in base_cols}
        df = df.rename(columns=rename_dict)

    return df

categories = ['attack', 'defense', 'passing', 'goalkeeping']
base_df = load_category('attack')

if base_df.empty:
    print("ERRO: Dados de Attack vazios. O Scraper pode ter falhado.")
else:
    for cat in categories[1:]:
        df_cat = load_category(cat)
        if not df_cat.empty:
            base_df = base_df.merge(df_cat, on=['player_id', 'player_name', 'team_name'], how='outer')

    # --- Resolver posições via arquivo gerado pelo scraper ---
    positions_path = 'data/player_positions.json'
    if os.path.exists(positions_path):
        with open(positions_path) as f:
            positions_map = json.load(f)
        # O JSON usa string keys
        base_df['position'] = base_df['player_id'].map(
            lambda pid: positions_map.get(str(pid)) or positions_map.get(pid)
        )
        total_with_pos = base_df['position'].notna().sum()
        print(f"Posição resolvida para {total_with_pos}/{len(base_df)} jogadores.")
    else:
        base_df['position'] = None
        print("Aviso: player_positions.json não encontrado. Execute o scraper para popular posições.")

    print(f"Colunas disponíveis: {list(base_df.columns)}")

    # Cálculo do GxG
    if 'goals' in base_df.columns and 'expectedGoals' in base_df.columns:
        base_df['goals'] = base_df['goals'].fillna(0)
        base_df['expectedGoals'] = base_df['expectedGoals'].fillna(0)
        base_df['GxG'] = base_df['goals'] - base_df['expectedGoals']
        print("Nova métrica 'GxG' criada com sucesso.")
    else:
        print("Aviso: 'goals' ou 'expectedGoals' não encontrados.")

    # Remover colunas desnecessárias
    cols_to_drop = ['rating_passing']
    base_df = base_df.drop(columns=[c for c in cols_to_drop if c in base_df.columns])

    # Salvar
    output_path = "data/dataset_brasileirao_2026.parquet"
    base_df.to_parquet(output_path, engine='pyarrow')
    print(f"Pipeline ETL concluído: {output_path} ({len(base_df)} jogadores)")
