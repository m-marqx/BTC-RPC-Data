# 🪙 BTC-RPC-Data

[![BTC Data Updater](https://github.com/m-marqx/BTC-RPC-Data/actions/workflows/btc_data_update.yml/badge.svg)](https://github.com/m-marqx/BTC-RPC-Data/actions/workflows/btc_data_update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

> **Free Bitcoin on-chain data without selling a kidney to run a full node.**

---

## 📑 Summary

| Section | Description |
|---------|-------------|
| [📖 The Story](#-the-story-how-this-madness-began) | How a 0.5TB problem became a free solution |
| [✨ Features](#-features) | What this repository offers |
| [🐳 Docker Usage](#-fetching-data-with-docker) | Get data in seconds with Docker |
| [🔧 Local Setup](#-local-development) | Run the project locally |
| [📊 Data Structure](#-data-structure) | What's inside the data folder |
| [🤝 Contributing](#-contributing) | Help make this better |

---

## 📖 The Story: How This Madness Began

Once upon a time, a developer (me) had a brilliant idea: *"I want Bitcoin on-chain data! Average transaction fees, transaction counts, fee rates... the whole enchilada!"*

Simple enough, right? Just spin up a full node and... **wait, what?**

### 🎭 Act I: The Harsh Reality

To get on-chain data, I'd need to run a Bitcoin full node on my machine. No big deal... until I discovered that a full node weighs **over 0.5TB** these days. I looked at my hard drives. My hard drives looked back at me. We both knew there wasn't enough space. I'd have to delete half my life to *maybe* make it fit.

### 🎭 Act II: The Cloud Fantasy

*"Aha!"* I thought, *"I'll just use the cloud!"*

Then I checked the prices. Running a full node on cloud infrastructure would cost me a small fortune. For a pet project. A *pet project*. My wallet started crying before I even finished the calculation.

### 🎭 Act III: The Hero's Journey (AKA Google Search)

After much research and an unhealthy amount of determination, I found it: **QuickNode API**.

It could extract all the information I needed, block by block. Would it be slow? Yes. Would it work? Also yes. And sometimes in life, *"it works"* is all you need.

### 🎭 Act IV: The Automation Saga

Now I had another problem: keeping this data updated. Three options emerged:

| Option | Description | Verdict |
|--------|-------------|---------|
| **A** | Pay for a hosting service to run the Python script | 💸 Money? What's that? |
| **B** | Leave my machine running 24/7 | 🔥 My electricity bill says no |
| **C** | Use GitHub Actions with a cron job every 30 minutes | 🎉 **FREE!** |

If you've peeked at the [workflow file](.github/workflows/btc_data_update.yml), you already know I chose Option C. GitHub Actions runs the script every 30 minutes, commits the new data, and even builds a fresh Docker image. All for the low price of *absolutely nothing*.

### 🎭 Epilogue

And that's how this repository was born: out of necessity, creativity, and a strong refusal to pay for things that could be free.

---

## ✨ Features

- 📈 **Bitcoin on-chain block statistics** - Transaction fees, counts, sizes, and more
- 🔄 **Auto-updated every 30 minutes** - Via GitHub Actions cron job
- 🐳 **Docker support** - Pull the image and get instant access to data
- 📦 **Parquet format** - Efficient, compressed, and pandas-friendly
- 💰 **100% Free** - No full node, no cloud costs, no tears

---

## 🐳 Fetching Data with Docker

The easiest way to get the data is through our Docker image. No setup required!

### Quick Start

```bash
# Pull the latest image
docker pull ghcr.io/m-marqx/btc-rpc:latest

# Run interactive Python shell with data explorer
docker run -it ghcr.io/m-marqx/btc-rpc:latest
```

### Inside the Container

Once inside, you'll have access to helper functions:

```python
# List all available parquet files
list_data_files()

# Load on-chain block statistics
df = load_onchain()
print(df.head())

# Check available columns
print(df.columns.tolist())
```

### Extract Data to Local Machine

Want the files on your local machine? Use docker-compose:

```bash
# Clone the repository
git clone https://github.com/m-marqx/BTC-RPC-Data.git
cd BTC-RPC-Data

# Extract data to ./output folder
docker compose up
```

Or manually copy from a running container:

```bash
# Run container in background
docker run -d --name btc-data ghcr.io/m-marqx/btc-rpc:latest sleep infinity

# Copy data to local folder
docker cp btc-data:/app/data ./local-data

# Clean up
docker rm -f btc-data
```

### Using Data in Your Projects

```python
import pandas as pd

# If you extracted the data locally
df = pd.read_parquet("./local-data/onchain/BTC/block_stats_fragments")

# Analyze away!
print(f"Total blocks: {len(df)}")
print(f"Date range: {df['time'].min()} to {df['time'].max()}")
print(f"Average fee rate: {df['avgfeerate'].mean()}")
```

---

## 🔧 Local Development

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/m-marqx/BTC-RPC-Data.git
cd BTC-RPC-Data

# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Running the Updater

You'll need QuickNode API endpoints set as environment variables:

```bash
export quicknode_endpoint_1="your-endpoint-here"
python main.py
```

---

## 📊 Data Structure

```
data/
└── onchain/
    └── BTC/
        └── block_stats_fragments/
            ├── dump/           # Historical data dumps
            └── incremental/    # Daily incremental updates
```

### Available Columns

The block stats data includes (but is not limited to):

| Column | Description |
|--------|-------------|
| `height` | Block height |
| `time` | Block timestamp |
| `avgfee` | Average transaction fee |
| `avgfeerate` | Average fee rate (sat/vB) |
| `txs` | Number of transactions |
| `total_size` | Total block size |
| `totalfee` | Total fees in block |
| `subsidy` | Block subsidy |

---

## 🔄 How Updates Work

1. **GitHub Actions** triggers every 30 minutes
2. **Script fetches** new blocks from QuickNode API
3. **Data is saved** as incremental parquet files
4. **Changes are committed** to the repository
5. **Docker image is rebuilt** with fresh data

Check the [workflow file](.github/workflows/btc_data_update.yml) for details.

---

## 🤝 Contributing

Found a bug? Have an idea? Want to add support for other cryptocurrencies?

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📬 Contact

Have questions, suggestions, or just want to say hi? My DMs are always open!

If this project helped you with your Data Science analyses or projects, I'd love to hear about it! 

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ☕ and a healthy dose of stubbornness
  <br>
  <a href="https://github.com/m-marqx/BTC-RPC-Data">⭐ Star this repo if it helped you!</a>
</p>