import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
import numpy as np

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
    'market_value':                    'Valor de Mercado (€)',
    'appearances_detailed':            'Partidas',
    'yellowCards_detailed':            'Cartões Amarelos',
    'redCards_detailed':               'Cartões Vermelhos',
    'totalDuelsWon_detailed':          'Duelos Ganhos',
    'fouls_detailed':                  'Faltas Cometidas'
}

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
@st.cache_data(ttl=3600)
def load_data():
    path = "data/dataset_brasileirao_2026.parquet"
    if os.path.exists(path):
        df = pd.read_parquet(path)
        return df
    else:
        st.warning(f"Extrato local ({path}) não encontrado. Execute o web scraper primeiro!")
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

df = load_data()

# --- SIDEBAR FILTROS ---
st.sidebar.image("brasileirao_logo.png", width=150)
st.sidebar.markdown("## Filtros")

teams = sorted(df['team_name'].dropna().unique())
selected_teams = st.sidebar.multiselect("Time", teams, default=[])

positions = sorted(df['position'].dropna().unique())
default_positions = [p for p in ["ATA", "PE", "PD", "MEI"] if p in positions]
selected_positions = st.sidebar.multiselect("Posição", positions, default=default_positions)

st.sidebar.markdown("### Métricas (Mínimos)")
min_matches = st.sidebar.slider("Mínimo Partidas Jogadas", 0, 38, 5)

if 'appearances_detailed' in df.columns:
    df = df[df['appearances_detailed'] >= min_matches]
elif 'appearances' in df.columns:
    df = df[df['appearances'] >= min_matches]

if selected_teams:
    df = df[df['team_name'].isin(selected_teams)]
