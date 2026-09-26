import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
import numpy as np
from datetime import datetime

# --- MAPEAMENTO DE NOMES DE COLUNAS (PT-BR) ---
COLUMN_LABELS = {
    'player_id':                       'ID',
    'player_name':                     'Jogador',
    'team_name':                       'Time',
    'position':                        'Posição',
    'goals':                           'Gols',
    'expectedGoals':                   'xG',
    'GxG':                             'GxG',
    'bigChancesMissed':                'Chances Perdidas',
    'successfulDribbles':              'Dribles',
    'totalShots':                      'Finalizações',
    'goalConversionPercentage':        'Conversão de Finalização (%)',
    'rating':                          'Nota Média',
    'bigChancesCreated_passing':       'Chances Criadas',
    'assists_passing':                 'Assistências',
    'accuratePasses_passing':          'Passes Certos',
    'accuratePassesPercentage_passing':'Conversão de Passes (%)',
    'keyPasses_passing':               'Passes Chave',
    # Colunas defensivas
    'tackles_defence':                 'Desarmes',
    'interceptions_defence':           'Interceptações',
    'clearances_defence':              'Cortes',
    'outfielderBlocks_defence':        'Chutes Bloqueados',
    'errorLeadToGoal_defence':         'Erros que Geraram Gol',
    'rating_defence':                  'Nota Média (Def)',
    # Detalhes e Mercado
    'age':                             'Idade',
    'market_value':                    'Valor de Mercado (€)',
    'performance_market_value':        'Valor de Desempenho (€)',
    'value_diff_euro':                 'Diferença de Valor (€)',
    'value_diff_pct':                  'Diferença (%)',
    'appearances_detailed':            'Partidas',
    'yellowCards_detailed':            'Cartões Amarelos',
    'redCards_detailed':               'Cartões Vermelhos',
    'totalDuelsWon_detailed':          'Duelos Ganhos',
    'fouls_detailed':                  'Faltas Cometidas',
    # Estatísticas de Goleiro
    'saves_goalkeeping':               'Defesas',
    'cleanSheet_goalkeeping':          'Jogos sem Sofrer Gol',
    'goalsConceded_goalkeeping':       'Gols Sofridos',
    'goalsPrevented_goalkeeping':      'Gols Evitados (xG)',
    'penaltySave_goalkeeping':         'Pênaltis Defendidos',
    'highClaims_goalkeeping':          'Bolas Altas Agarradas',
    'punches_goalkeeping':             'Socos na Bola'
}

