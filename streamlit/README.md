# Stablecoin Circulation Dashboard

A Streamlit application for visualizing stablecoin circulation data across different blockchains and coins.

## Features

- Interactive visualization of stablecoin circulation data
- Option to view data by blockchain or by coin name
- Interactive charts with logarithmic scaling for better visualization
- Data tables for detailed information

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Navigate to the streamlit directory:

```bash
cd streamlit
```

2. Run the Streamlit app:

```bash
streamlit run app.py
```

3. The application will be available at http://localhost:8501

## Data

The application uses stablecoin circulation data from `../data/chain_circulating.csv`.

## Structure

- `app.py`: Main Streamlit application
- `utils.py`: Data loading and processing utilities
- `visualization.py`: Visualization functions
- `requirements.txt`: Required packages 