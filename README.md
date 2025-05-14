# Stablecoins 
Dashboard for analyzing stablecoin data

## Features


## Project Structure

```
stablecoin-analytics-dashboard/
├── .env                    # Store API keys (add to .gitignore)
├── .gitignore              # Ignore env files and large datasets
├── README.md               # Project documentation
├── requirements.txt        # Dependencies
├── data/
│   ├── raw/                # Raw data from APIs
│   │   ├── blockchain/     # On-chain data
│   │   ├── market/         # Price and market cap data
│   │   └── defi/           # DeFi protocol integration data
│   └── processed/          # Cleaned and transformed data
├── notebooks/              # Jupyter notebooks for exploration
├── src/
│   ├── data/               # Data collection scripts
│   │   ├── blockchain.py   # On-chain data collection
│   │   ├── market_data.py  # Price and market data
│   │   └── defi_data.py    # Protocol integration data
│   ├── transform/         # Data transformation
│   │   └── transformations.py
│   ├── analysis/           # Analysis and metrics
│   │   └── basic_metrics.py
│   └── visualization/      # Visualization components
│       └── components.py
└── dashboard/             # Streamlit dashboard app
    └── app.py             # Main dashboard
```

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd stables
```

2. Create and activate a virtual environment:
```bash
uv sync
uv pip install -r requirements.txt
uv pip install -e .
```
3. Or use pip to install the dependencies:
```bash
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
pip install -e .
```


