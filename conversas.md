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
- [x] **Sidebar**: Remover logo redundante e definir todas as posições como selecionadas por default.
- [x] **Registro**: Atualizar o arquivo `conversas.md` para documentar o progresso.

---
*Este arquivo será atualizado automaticamente a cada nova solicitação.*
