# Dashboard de Performance - Brasileirão 2026 (Sofascore)

Este plano detalha a construção do pipeline de dados e da dashboard Streamlit interativa com foco na análise de performance dos jogadores do Brasileirão 2026, com uma estética premium inspirada em layouts SaaS modernos ("Nexus").

## User Review Required

> [!IMPORTANT]
> **Estratégia de Scraping**: Sofascore utiliza proteção contra bots e não possui API pública oficial. 
> Propomos utilizar o **Playwright** para interceptar as requisições de rede (XHR/Fetch) que trazem o JSON puro com os dados de "Player Statistics". Isso é mais escalável do que tentar ler o HTML (já que o site tem paginação e renderiza dinamicamente).
> Você aprova começar com Playwright + Python? E você possui o `Node.js` e/ou o `playwright` instalado no seu ambiente? (Nós cuidaremos da instalação via `pip` durante a execução, apenas precisamos checar se é compatível).

> [!WARNING]
> **Atualização de Dados**: Propomos criar um botão "Atualizar Dados (Scrape)" diretamente oculto/visível na interface ou como um script via terminal `python update_data.py`. Sendo um script na sua máquina local, o script processará e atualizará a base localmente.

## Proposed Changes

---

### Pipeline de Dados e ETL (Scraper)

A primeira etapa garante extração e preparação segura dos dados de Attack, Defense, Passing e Goalkeeping.

#### [NEW] `scraper.py`
- Utilizará `playwright` acoplado ao Python para abrir a URL do Brasileirão Betano (Player Stats).
- Capturará em background os JSONs retornados pela API não ofícial durante a navegação das páginas.
- Salvará o snapshot raw de cada categoria e cruzará em um único DataFrame usando nome de jogador e ID.

#### [NEW] `process_data.py`
- Lerá os `raw JSON/CSV`.
- Tratará inconsistências, formatações e merge de tabelas.
- **Transformação**: Criação da métrica derivada `GxG = Goals - Expected Goals (xG)`.
- **Exportação Final**: Consolidação em um arquivo de alta performance `data/dataset_brasileirao_2026.parquet`.

---

### Dashboard Streamlit

A Dashboard será construída utilizando Streamlit aliada a `Plotly` para gráficos ricos e estilos customizados via CSS para termos o "Wow Factor".

#### [NEW] `app.py`
- Script mestre que executa a aplicação `streamlit run app.py`.
- Lida com a barra lateral de filtros interativos (Time, Posição, filtro de Goals/xG/GxG usando Sliders).
- Apresenta as visões: Histograma GxG, Dispersão de xG vs Goals e as Tabelas Rankeadas no layout em colunas (imitando o layout Nexus).

#### [NEW] `assets/styles.css`
- Responsável por aplicar todo o CSS e modificar o Streamlit cru para a estética Premium Nexus (bordas arredondadas, sombras leves, dark/light tones dependendo da escolha, mas com as cores vibrantes apontadas).

---

## Open Questions

1. **Gráficos Específicos**: Você gostaria de alguma cor específica para a série de GxG (ex: Verde para performance positiva GxG > 0, Vermelho para negativa)?
2. **Ambiente**: Posso configurar um ambiente virtual (ex: `venv`) no diretório do projeto para isolar as dependências (pandas, streamlit, playwright, plotly)?
3. **Bibliotecas de UI Adicionais**: Podemos utilizar `streamlit-aggrid` ou `st-aggrid` para tabelas avançadas (ordenação e paginação fluidas) em vez da tabela nativa do Streamlit. Alguma objeção?

## Verification Plan

### Automated Tests
- Executaremos um "Dry Run" do scraper extraindo até 2 páginas por categoria para garantir que a proteção do Cloudflare/Sofascore não derrube nossa automação.
- Validaremos se a métrica `GxG` é calculada corretamente no Pandas.

### Manual Verification
- Renderização visual do Streamlit, comparando com a imagem de referência Nexus em que botões, cartões de KPI e gráficos devem seguir o padrão estético de Web App moderno.
