# 📊 Prompt — Dashboard de Performance de Jogadores (Brasileirão 2026)

## 🎯 Objetivo

Construir uma **dashboard interativa** para análise da performance de jogadores da Série A do Campeonato Brasileiro 2026 (**Brasileirão Betano**), permitindo:

- Exploração visual dos dados
- Filtragem dinâmica
- Comparação entre jogadores
- Análises baseadas em múltiplas métricas

---

## 🌐 Fonte de Dados

Os dados estão disponíveis em:

- Website: https://www.sofascore.com  
- Navegação:
  - Football → Top Competitions → **Brasileirão Betano**
  - Acessar a aba **Stats (Player Stats)**

---

## 📥 Coleta de Dados (ETL)

### 🔴 Requisito crítico

Os dados devem ser **extraídos previamente e armazenados localmente** antes da construção da dashboard.

### 📊 Escopo da coleta

Coletar dados completos de jogadores nas seguintes abas:

- Attack
- Defense
- Passing
- Goalkeeping

### 📄 Paginação

- Cada aba apresenta aproximadamente:
  - **20 jogadores por página**
  - **~28 páginas no total**

➡️ Implementar scraping que percorra **todas as páginas automaticamente**

---

## 🧮 Transformações de Dados

### Nova métrica derivada

Criar uma nova coluna:

- **GxG = Goals − Expected Goals (xG)**

### Requisitos

- Manter todas as colunas originais da aba **Attack**
- Integrar dados das demais abas (Defense, Passing, Goalkeeping)
- Garantir consistência por jogador (join correto entre tabelas)

---

## 💾 Armazenamento

Sugestões:

- CSV ou Parquet (preferível para performance)
- Estrutura recomendada:
  - dataset unificado por jogador
  - chave única: nome + time (ou ID se disponível)

---

## 🔄 Atualização dos Dados

Os dados são atualizados a cada rodada.

### Propor solução automatizada:

- Opção 1: Script manual executável (ex: `update_data.py`)
- Opção 2: Atualização automática:
  - agendamento diário (cron/job scheduler)
- Opção 3: Botão dentro da dashboard:
  - "Atualizar dados"

### Requisito

- Evitar duplicação de dados
- Permitir atualização incremental (se possível)

---

## 📊 Dashboard — Funcionalidades

### 📌 Visualizações obrigatórias

1. **Tabela interativa de jogadores**
   - Incluindo:
     - Todas as colunas da aba Attack
     - Nova coluna **GxG**
   - Com:
     - Ordenação
     - Busca
     - Paginação

2. **Filtros dinâmicos**
   - Time
   - Posição
   - Métricas (ex: Goals, xG, GxG)
   - Faixas numéricas (sliders)

3. **Gráficos**
   - Scatter plot:
     - xG vs Goals
     - Destaque para GxG (over/underperformance)
   - Bar charts:
     - Top jogadores por métricas
   - Distribuições:
     - Histogramas (Goals, xG, GxG)
   - Comparação entre jogadores

4. **Integração multi-aba**
   - Permitir alternar entre:
     - Attack / Defense / Passing / Goalkeeping
   - Ou visão consolidada

---

## 🎨 Layout e Design

- Utilizar a imagem de referência fornecida posteriormente
- Priorizar:
  - Clareza visual
  - Responsividade
  - Organização por seções
- Sugestão:
  - Sidebar com filtros
  - Área principal com gráficos + tabela

---

## ⚙️ Stack Sugerida

- Python
- Streamlit (preferencial)
- Pandas
- Altair ou Plotly

---

## 🚀 Entregáveis Esperados

1. Script de coleta de dados (scraper)
2. Pipeline de transformação
3. Dataset final consolidado
4. Dashboard funcional
5. Mecanismo de atualização de dados

---

## ⚠️ Observações Importantes

- Garantir robustez contra mudanças na estrutura do site
- Tratar possíveis inconsistências ou dados faltantes
- Evitar bloqueios (rate limit, scraping ético)

---

## 📎 Próximo passo

Vou fornecer uma **imagem de referência da dashboard** que deve ser usada como base para o layout.
