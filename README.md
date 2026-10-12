# EV ChargeOps — Sprint 02

Protótipo funcional para gestão de recargas compartilhadas do carregador GoodWe HCA G2 no Energy Innovation Lab. A solução implementa registro autenticado por RFID, cálculo de consumo individual, rateio mensal e inteligência aplicada ao fluxo operacional.

O projeto segue as decisões registradas na [Sprint 01](https://github.com/timsleo/enterprise_challenge): rateio por kWh real, taxa de infraestrutura dividida somente por usuários ativos, previsão de demanda e detecção de anomalias.

## O que foi implementado

- API em Python/FastAPI para consultar a operação e registrar sessões simuladas;
- validação do RFID contra o cadastro de usuários ativos;
- persistência local em JSON para tornar a demonstração reproduzível;
- faturamento por usuário com a fórmula `kWh × tarifa + infraestrutura / usuários ativos`;
- previsão de demanda por faixa horária com regressão linear;
- detecção de anomalias com Isolation Forest, usando energia, duração e potência média;
- painel web responsivo para gestor, com indicadores, faturas, alertas e formulário de sessão.

## Arquitetura

```text
Painel web (HTML/CSS/JS)
          │ HTTP/JSON
FastAPI — regras de negócio — modelos de IA
          │
JSON simulado (usuários, sessões e configurações)
```

No cenário real, a origem das sessões seria a API SEMS Portal/GoodWe com autenticação RFID no carregador. Nesta Sprint, a coleta externa foi simulada por JSON para não depender de credenciais, dispositivo físico ou endpoints não documentados.

## Como executar no Windows

### 1. Instale o Python

Instale o Python 3.10 ou superior em [python.org/downloads](https://www.python.org/downloads/) e, durante a instalação, marque **Add Python to PATH**. Depois, abra o PowerShell e confira:

```powershell
python --version
```

Se o comando não for reconhecido, feche e abra o PowerShell novamente ou reinstale o Python com essa opção marcada.

### 2. Abra a pasta do projeto

Extraia o ZIP e, no PowerShell, entre na pasta extraída. Exemplo:

```powershell
cd "C:\Users\SEU_USUARIO\Downloads\EV_ChargeOps_Sprint02"
```

### 3. Crie e ative o ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a ativação, execute apenas nesta janela:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. Instale as dependências

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Inicie o sistema

```powershell
uvicorn app.main:app --reload
```

Mantenha esse terminal aberto e abra **http://127.0.0.1:8000** no navegador. A documentação dos endpoints está em **http://127.0.0.1:8000/docs**. Para encerrar, volte ao terminal e pressione `Ctrl + C`.

### 6. Demonstração rápida

1. Na tela **Operação e rateio**, confira as faturas calculadas.
2. Clique em **Indicadores** para ver consumo médio, taxa de interrupção, previsão e anomalias.
3. Volte à primeira tela, cadastre uma sessão usando `RFID-1001` e clique em **Registrar e recalcular**.
4. Atualize a tela **Indicadores** para observar os valores recalculados.

## Dados de demonstração

O diretório `data/` contém quatro usuários e 16 sessões do período 2026-06. Há uma sessão interrompida e uma sessão de consumo elevado para demonstrar o módulo de revisão. A tarifa simulada é R$ 0,98/kWh e o custo mensal de infraestrutura é R$ 50,00.

Para demonstrar: abra o painel, apresente os cards e faturas, mostre as previsões/alertas de IA e registre uma nova sessão com o RFID `RFID-1001`. O painel atualiza os valores e a nova sessão passa a integrar a cobrança.

## Decisões técnicas e desvios justificados

A Sprint 01 previa PostgreSQL, React e integração com SEMS Portal. O protótipo usa arquivos JSON, HTML/CSS/JavaScript nativos e dados simulados. A troca reduz a complexidade de implantação para a entrega acadêmica, preserva as regras de negócio e torna a demonstração executável sem banco, chaves, hardware ou integração externa. FastAPI, Python e scikit-learn foram mantidos, portanto a lógica pode ser migrada para PostgreSQL e um front-end React sem reescrever os serviços principais.

O modelo de IA é deliberadamente simples: não é usado para aprovar cobrança nem bloquear usuários. Ele gera recomendação de demanda e alerta de anomalia para validação do gestor. Isso evita transformar um resultado estatístico em decisão automática irreversível.

## Estrutura

```text
app/             API e regras de negócio
data/            base simulada
static/          painel web
docs/            roteiro de evidências
requirements.txt dependências
link_repositorio.txt entrega textual solicitada
```