# --- CÁLCULO DO VALOR DE MERCADO POR DESEMPENHO E IDADE ---
def add_performance_market_value(df):
    if df.empty or 'market_value' not in df.columns:
        return df

    df = df.copy()
    mv_num = pd.to_numeric(df['market_value'], errors='coerce').fillna(0)

    # Obter número de partidas jogadas (amostragem)
    apps = pd.Series(0, index=df.index, dtype=float)
    if 'appearances_detailed' in df.columns:
        apps = pd.to_numeric(df['appearances_detailed'], errors='coerce').fillna(0)
    elif 'appearances' in df.columns:
        apps = pd.to_numeric(df['appearances'], errors='coerce').fillna(0)

    # Obter idade do jogador
    ages = pd.Series(np.nan, index=df.index, dtype=float)
    if 'age' in df.columns:
        ages = pd.to_numeric(df['age'], errors='coerce')

    # Fator de Idade (Curva de Valorização por Potencial Futuro)
    # - Idade <= 23: Jovem com potencial de revenda (+5% por ano abaixo de 23)
    # - Idade 23 a 28: Ápice físico/tático (Multiplicador 1.0x neutro)
    # - Idade > 28: Depreciação por idade (-3.5% por ano acima de 28)
    def get_age_multiplier(age):
        if pd.isna(age) or age <= 0:
            return 1.0
        if age <= 23:
            return 1.0 + 0.05 * (23.0 - age)
        elif age <= 28:
            return 1.0
        else:
            return max(0.65, 1.0 - 0.035 * (age - 28.0))

    age_multipliers = ages.apply(get_age_multiplier)

    # Métricas relevantes por posição para calcular percentil de desempenho
    pos_metrics = {
        'ATA': ['goals', 'expectedGoals', 'GxG', 'totalShots', 'successfulDribbles', 'rating'],
        'PE':  ['goals', 'expectedGoals', 'GxG', 'totalShots', 'successfulDribbles', 'rating'],
        'PD':  ['goals', 'expectedGoals', 'GxG', 'totalShots', 'successfulDribbles', 'rating'],
        'MEI': ['assists_passing', 'keyPasses_passing', 'accuratePassesPercentage_passing', 'bigChancesCreated_passing', 'successfulDribbles', 'rating'],
        'MC':  ['assists_passing', 'keyPasses_passing', 'accuratePassesPercentage_passing', 'bigChancesCreated_passing', 'successfulDribbles', 'rating'],
        'VOL': ['tackles_defence', 'interceptions_defence', 'accuratePassesPercentage_passing', 'totalDuelsWon_detailed', 'rating'],
        'ZAG': ['tackles_defence', 'interceptions_defence', 'clearances_defence', 'outfielderBlocks_defence', 'totalDuelsWon_detailed', 'rating'],
        'LD':  ['tackles_defence', 'interceptions_defence', 'keyPasses_passing', 'accuratePassesPercentage_passing', 'successfulDribbles', 'rating'],
        'LE':  ['tackles_defence', 'interceptions_defence', 'keyPasses_passing', 'accuratePassesPercentage_passing', 'successfulDribbles', 'rating'],
        'GL':  ['saves_goalkeeping', 'cleanSheet_goalkeeping', 'goalsPrevented_goalkeeping', 'penaltySave_goalkeeping', 'rating']
    }

    perf_scores = pd.Series(0.5, index=df.index, dtype=float)

    if 'position' in df.columns:
        for pos in df['position'].dropna().unique():
            if pos == 'N/D':
                continue
            pos_mask = (df['position'] == pos)
            sub_df = df[pos_mask]
            
            metrics = pos_metrics.get(pos, ['rating', 'goals', 'assists_passing', 'tackles_defence'])
            valid_metrics = [m for m in metrics if m in sub_df.columns]
            
            if valid_metrics and len(sub_df) > 1:
                pcts = sub_df[valid_metrics].rank(pct=True).mean(axis=1)
                perf_scores.update(pcts)

    # Multiplicador Bruto de Desempenho (0.60x a 1.40x em relação à mediana 0.5)
    raw_multipliers = 0.60 + (0.80 * perf_scores)

    # Fator de Confiança por Número de Partidas (0.20 a 1.00)
    confidence_weight = np.clip(apps / 15.0, 0.20, 1.00)

    # Multiplicador Final Combinando Desempenho x Consistência x Fator Idade
    performance_adj = 1.0 + (confidence_weight * (raw_multipliers - 1.0))
    final_multipliers = performance_adj * age_multipliers

    # Para jogadores sem valor oficial, usa a mediana de mercado da posição
    pos_medians = df.groupby('position')['market_value'].transform(lambda x: x[pd.to_numeric(x, errors='coerce') > 0].median() if len(x[pd.to_numeric(x, errors='coerce') > 0]) > 0 else 0)
    pos_medians = pd.to_numeric(pos_medians, errors='coerce').fillna(0)

    base_values = mv_num.where(mv_num > 0, pos_medians)

    df['performance_market_value'] = (base_values * final_multipliers).round()
    df['value_diff_euro'] = (df['performance_market_value'] - mv_num).round()
    
    df['value_diff_pct'] = np.where(
        mv_num > 0,
        ((df['performance_market_value'] - mv_num) / mv_num) * 100,
        0.0
    ).round(1)

    return df

# --- HELPER ESCUDOS ---
TEAM_SHIELDS = {
    'Athletico': 'Athletico.png',
    'Atlético Mineiro': 'AtleticoMineiro.png',
    'Bahia': 'Bahia.png',
    'Botafogo': 'Botafogo.png',
    'Chapecoense': 'Chapecoense.png',
    'Corinthians': 'Corinthians.webp',
    'Coritiba': 'Coritiba.png',
    'Cruzeiro': 'Cruzeiro.png',
    'Flamengo': 'Flamengo.png',
    'Fluminense': 'Fluminense.webp',
    'Grêmio': 'Gremio.png',
    'Internacional': 'Internacional.webp',
    'Mirassol': 'Mirassol.png',
    'Palmeiras': 'Palmeiras.webp',
    'Red Bull Bragantino': 'Bragantino.png',
    'Remo': 'Remo.webp',
    'Santos': 'Santos.webp',
    'São Paulo': 'SaoPaulo.png',
    'Vasco da Gama': 'Vasco.webp',
    'Vitória': 'Vitoria.png'
}

