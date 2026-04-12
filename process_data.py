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
        
        # Base info
        record = {
            'player_id': player.get('id'),
            'player_name': player.get('name'),
            'position': player.get('position'),
            'team_name': team.get('name'),
        }
        
        # Outras estatísticas estão no primeiro nível (ex: goals, expectedGoals)
        for k, v in row.items():
            if k not in ['player', 'team'] and not isinstance(v, dict):
                record[k] = v
                
        records.append(record)
        
    df = pd.DataFrame(records)
    # remover duplicados caso a paginação tenha trazido redundância
    df = df.drop_duplicates(subset=['player_id'])
    
    # Adicionar sufixo usando a categoria (exceto para cols base) para lidar com merges se houver colisões (exceto attack)
    if category != 'attack':
        rename_dict = {col: f"{col}_{category}" for col in df.columns if col not in ['player_id', 'player_name', 'position', 'team_name']}
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
            base_df = base_df.merge(df_cat, on=['player_id', 'player_name', 'position', 'team_name'], how='outer')
            
    print(f"Colunas disponíveis no dataset consolidado: {list(base_df.columns)}")
    
    # Transformação requirida: GxG = Goals - Expected Goals (xG)
    if 'goals' in base_df.columns and 'expectedGoals' in base_df.columns:
        # Preencher NaNs com 0 para o cálculo se houver
        base_df['goals'] = base_df['goals'].fillna(0)
        base_df['expectedGoals'] = base_df['expectedGoals'].fillna(0)
        base_df['GxG'] = base_df['goals'] - base_df['expectedGoals']
        print("Nova métrica 'GxG' criada com sucesso.")
    else:
        print("Aviso: 'goals' ou 'expectedGoals' não encontrados nos dados.")
        
    # Salvar em Parquet format
    output_path = "data/dataset_brasileirao_2026.parquet"
    base_df.to_parquet(output_path, engine='pyarrow')
    print(f"Pipeline ETL concluído: Dataset salvo em {output_path} (Total de Jogadores: {len(base_df)})")
