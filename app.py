import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
import os

# Configuração de Página
st.set_page_config(page_title="Brasileirão Analytics", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS (NEXUS STYLE) ---
st.markdown("""
<style>
    /* Background e Fontes */
    .stApp {
        background-color: #f4f7f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e6ed;
    }
    
    /* Ocultar header do Streamlit */
    header { visibility: hidden; }
    
    /* Estilizar os blocos (Cards) */
    div.css-1r6slb0, div.css-12oz5g7 {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e9f0;
        margin-bottom: 20px;
    }

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        color: #2b3648;
        font-weight: 700;
        font-size: 28px;
    }
    [data-testid="stMetricLabel"] {
        color: #7a869a;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Titles */
    h1, h2, h3 {
        color: #1a202c;
    }
    
    .nexus-title {
        font-size: 24px;
        font-weight: 700;
        color: #2b3648;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

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

df = load_data()

# Se não houver dados, para execução
if df.empty:
    st.stop()

# --- SIDEBAR FILTROS ---
st.sidebar.image("brasileirao_logo.png", width=150)
st.sidebar.markdown("## Filtros")

teams = sorted(df['team_name'].dropna().unique())
selected_teams = st.sidebar.multiselect("Time", teams, default=[])

positions = sorted(df['position'].dropna().unique())
default_positions = [p for p in ["F", "M"] if p in positions]
selected_positions = st.sidebar.multiselect("Posição", positions, default=default_positions)

st.sidebar.markdown("### Métricas (Mínimos)")
min_matches = st.sidebar.slider("Mínimo Partidas Jogadas", 0, 38, 5)

if 'appearances' in df.columns:
    df = df[df['appearances'] >= min_matches]

if selected_teams:
    df = df[df['team_name'].isin(selected_teams)]
if selected_positions:
    df = df[df['position'].isin(selected_positions)]

# --- HEADER ---
st.markdown("<div class='nexus-title'>Dashboard - Performance de Jogadores</div>", unsafe_allow_html=True)

# --- KPIs ROW ---
col1, col2, col3, col4 = st.columns(4)

top_scorer = df.loc[df['goals'].idxmax()] if not df.empty and 'goals' in df.columns else None
top_gxg = df.loc[df['GxG'].idxmax()] if not df.empty and 'GxG' in df.columns else None
total_goals = df['goals'].sum() if 'goals' in df.columns else 0
total_xg = df['expectedGoals'].sum() if 'expectedGoals' in df.columns else 0

with col1:
    st.metric("Total Goals (Filtered)", f"{total_goals:,.0f}")
with col2:
    st.metric("Total xG (Filtered)", f"{total_xg:,.2f}")
with col3:
    if top_scorer is not None:
        st.metric("Top Scorer", f"{top_scorer['player_name']} ({int(top_scorer['goals'])})")
    else:
        st.metric("Top Scorer", "-")
with col4:
    if top_gxg is not None:
        st.metric("Maior Overperformer (GxG)", f"{top_gxg['player_name']} (+{top_gxg['GxG']:.2f})")
    else:
        st.metric("Maior Overperformer", "-")

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
            plot_bgcolor='white', margin=dict(t=10, l=10, r=10, b=10),
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
            plot_bgcolor='white', margin=dict(t=10, l=10, r=10, b=10),
            xaxis_title="GxG", yaxis_title="Frequency", showlegend=False
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig_hist, use_container_width=True)

# --- TABLE ROW (AgGrid) ---
st.markdown("### Detalhamento Interativo de Jogadores")

# Selecionar colunas relevantes para a tabela
cols_to_show = ['player_name', 'team_name', 'position']
if 'goals' in df.columns:
    cols_to_show.extend(['goals', 'expectedGoals', 'GxG', 'assists', 'matchesStarted'])

# Pegar as que existem
show_df = df[[c for c in cols_to_show if c in df.columns]].copy()

# Preencher NaNs que quebram o AgGrid (como a coluna position inteira vazia)
for col in show_df.columns:
    if show_df[col].isnull().all():
        show_df[col] = "N/D"
    elif show_df[col].dtype == 'object' or show_df[col].dtype.name == 'category':
        show_df[col] = show_df[col].fillna("N/D")
    else:
        show_df[col] = show_df[col].fillna(0)

if 'GxG' in show_df.columns:
    show_df['GxG'] = show_df['GxG'].round(2)
if 'expectedGoals' in show_df.columns:
    show_df['expectedGoals'] = show_df['expectedGoals'].round(2)

gb = GridOptionsBuilder.from_dataframe(show_df)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
gb.configure_default_column(sortable=True, filter=True, resizable=True)
gb.configure_column("player_name", pinned='left')
if 'GxG' in show_df.columns:
    # Destacar GxG
    gb.configure_column("GxG", type=["numericColumn", "numberColumnFilter"], 
                        cellStyle={'fontWeight': 'bold'}, sort='desc')

gridOptions = gb.build()

AgGrid(
    show_df,
    gridOptions=gridOptions,
    enable_enterprise_modules=False,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    theme='balham',
    height=500
)
