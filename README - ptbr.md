# 🪙 BTC-RPC-Data

[![BTC Data Updater](https://github.com/m-marqx/BTC-RPC-Data/actions/workflows/btc_data_update.yml/badge.svg)](https://github.com/m-marqx/BTC-RPC-Data/actions/workflows/btc_data_update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

> **Dados on-chain do Bitcoin de graça, sem precisar vender um rim para rodar um full node.**

---

## 📑 Sumário

| Seção | Descrição |
|-------|-----------|
| [📖 A História](#-a-história-como-essa-loucura-começou) | Como um problema de 0.5TB virou uma solução gratuita |
| [✨ Funcionalidades](#-funcionalidades) | O que este repositório oferece |
| [🐳 Uso com Docker](#-obtendo-dados-com-docker) | Obtenha dados em segundos com Docker |
| [🔧 Setup Local](#-desenvolvimento-local) | Rode o projeto localmente |
| [📊 Estrutura dos Dados](#-estrutura-dos-dados) | O que tem dentro da pasta data |
| [🤝 Contribuindo](#-contribuindo) | Ajude a melhorar este projeto |

---

## 📖 A História: Como Essa Loucura Começou

Era uma vez um desenvolvedor (eu) que teve uma ideia brilhante: *"Eu quero dados on-chain do Bitcoin! Taxa média de transação, quantidade de transações, fee rate... tudo!"*

Simples, né? É só rodar um full node e... **espera, o quê?**

### 🎭 Ato I: A Dura Realidade

Para obter dados on-chain, eu precisaria rodar um full node do Bitcoin na minha máquina. Tranquilo... até eu descobrir que um full node pesa **mais de 0.5TB** hoje em dia. Olhei para meus discos rígidos. Meus discos rígidos olharam de volta para mim. Nós dois sabíamos que não tinha espaço. Eu teria que deletar metade da minha vida para *talvez* conseguir encaixar.

### 🎭 Ato II: A Fantasia da Cloud

*"Aha!"* pensei, *"Vou usar a cloud!"*

Aí eu vi os preços. Rodar um full node em infraestrutura cloud custaria uma pequena fortuna. Para um pet project. Um *pet project*. Minha carteira começou a chorar antes mesmo de eu terminar o cálculo.

### 🎭 Ato III: A Jornada do Herói (Vulgo Pesquisa no Google)

Depois de muita pesquisa e uma quantidade insalubre de determinação, eu encontrei: **QuickNode API**.

Dava para extrair todas as informações que eu queria, bloco a bloco. Seria lento? Sim. Funcionaria? Também sim. E às vezes na vida, *"funciona"* é tudo que você precisa.

### 🎭 Ato IV: A Saga da Automação

Agora eu tinha outro problema: manter esses dados atualizados. Três opções surgiram:

| Opção | Descrição | Veredito |
|-------|-----------|----------|
| **A** | Pagar um serviço de hospedagem para rodar o script Python | 💸 Dinheiro? O que é isso? |
| **B** | Deixar minha máquina rodando 24/7 | 🔥 Minha conta de luz disse não |
| **C** | Usar GitHub Actions com cron job a cada 30 minutos | 🎉 **DE GRAÇA!** |

Se você já deu uma olhada no [arquivo de workflow](.github/workflows/btc_data_update.yml), você já sabe que eu escolhi a Opção C. O GitHub Actions roda o script a cada 30 minutos, faz commit dos novos dados e ainda builda uma imagem Docker fresquinha. Tudo pelo baixo preço de *absolutamente nada*.

### 🎭 Epílogo

E foi assim que este repositório nasceu: da necessidade, criatividade e uma forte recusa em pagar por coisas que poderiam ser de graça.

---

## ✨ Funcionalidades

- 📈 **Estatísticas de blocos on-chain do Bitcoin** - Taxas de transação, contagens, tamanhos e mais
- 🔄 **Atualizado automaticamente a cada 30 minutos** - Via cron job do GitHub Actions
- 🐳 **Suporte a Docker** - Baixe a imagem e tenha acesso instantâneo aos dados
- 📦 **Formato Parquet** - Eficiente, comprimido e amigável ao pandas
- 💰 **100% Gratuito** - Sem full node, sem custos de cloud, sem lágrimas

---

## 🐳 Obtendo Dados com Docker

A maneira mais fácil de obter os dados é através da nossa imagem Docker. Nenhuma configuração necessária!

### Início Rápido

```bash
# Baixe a imagem mais recente
docker pull ghcr.io/m-marqx/btc-rpc:latest

# Execute o shell Python interativo com o explorador de dados
docker run -it ghcr.io/m-marqx/btc-rpc:latest
```

### Dentro do Container

Uma vez dentro, você terá acesso a funções auxiliares:

```python
# Liste todos os arquivos parquet disponíveis
list_data_files()

# Carregue as estatísticas de blocos on-chain
df = load_onchain()
print(df.head())

# Veja as colunas disponíveis
print(df.columns.tolist())
```

### Extrair Dados para Máquina Local

Quer os arquivos na sua máquina local? Use o docker-compose:

```bash
# Clone o repositório
git clone https://github.com/m-marqx/BTC-RPC-Data.git
cd BTC-RPC-Data

# Extraia os dados para a pasta ./output
docker compose --profile extract up
```

Ou copie manualmente de um container em execução:

```bash
# Execute o container em background
docker run -d --name btc-data ghcr.io/m-marqx/btc-rpc:latest sleep infinity

# Copie os dados para pasta local
docker cp btc-data:/app/data ./dados-locais

# Limpe
docker rm -f btc-data
```

### Usando os Dados nos Seus Projetos

```python
import pandas as pd

# Se você extraiu os dados localmente
df = pd.read_parquet("./dados-locais/onchain/BTC/block_stats_fragments")

# Analise à vontade!
print(f"Total de blocos: {len(df)}")
print(f"Período: {df['time'].min()} até {df['time'].max()}")
print(f"Fee rate médio: {df['avgfeerate'].mean()}")
```

---

## 🔧 Desenvolvimento Local

### Pré-requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recomendado) ou pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/m-marqx/BTC-RPC-Data.git
cd BTC-RPC-Data

# Usando uv (recomendado)
uv sync

# Ou usando pip
pip install -r requirements.txt
```

### Executando o Atualizador

Você precisará de endpoints da API QuickNode configurados como variáveis de ambiente:

```bash
export quicknode_endpoint_1="seu-endpoint-aqui"
python main.py
```

---

## 📊 Estrutura dos Dados

```
data/
└── onchain/
    └── BTC/
        └── block_stats_fragments/
            ├── dump/           # Dumps de dados históricos
            └── incremental/    # Atualizações incrementais diárias
```

### Colunas Disponíveis

Os dados de estatísticas de blocos incluem (mas não se limitam a):

| Coluna | Descrição |
|--------|-----------|
| `height` | Altura do bloco |
| `time` | Timestamp do bloco |
| `avgfee` | Taxa média de transação |
| `avgfeerate` | Fee rate médio (sat/vB) |
| `txs` | Número de transações |
| `total_size` | Tamanho total do bloco |
| `totalfee` | Total de taxas no bloco |
| `subsidy` | Subsídio do bloco |

---

## 🔄 Como as Atualizações Funcionam

1. **GitHub Actions** dispara a cada 30 minutos
2. **Script busca** novos blocos da API QuickNode
3. **Dados são salvos** como arquivos parquet incrementais
4. **Mudanças são commitadas** no repositório
5. **Imagem Docker é reconstruída** com dados atualizados

Confira o [arquivo de workflow](.github/workflows/btc_data_update.yml) para detalhes.

---

## 🤝 Contribuindo

Encontrou um bug? Tem uma ideia? Quer adicionar suporte para outras criptomoedas?

1. Faça um Fork do repositório
2. Crie sua branch de feature (`git checkout -b feature/feature-incrivel`)
3. Commit suas mudanças (`git commit -m 'Adiciona feature incrível'`)
4. Push para a branch (`git push origin feature/feature-incrivel`)
5. Abra um Pull Request

---

## 📬 Contato

Tem dúvidas, sugestões ou só quer dar um oi? Minha DM está sempre aberta!

Se este projeto te ajudou nas suas análises de Data Science ou projetos, eu adoraria saber!

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  Feito com ☕ e uma dose saudável de teimosia
  <br>
  <a href="https://github.com/m-marqx/BTC-RPC-Data">⭐ Dê uma estrela se te ajudou!</a>
</p>