if selected_positions:
    df = df[df['position'].isin(selected_positions)]

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
            # Preparando df para plot, removendo nulos de xG e Goals e os que não jogaram nada no ataque
            plot_df = df.dropna(subset=['goals', 'expectedGoals', 'GxG']).copy()
            plot_df = plot_df[(plot_df['goals'] > 0) | (plot_df['expectedGoals'] > 0)]

            # Cor Azul para positivo (G > xG) e vermelho para negativo (G < xG) conforme pedido do usuário
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
            max_val = max(plot_df['expectedGoals'].max(), plot_df['goals'].max()) * 1.1
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
        # Se for market_value, garantir que é numérico antes do config
        if col == "market_value":
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

    # Escudo sempre primeiro, depois Jogador, Time, Posição e Valor de Mercado
    fixed_order = ["Escudo", "Jogador", "Time", "Posição", "Valor de Mercado (€)", "Gols", "xG", "GxG"]
    ordered_cols = [c for c in fixed_order if c in show_df.columns] \
                   + [c for c in show_df.columns if c not in fixed_order]

    column_config = {
        "Escudo": st.column_config.ImageColumn("Time", help="Escudo Oficial do Clube"),
        "Valor de Mercado (€)": st.column_config.NumberColumn(
            "Valor de Mercado (€)",
            help="Valor estimado do jogador",
            format="€%,d"
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
    st.markdown("Pesquise por **qualquer jogador** na liga. O algoritmo encontrará os **Gêmeos Estatísticos** desse atleta, usando Distância Euclidiana nos percentis de todas as métricas.")

    # Usamos df_full (sem filtros de sidebar) para o comparador
    df_full = load_data()

    # Criar lista formatada para busca: "Nome do Jogador (Time)"
    player_options = df_full.apply(lambda x: f"{x['player_name']} ({x['team_name']})", axis=1).tolist()
    player_names = df_full['player_name'].tolist()
    
    target_search = st.selectbox("🔍 Pesquise pelo Jogador Alvo:", player_options, index=None, placeholder="Digite o nome do jogador...")

    if target_search:
        # Extrair o nome do jogador da string formatada
        # Vamos usar o índice da opção selecionada para pegar a linha exata do df
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

        # Colunas numéricas relevantes para o cálculo
        numeric_cols = df_pos.select_dtypes(include=['number']).columns.tolist()
        numeric_cols = [c for c in numeric_cols if c not in ['player_id']]

        # Garante que o jogador alvo está no grupo
        if target_player not in df_pos['player_name'].values:
            df_pos = df_full.copy()
            group_label = "(toda a liga)"

        # Remove linhas onde TODOS os numéricos são NaN
        df_pos = df_pos.dropna(subset=numeric_cols, how='all').reset_index(drop=True)

        if len(df_pos) > 1 and len(numeric_cols) > 0:
            # Percentil ranking (0–1)
            pct_df = df_pos[numeric_cols].rank(pct=True).fillna(0)

            target_mask = df_pos['player_name'] == target_player
            if target_mask.sum() == 0:
                st.warning("Jogador não encontrado no grupo. Tente outro.")
                st.stop()

            target_idx = df_pos[target_mask].index[0]
            target_vector = pct_df.loc[target_idx]

            # Distância Euclidiana
            distances = ((pct_df - target_vector) ** 2).sum(axis=1) ** 0.5
            df_pos = df_pos.copy()
            df_pos['_distance'] = distances.values

            top_similar = (
                df_pos[df_pos['player_name'] != target_player]
                .sort_values('_distance')
                .head(3)
            )

            st.markdown(f"---\n**Comparando {target_player}** com jogadores {group_label}\n")

            if len(top_similar) == 0:
                st.info("Não foram encontrados jogadores similares suficientes.")
            else:
                sim_1 = top_similar.iloc[0]
                sim_1_idx = top_similar.index[0]

                rad_col, res_col = st.columns([1, 1.2])

                with rad_col:
                    focal_categories = [
                        'goals', 'expectedGoals', 'GxG', 'rating',
                        'totalShots', 'successfulDribbles',
                        'assists_passing', 'keyPasses_passing'
                    ]
                    focal_categories = [c for c in focal_categories if c in numeric_cols]
                    if len(focal_categories) < 3:
                        focal_categories = numeric_cols[:6]

                    fig_rad = go.Figure()

                    colors = ['#2b3648', '#3b82f6', '#10b981']
                    for i, (_, row) in enumerate([(-1, target_row)] + list(top_similar.iterrows())[:2]):
                        if i == 0:
                            # Jogador alvo
                            r_vals = pct_df.loc[target_idx, focal_categories].values.tolist()
                            label = f"{target_player} ({target_row['team_name']})"
                        else:
                            row = top_similar.iloc[i - 1]
                            r_vals = pct_df.loc[top_similar.index[i - 1], focal_categories].values.tolist()
                            label = f"{row['player_name']} ({row['team_name']})"

                        fig_rad.add_trace(go.Scatterpolar(
                            r=r_vals,
                            theta=focal_categories,
                            fill='toself',
                            name=label,
                            line_color=colors[i],
                            opacity=0.75
                        ))

                    fig_rad.update_layout(
                        polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
                        showlegend=True,
                        title="Radar Percentil na Liga",
                        margin=dict(t=60, l=20, r=20, b=20),
                        legend=dict(orientation="v", x=1.05)
                    )
                    st.plotly_chart(fig_rad, use_container_width=True)

                with res_col:
                    st.markdown("#### 🏆 Top 3 Jogadores Mais Similares")
                    for rank, (_, row) in enumerate(top_similar.iterrows(), start=1):
                        dist = row['_distance']
                        # Normaliza a distância para 0-100% de forma mais realista
                        max_possible_dist = (len(numeric_cols)) ** 0.5
                        similarity_pct = max(0.0, (1 - dist / max_possible_dist) * 100)
                        shield_b64 = get_shield_b64(row['team_name'])
                        medal = ["🥇", "🥈", "🥉"][rank - 1]

                        with st.container():
                            c1, c2 = st.columns([1, 5])
                            with c1:
                                if shield_b64:
                                    st.image(shield_b64, width=48)
                            with c2:
                                st.markdown(
                                    f"{medal} **{row['player_name']}**  \n"
                                    f"*{row['team_name']}*  \n"
                                    f"Similaridade: **{similarity_pct:.1f}%**"
                                )
                            st.markdown("---")

                    # Métricas chave lado a lado
                    st.markdown("#### 📊 Comparação de Métricas-Chave")
                    key_metrics = [c for c in ['market_value', 'goals', 'expectedGoals', 'GxG', 'rating', 'assists_passing'] if c in df_full.columns]
                    compare_rows = [target_row] + [top_similar.iloc[i] for i in range(min(2, len(top_similar)))]
                    compare_names = [target_player] + [top_similar.iloc[i]['player_name'] for i in range(min(2, len(top_similar)))]

                    # Usar rótulos para o comparador final
                    cmp_df = pd.DataFrame(
                        {name: [row[m] if m in row.index else None for m in key_metrics]
                         for name, row in zip(compare_names, compare_rows)},
                        index=[COLUMN_LABELS.get(m, m) for m in key_metrics]
                    )
                    st.dataframe(cmp_df.round(2), use_container_width=True)

        else:
            st.warning("Não há jogadores suficientes no grupo para calcular similaridade.")
