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
│   └── processed/          # Cleaned and transformed data
├── notebooks/              # Jupyter notebooks for exploration
├── src/
│   ├── data/               # Data collection scripts
│   ├── transform/         # Data transformation
│   ├── analysis/           # Analysis and metrics
│   └── visualization/      # Visualization components
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