@st.cache_data
def get_shield_b64(team_name):
    if not isinstance(team_name, str):
        return None
    filename = TEAM_SHIELDS.get(team_name)
    if not filename:
        return None
    path = os.path.join("escudos", filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = path.split('.')[-1]
            return f"data:image/{ext};base64,{encoded}"
    return None

def rename_for_display(df):
    """Renomeia colunas para exibição, sem alterar o DataFrame original."""
    return df.rename(columns={k: v for k, v in COLUMN_LABELS.items() if k in df.columns})

# Configuração de Página
st.set_page_config(page_title="Brasileirão Analytics", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS (NEXUS STYLE) ---
st.markdown("""
<style>
    /* Fontes e Estilo Base */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar - Removido cores fixas para respeitar o Dark Mode */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(0,0,0,0.1);
    }
    
    /* Blocos/Cards */
    div.css-1r6slb0, div.css-12oz5g7 {
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* Metric Cards - Removido cores fixas */
    [data-testid="stMetricValue"] {
        font-weight: 700;
        font-size: 28px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
    }

    .nexus-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    /* Ajuste para mobile */
    @media (max-width: 768px) {
        .stMetric {
            padding: 10px;
        }
    }
</style>
""", unsafe_allow_html=True)

def format_market_value(val):
    if pd.isna(val) or val == 0:
        return "N/D"
    if val >= 1_000_000:
        return f"€{val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"€{val/1_000:.0f}k"
    return f"€{val}"

# --- LOAD DATA ---
DATA_PATH = "data/dataset_brasileirao_2026.parquet"

def get_data_version():
    if os.path.exists(DATA_PATH):
        return os.path.getmtime(DATA_PATH)
    return None

@st.cache_data
def load_data(data_version):
    if data_version is not None and os.path.exists(DATA_PATH):
        df = pd.read_parquet(DATA_PATH)
        df = add_performance_market_value(df)
        return df
    st.warning(f"Extrato local ({DATA_PATH}) não encontrado. Execute o web scraper primeiro!")
    return pd.DataFrame()

# --- UI HEADER: IMAGES ---
col_logo1, col_logo2, _ = st.columns([1, 1, 4])
with col_logo1:
    if os.path.exists("brasileirao_logo.png"):
        st.image("brasileirao_logo.png", width=120)
with col_logo2:
    if os.path.exists("farroupilha.jpeg"):
        # Mesma largura para tentar manter altura proporcional (ajuste se necessário)
        st.image("farroupilha.jpeg", width=120)

data_version = get_data_version()
df = load_data(data_version)

# --- SIDEBAR FILTROS ---
st.sidebar.markdown("## Filtros")

if data_version is not None:
    updated_at = datetime.fromtimestamp(data_version).strftime("%d/%m/%Y %H:%M")
    st.sidebar.caption(f"Base carregada: {updated_at}")

teams = sorted(df['team_name'].dropna().unique())
selected_teams = st.sidebar.multiselect("Time", teams, default=[])

positions = sorted(df['position'].dropna().unique())
default_positions = positions
selected_positions = st.sidebar.multiselect("Posição", positions, default=default_positions)

st.sidebar.markdown("### Perfil do Atleta")

# Filtro de Idade
min_age_val = int(df['age'].min()) if 'age' in df.columns and not df['age'].dropna().empty else 16
max_age_val = int(df['age'].max()) if 'age' in df.columns and not df['age'].dropna().empty else 45
age_range = st.sidebar.slider("Faixa de Idade (Anos)", min_value=min_age_val, max_value=max_age_val, value=(min_age_val, max_age_val))

# Filtro de Valor de Mercado (€ M) - Permitir Digitação
st.sidebar.markdown("**Valor de Mercado (€ M)**")
col_mv1, col_mv2 = st.sidebar.columns(2)

mv_max_real = df['market_value'].max() if 'market_value' in df.columns and not df['market_value'].dropna().empty else 40_000_000
max_mv_m = float(np.ceil(mv_max_real / 1_000_000.0)) if mv_max_real > 0 else 40.0

with col_mv1:
    min_mv_input = st.number_input("Mín (€M)", min_value=0.0, max_value=max_mv_m, value=0.0, step=0.5, format="%.1f")
with col_mv2:
    max_mv_input = st.number_input("Máx (€M)", min_value=0.0, max_value=max_mv_m, value=max_mv_m, step=0.5, format="%.1f")

if min_mv_input > max_mv_input:
    min_mv_input, max_mv_input = max_mv_input, min_mv_input

mv_range = (min_mv_input, max_mv_input)

st.sidebar.markdown("### Métricas (Mínimos)")
min_matches = st.sidebar.slider("Mínimo Partidas Jogadas", 0, 38, 5)

# Aplicação dos Filtros
if 'appearances_detailed' in df.columns:
    df = df[df['appearances_detailed'] >= min_matches]
elif 'appearances' in df.columns:
    df = df[df['appearances'] >= min_matches]

if selected_teams:
    df = df[df['team_name'].isin(selected_teams)]
if selected_positions:
    df = df[df['position'].isin(selected_positions)]

if 'age' in df.columns:
    df = df[(df['age'].isna()) | ((df['age'] >= age_range[0]) & (df['age'] <= age_range[1]))]

if 'market_value' in df.columns:
    mv_num = pd.to_numeric(df['market_value'], errors='coerce').fillna(0)
    df = df[(mv_num >= mv_range[0] * 1_000_000) & (mv_num <= mv_range[1] * 1_000_000)]

# --- HEADER ---
st.markdown("<div class='nexus-title'>Dashboard - Performance de Jogadores</div>", unsafe_allow_html=True)

# --- NAVEGAÇÃO (radio button — compatível com mobile) ---
aba = st.radio(
    "",
    ["📊 Visão Geral", "🤝 Comparador"],
    horizontal=True,
    label_visibility="collapsed",
    key="nav_aba"
)
st.markdown("<hr style='margin:6px 0 16px 0'>", unsafe_allow_html=True)

if aba == "📊 Visão Geral":

    # --- KPIs ROW ---
    col1, col2, col3, col4, col5 = st.columns(5)

    top_scorer = df.loc[df['goals'].idxmax()] if not df.empty and 'goals' in df.columns else None
    top_gxg = df.loc[df['GxG'].idxmax()] if not df.empty and 'GxG' in df.columns else None
    total_goals = df['goals'].sum() if 'goals' in df.columns else 0
    total_val = df['market_value'].sum() if 'market_value' in df.columns else 0
    avg_rating = df['rating'].mean() if 'rating' in df.columns else 0

    with col1:
        st.metric("Total de Gols", f"{total_goals:,.0f}")
    with col2:
        st.metric("Valor Total Elenco", format_market_value(total_val))
    with col3:
        st.metric("Nota Média", f"{avg_rating:.2f}")
    with col4:
        if top_scorer is not None:
            st.metric("Artilheiro", f"{top_scorer['player_name']} ({int(top_scorer['goals'])})")
        else:
            st.metric("Artilheiro", "-")
    with col5:
        if top_gxg is not None:
            st.metric("Maior GxG", f"{top_gxg['player_name']} (+{top_gxg['GxG']:.2f})")
        else:
            st.metric("Maior GxG", "-")

    st.markdown("---")

    # --- CHARTS ROW ---
    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        st.markdown("### xG vs Goals (GxG em Destaque)")
        if 'goals' in df.columns and 'expectedGoals' in df.columns:
            plot_df = df.dropna(subset=['goals', 'expectedGoals', 'GxG']).copy()
            plot_df = plot_df[(plot_df['goals'] > 0) | (plot_df['expectedGoals'] > 0)]

            plot_df['Performance'] = ['Positiva (>0)' if x > 0 else 'Negativa (<0)' for x in plot_df['GxG']]
            color_map = {'Positiva (>0)': '#3b82f6', 'Negativa (<0)': '#ef4444'} # Blue & Red

            fig_scatter = px.scatter(
                plot_df, x='expectedGoals', y='goals', color='Performance',
                color_discrete_map=color_map,
                hover_name='player_name', hover_data=['team_name', 'GxG'],
                size='goals', size_max=15, opacity=0.8,
                title=""
            )
            # Adicionar linha diagonal de 1:1
            max_val = max(plot_df['expectedGoals'].max(), plot_df['goals'].max()) * 1.1 if not plot_df.empty else 10
            fig_scatter.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, 
                                  line=dict(color="Gray", dash="dash"))

            fig_scatter.update_layout(
                margin=dict(t=10, l=10, r=10, b=10),
                xaxis_title="Expected Goals (xG)", yaxis_title="Goals Scored",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

    with col_chart2:
        st.markdown("### GxG Distribution")
        if 'GxG' in df.columns:
            fig_hist = px.histogram(df, x='GxG', nbins=30, opacity=0.8,
                                    color_discrete_sequence=['#8b5cf6']) # Purple accent
            fig_hist.update_layout(
                margin=dict(t=10, l=10, r=10, b=10),
                xaxis_title="GxG", yaxis_title="Frequency", showlegend=False
            )
            fig_hist.add_vline(x=0, line_dash="dash", line_color="black")
            st.plotly_chart(fig_hist, use_container_width=True)

    # --- EXPLORADOR CUSTOMIZADO ---
    st.markdown("### Explorador de Variáveis Interativo")
    col_eixo_x, col_eixo_y = st.columns(2)

    # Usar rótulos traduzidos para os selectboxes, mapeando devolta para nome interno
    numeric_cols_raw = df.select_dtypes(include=['number']).columns.tolist()
    numeric_labels = {COLUMN_LABELS.get(c, c): c for c in numeric_cols_raw}
    label_list = list(numeric_labels.keys())

    with col_eixo_x:
        default_x_label = COLUMN_LABELS.get('expectedGoals', 'expectedGoals')
        default_x_idx = label_list.index(default_x_label) if default_x_label in label_list else 0
        eixo_x_label = st.selectbox("Variável do Eixo X", label_list, index=default_x_idx)
        eixo_x = numeric_labels[eixo_x_label]

    with col_eixo_y:
        default_y_label = COLUMN_LABELS.get('goals', 'goals')
        default_y_idx = label_list.index(default_y_label) if default_y_label in label_list else min(1, len(label_list)-1)
        eixo_y_label = st.selectbox("Variável do Eixo Y", label_list, index=default_y_idx)
        eixo_y = numeric_labels[eixo_y_label]

    if eixo_x and eixo_y:
        fig_explorer = px.scatter(
            df, x=eixo_x, y=eixo_y,
            color='team_name' if 'team_name' in df.columns else None,
            hover_name='player_name' if 'player_name' in df.columns else None,
            hover_data=['team_name'] if 'team_name' in df.columns else [],
            labels=COLUMN_LABELS,
            title=f"{eixo_y_label} vs {eixo_x_label}",
            opacity=0.8,
            size_max=12
        )
        fig_explorer.update_layout(
            margin=dict(t=30, l=10, r=10, b=10)
        )
        st.plotly_chart(fig_explorer, use_container_width=True)

    # --- TABELA COMPLETA NATIVA ---
    st.markdown("### Detalhamento Interativo de Jogadores")

    show_df = df.copy()

    # Adicionar escudos
    if 'team_name' in show_df.columns:
        show_df.insert(0, "Escudo", show_df["team_name"].apply(get_shield_b64))

    # Tratar dados faltantes
    for col in show_df.columns:
        if col == "Escudo":
            continue
        # Se for coluna de mercado ou diferença, garantir que é numérico antes do config
        if col in ["market_value", "performance_market_value", "value_diff_euro", "value_diff_pct"]:
            show_df[col] = pd.to_numeric(show_df[col], errors='coerce').fillna(0)
            continue
            
        if show_df[col].isnull().all():
            show_df[col] = "N/D"
        elif show_df[col].dtype == 'object' or show_df[col].dtype.name == 'category':
            show_df[col] = show_df[col].fillna("N/D")
        else:
            show_df[col] = show_df[col].fillna(0)

    # Renomear colunas para PT-BR
    show_df = rename_for_display(show_df)

    # Escudo sempre primeiro, depois Jogador, Time, Posição, Idade, Valor de Mercado, Valor de Desempenho e Diferenças
    fixed_order = [
        "Escudo", "Jogador", "Time", "Posição", "Idade",
        "Valor de Mercado (€)", "Valor de Desempenho (€)", "Diferença de Valor (€)", "Diferença (%)",
        "Gols", "xG", "GxG"
    ]
    ordered_cols = [c for c in fixed_order if c in show_df.columns] \
                   + [c for c in show_df.columns if c not in fixed_order]

    column_config = {
        "Escudo": st.column_config.ImageColumn("Time", help="Escudo Oficial do Clube"),
        "Idade": st.column_config.NumberColumn(
            "Idade",
            help="Idade do jogador em anos",
            format="%.0f anos"
        ),
        "Valor de Mercado (€)": st.column_config.NumberColumn(
            "Valor de Mercado (€)",
            help="Valor de Mercado Real/Oficial (Sofascore)",
            format="€%,d"
        ),
        "Valor de Desempenho (€)": st.column_config.NumberColumn(
            "Valor de Desempenho (€)",
            help="Valor estimado ajustado pelas estatísticas e desempenho do jogador na posição",
            format="€%,d"
        ),
        "Diferença de Valor (€)": st.column_config.NumberColumn(
            "Diferença de Valor (€)",
            help="Diferença absoluta: (Valor de Desempenho − Valor de Mercado)",
            format="€%,d"
        ),
        "Diferença (%)": st.column_config.NumberColumn(
            "Diferença (%)",
            help="Diferença percentual entre o Valor de Desempenho e o Valor Real",
            format="%.1f%%"
        ),
        "Chances Perdidas": st.column_config.NumberColumn(
            "Chances Perdidas",
            help="⚠️ Menor é melhor"
        ),
    }

    st.dataframe(
        show_df,
        use_container_width=True,
        height=500,
        hide_index=True,
        column_config=column_config,
        column_order=[c for c in ordered_cols if c in show_df.columns]
    )


else:  # Comparador
    st.markdown("### Motor de Similaridade & Radar Estatístico")
    st.markdown("Pesquise por **qualquer jogador** na liga para encontrar os seus **Gêmeos Estatísticos**, filtrando pelas métricas e pesos que você definir.")

    # Usamos df_full (sem filtros de sidebar) para o comparador
    df_full = load_data(data_version)

    # Criar lista formatada para busca: "Nome do Jogador (Time)"
    player_options = df_full.apply(lambda x: f"{x['player_name']} ({x['team_name']})", axis=1).tolist()
    
    target_search = st.selectbox("🔍 Pesquise pelo Jogador Alvo:", player_options, index=None, placeholder="Digite o nome do jogador...")

    if target_search:
        selected_idx = player_options.index(target_search)
        target_row = df_full.iloc[selected_idx]
        target_player = target_row['player_name']
        pos_target = target_row['position']

        # -- Agrupamento: mesma posição, ou todos se posição for nula --
        if pd.notna(pos_target) and pos_target != "N/D":
            df_pos = df_full[df_full['position'] == pos_target].copy()
            group_label = f"(posição: {pos_target})"
        else:
            df_pos = df_full.copy()
            group_label = "(toda a liga)"

        # Colunas numéricas relevantes disponíveis
        all_numeric_cols = df_pos.select_dtypes(include=['number']).columns.tolist()
        all_numeric_cols = [c for c in all_numeric_cols if c not in ['player_id']]

        # Predefinições de Métricas por Posição/Perfil
        PRESET_METRICS = {
            'Ataque / Ofensivo': ['goals', 'expectedGoals', 'GxG', 'totalShots', 'successfulDribbles', 'bigChancesMissed', 'rating'],
            'Meio-Campo / Criação': ['assists_passing', 'keyPasses_passing', 'accuratePassesPercentage_passing', 'accuratePasses_passing', 'bigChancesCreated_passing', 'successfulDribbles', 'rating'],
            'Laterais / Apoio & Defesa': ['tackles_defence', 'interceptions_defence', 'keyPasses_passing', 'assists_passing', 'accuratePassesPercentage_passing', 'successfulDribbles', 'rating'],
            'Defensivo / Zaga & Volante': ['tackles_defence', 'interceptions_defence', 'clearances_defence', 'outfielderBlocks_defence', 'totalDuelsWon_detailed', 'fouls_detailed', 'rating'],
            'Goleiro': ['saves_goalkeeping', 'cleanSheet_goalkeeping', 'goalsPrevented_goalkeeping', 'penaltySave_goalkeeping', 'highClaims_goalkeeping', 'rating']
        }

        # Determinar predefinição recomendada com base na posição do jogador alvo
        default_preset_name = 'Customizado'
        if pos_target in ['ATA', 'PE', 'PD']:
            default_preset_name = 'Ataque / Ofensivo'
        elif pos_target in ['MEI', 'MC']:
            default_preset_name = 'Meio-Campo / Criação'
        elif pos_target in ['LD', 'LE']:
            default_preset_name = 'Laterais / Apoio & Defesa'
        elif pos_target in ['ZAG', 'VOL']:
            default_preset_name = 'Defensivo / Zaga & Volante'
        elif pos_target == 'GL':
            default_preset_name = 'Goleiro'

        # UI de Configuração das Métricas e Pesos
        st.markdown("#### ⚙️ Configuração das Métricas & Pesos de Comparação")
        col_preset, col_metrics = st.columns([1, 2])
        
        with col_preset:
            preset_choice = st.selectbox(
                "Predefinição de Perfil:",
                ['Automático por Posição', 'Ataque / Ofensivo', 'Meio-Campo / Criação', 'Laterais / Apoio & Defesa', 'Defensivo / Zaga & Volante', 'Goleiro', 'Todas as Métricas'],
                index=0
            )

        # Determinar quais métricas pré-selecionar
        if preset_choice == 'Automático por Posição':
            initial_metrics = PRESET_METRICS.get(default_preset_name, all_numeric_cols)
        elif preset_choice in PRESET_METRICS:
            initial_metrics = PRESET_METRICS[preset_choice]
        elif preset_choice == 'Todas as Métricas':
            initial_metrics = all_numeric_cols
        else:
            initial_metrics = all_numeric_cols[:6]

        # Filtrar apenas métricas que realmente existem em all_numeric_cols
        initial_metrics = [c for c in initial_metrics if c in all_numeric_cols]
        if not initial_metrics:
            initial_metrics = all_numeric_cols[:6]

        # Mapeamento para nomes em Português
        col_label_map = {c: COLUMN_LABELS.get(c, c) for c in all_numeric_cols}
        label_col_map = {v: k for k, v in col_label_map.items()}

        with col_metrics:
            selected_labels = st.multiselect(
                "Métricas Utilizadas na Comparação & Radar:",
                options=list(label_col_map.keys()),
                default=[col_label_map[c] for c in initial_metrics if c in col_label_map],
                key=f"ms_{target_player}_{preset_choice}"
            )

        selected_metrics = [label_col_map[lbl] for lbl in selected_labels if lbl in label_col_map]

        if not selected_metrics:
            st.warning("Selecione pelo menos uma métrica para realizar a comparação.")
            st.stop()

        # Expansor de Ajuste de Pesos
        weights = {}
        with st.expander("⚖️ Ajustar Pesos das Métricas (Opcional)", expanded=False):
            st.caption("Aumente o peso (0.1x a 3.0x) para dar mais importância a determinada estatística no cálculo de similaridade.")
            w_cols = st.columns(min(3, len(selected_metrics)))
            for idx, m_code in enumerate(selected_metrics):
                col_target = w_cols[idx % len(w_cols)]
                lbl = col_label_map[m_code]
                weights[m_code] = col_target.slider(
                    f"Peso: {lbl}",
                    min_value=0.1, max_value=3.0, value=1.0, step=0.1, key=f"w_{m_code}"
                )

        # -- CÁLCULO DE SIMILARIDADE PONDERADA --
        # Garante que o jogador alvo está no grupo
        if target_player not in df_pos['player_name'].values:
            df_pos = df_full.copy()
            group_label = "(toda a liga)"

        df_pos = df_pos.dropna(subset=selected_metrics, how='all').reset_index(drop=True)

        if len(df_pos) > 1:
            # Ranking Percentil (0-1) para as métricas selecionadas
            pct_df = df_pos[selected_metrics].rank(pct=True).fillna(0)

            target_mask = df_pos['player_name'] == target_player
            if target_mask.sum() == 0:
                st.warning("Jogador não encontrado no grupo. Tente outro.")
                st.stop()

            target_idx = df_pos[target_mask].index[0]
            target_vector = pct_df.loc[target_idx]

            # Vetor de pesos
            weight_vector = pd.Series([weights[m] for m in selected_metrics], index=selected_metrics)

            # Distância Euclidiana Ponderada
            weighted_sq_diff = ((pct_df - target_vector) ** 2) * weight_vector
            weighted_distances = (weighted_sq_diff.sum(axis=1)) ** 0.5
            
            df_pos = df_pos.copy()
            df_pos['_distance'] = weighted_distances.values

            top_similar = (
                df_pos[df_pos['player_name'] != target_player]
                .sort_values('_distance')
                .head(3)
            )

            st.markdown(f"---\n**Comparando {target_player}** com jogadores {group_label}\n")

            if len(top_similar) == 0:
                st.info("Não foram encontrados jogadores similares suficientes.")
            else:
                rad_col, res_col = st.columns([1, 1.2])

                with rad_col:
                    fig_rad = go.Figure()

                    # 4 Cores: Alvo (Escuro), 1º (Azul), 2º (Verde), 3º (Laranja)
                    colors = ['#2b3648', '#3b82f6', '#10b981', '#f59e0b']
                    # Rótulos das métricas para o Radar (em PT-BR)
                    radar_thetas = [col_label_map[m] for m in selected_metrics]

                    for i, (_, row) in enumerate([(-1, target_row)] + list(top_similar.iterrows())[:3]):
                        if i == 0:
                            # Jogador alvo
                            r_vals = pct_df.loc[target_idx, selected_metrics].values.tolist()
                            label = f"{target_player} ({target_row['team_name']})"
                        else:
                            row_sim = top_similar.iloc[i - 1]
                            sim_idx = top_similar.index[i - 1]
                            r_vals = pct_df.loc[sim_idx, selected_metrics].values.tolist()
                            label = f"{row_sim['player_name']} ({row_sim['team_name']})"

                        fig_rad.add_trace(go.Scatterpolar(
                            r=r_vals,
                            theta=radar_thetas,
                            fill='toself',
                            name=label,
                            line_color=colors[i % len(colors)],
                            opacity=0.75
                        ))

                    fig_rad.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=True,
                        title="Radar Percentil na Liga",
                        margin=dict(t=60, l=20, r=20, b=20),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig_rad, use_container_width=True)

                with res_col:
                    st.markdown("#### 🏆 Top 3 Jogadores Mais Similares")
                    max_possible_dist = (weight_vector.sum()) ** 0.5
                    for rank, (_, row) in enumerate(top_similar.iterrows(), start=1):
                        dist = row['_distance']
                        similarity_pct = max(0.0, (1 - dist / max_possible_dist) * 100) if max_possible_dist > 0 else 0
                        shield_b64 = get_shield_b64(row['team_name'])
                        medal = ["🥇", "🥈", "🥉"][rank - 1]
                        
                        pos_str = row.get('position', 'N/D')
                        mv_str = format_market_value(row.get('market_value', 0))
                        pv_str = format_market_value(row.get('performance_market_value', 0))

                        with st.container():
                            c1, c2 = st.columns([1, 5])
                            with c1:
                                if shield_b64:
                                    st.image(shield_b64, width=48)
                            with c2:
                                st.markdown(
                                    f"{medal} **{row['player_name']}** ({pos_str})  \n"
                                    f"*{row['team_name']}* | Similaridade: **{similarity_pct:.1f}%**  \n"
                                    f"💰 Mercado: **{mv_str}** | 📈 Desempenho: **{pv_str}**"
                                )
                            st.markdown("---")

                    # Métricas chave selecionadas lado a lado
                    st.markdown("#### 📊 Comparação de Métricas Selecionadas")
                    compare_rows = [target_row] + [top_similar.iloc[i] for i in range(min(3, len(top_similar)))]
                    compare_names = [target_player] + [top_similar.iloc[i]['player_name'] for i in range(min(3, len(top_similar)))]

                    # Adicionar métricas de mercado no início da comparação se disponíveis
                    extra_m = [c for c in ['market_value', 'performance_market_value'] if c in df_full.columns and c not in selected_metrics]
                    display_metrics = extra_m + selected_metrics

                    cmp_df = pd.DataFrame(
                        {name: [row[m] if m in row.index else None for m in display_metrics]
                         for name, row in zip(compare_names, compare_rows)},
                        index=[col_label_map.get(m, m) for m in display_metrics]
                    )
                    cmp_df = cmp_df.astype(object)

                    mv_label = COLUMN_LABELS.get('market_value', 'market_value')
                    if mv_label in cmp_df.index:
                        cmp_df.loc[mv_label] = cmp_df.loc[mv_label].apply(format_market_value)

                    pv_label = COLUMN_LABELS.get('performance_market_value', 'performance_market_value')
                    if pv_label in cmp_df.index:
                        cmp_df.loc[pv_label] = cmp_df.loc[pv_label].apply(format_market_value)

                    st.dataframe(cmp_df, use_container_width=True)

        else:
            st.warning("Não há jogadores suficientes no grupo para calcular similaridade.")
