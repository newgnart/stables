# Stablecoin Analytics Dashboard

A comprehensive dashboard for analyzing stablecoin data from DeFiLlama, providing insights into market share, chain distribution, and growth metrics.

## Features

- Real-time data collection from DeFiLlama API
- Market share analysis and visualization
- Chain distribution metrics
- Growth rate analysis
- Historical trend visualization
- Interactive Streamlit dashboard

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
│   ├── processing/         # Data transformation
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
cd stablecoin-analytics-dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add any required API keys:
```
DEFILLAMA_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit dashboard:
```bash
streamlit run dashboard/app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Click the "Refresh Data" button to fetch the latest data from DeFiLlama

## Data Collection

The dashboard collects data from the following sources:
- DeFiLlama API for stablecoin data
- Historical data for trend analysis
- Chain-specific circulating supply data

## Analysis Features

- Market share distribution
- Chain distribution analysis
- Growth rate metrics
- Historical trend visualization
- Raw data tables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
