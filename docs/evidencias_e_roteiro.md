# Evidências e roteiro de demonstração

## Evidências geradas pelo protótipo

1. O painel mostra o total de sessões, energia entregue, usuários ativos, receita estimada e interrupções.
2. A tabela de faturas detalha consumo, energia, infraestrutura e total de cada usuário.
3. O cartão de IA mostra previsão por horário; a seção de anomalias destaca sessões atípicas e interrompidas.
4. O formulário valida um RFID e registra uma nova sessão via `POST /api/sessoes`; em seguida, os totais e faturas são recalculados.

## Roteiro de vídeo (até 5 minutos)

1. Contexto (30 s): apresente o problema do carregador compartilhado e a proposta EV ChargeOps.
2. Arquitetura (40 s): explique RFID/SEMS no cenário real, API Python, dados simulados e painel.
3. Rateio (60 s): abra as faturas e apresente a fórmula de cobrança individual.
4. IA (60 s): mostre a previsão por horário e as anomalias; destaque que o gestor valida os alertas.
5. Demonstração (90 s): cadastre uma sessão com `RFID-1001`, energia 10,5 kWh e potência 7 kW. Mostre o retorno e os valores atualizados.
6. Limitações e próximos passos (20 s): cite integração SEMS, PostgreSQL, autenticação e testes com dados reais.
