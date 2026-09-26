# Histórico de Solicitações - Brasileirão Performance Dashboard

Este arquivo registra o desenvolvimento do projeto através das solicitações do usuário.

## 📅 Fase Inicial: Configuração e Problemas de Deploy
- [x] Adicionar instruções iniciais ao arquivo `update.txt`.
- [x] Esclarecer o funcionamento dos IDs de URL no Streamlit.
- [x] Resolver problema onde a aba de comparação não aparecia na versão mobile.
- [x] Corrigir falha de atualização/deploy do Streamlit App.

## 📊 Fase de Evolução: Dados e Localização
- [x] **Tradução da Interface**: Renomear colunas técnicas para Português (Gols, xG, Chances Perdidas, Dribles, Finalizações, Nota Média, etc.).
- [x] **Ajuste de KPIs**: Garantir que 'Chances Perdidas' seja contabilizado como métrica negativa (menor é melhor).
- [x] **Scraping de Posições**: Adicionar a posição de cada jogador ao dashboard.
- [x] **Motor de Similaridade**: Permitir pesquisa de jogadores sem a restrição de filtrar por time primeiro.

## 🛡️ Fase de Refinamento: Defesa e Detalhes
- [x] **Coleta Sofascore**: Realizar novo scrape para incluir estatísticas defensivas (Desarmes, Interceptações, Cortes).
- [x] **Posições Brasileiras**: Mapear posições detalhadas para as siglas nacionais (GL, LD, ZAG, LE, VOL, MC, MEI, PE, ATA, PD).
- [x] **Valor de Mercado**: Integrar valores de mercado do Sofascore em euro (€) com destaque em KPIs e na tabela.

## 🛠️ Fase de Estabilização e Mobile
- [x] **Correção de Erros**: Resolver `SyntaxError` no `app.py` causado por indentação.
- [x] **Layout da Tabela**: Mover coluna de Valor de Mercado para logo após a Posição.
- [x] **Formatação**: Converter valores numéricos grandes para formato amigável (ex: €1.5M, €500k).
- [x] **Dark Mode Mobile**: Corrigir CSS para que o dashboard siga o tema (Escuro/Claro) do sistema do usuário.
- [x] **Deploy Production**: Corrigir erro `FileNotFoundError: system` causado por configuração de tema inválida no servidor.
- [x] **Acesso Mobile**: Restaurar visibilidade do botão de menu lateral (hambúrguer) no celular.
- [x] **Ordenação de Valores**: Corrigir a ordenação da coluna de mercado para ser numérica (removendo a formatação de string que quebrava o sort).
- [x] **Identidade Visual**: Adicionar a imagem `farroupilha.jpeg` ao lado do logo do Brasileirão no topo.
- [x] **Comparador**: Incluir a métrica de Valor de Mercado na tabela de comparação de métricas-chave e formatar com o padrão (€M/k).
## 🔄 Fase de Manutenção & Recursos Avançados
- [x] **Correção do Scraper**: Atualizado o `scraper.py` para utilizar o novo endpoint `www.sofascore.com/api/v1/...` (em substituição ao endpoint legado `api.sofascore.com` bloqueado com HTTP 403) e ajustada a navegação do Playwright para evitar a checagem de robôs / captcha do Cloudflare.
- [x] **Atualização de Dados (ETL)**: Reexecutado o scraper com sucesso (680+ jogadores em todas as categorias) e regerado o `data/dataset_brasileirao_2026.parquet` via `process_data.py`.
- [x] **Comparador Personalizável & Pesos**: Adicionada a seleção de predefinições de métricas por posição (Ataque, Meio, Defesa, Goleiro), seleção dinâmica de estatísticas no multiselect e controle de pesos individuais (0.1x a 3.0x) para o cálculo da distância de similaridade e geração do gráfico de radar.
- [x] **Valor de Desempenho (€) & Diferenças**: Criado modelo de precificação ajustado por desempenho (`Valor de Desempenho (€)`) que cruza o valor de mercado real com o percentil de rendimento estatístico na posição, ponderado pelo número de partidas jogadas (fator de amostragem/consistência), adicionando as colunas `Diferença de Valor (€)` e `Diferença (%)` na tabela do Detalhamento Interativo.
- [x] **Estatísticas Específicas de Goleiro**: Coletadas e integradas 7 métricas exclusivas da meta (`Defesas`, `Jogos sem Sofrer Gol`, `Gols Evitados (xG)`, `Gols Sofridos`, `Pênaltis Defendidos`, `Bolas Altas Agarradas` e `Socos na Bola`), atualizando o perfil de predefinição do comparador e a valoração por posição.
- [x] **Apresentação Beamer (LaTeX)**: Gerada e compilada a apresentação em PDF (`apresentacao_metricas.pdf`) de 11 slides com a documentação completa de todas as métricas, modelo de valoração e algoritmos.
- [x] **Separacão de Laterais e Zagueiros**: Criado um perfil estatístico e predefinição dedicados para Laterais (`LD` e `LE`: `Desarmes`, `Interceptações`, `Passes Chave`, `Conversão de Passe (%)`, `Dribles` e `Nota Média`), desvinculando-os do perfil estritamente defensivo dos Zagueiros (`ZAG`) no modelo de valoração de mercado e nas predefinições do comparador.
- [x] **Filtros de Idade e Valor de Mercado**: Adicionado o controle de faixa de idade e campos numéricos digitáveis (`Mín (€M)` e `Máx (€M)`) na barra lateral para filtragem direta de valores de mercado em milhões de euros.

---
*Este arquivo será atualizado automaticamente a cada nova solicitação.*
