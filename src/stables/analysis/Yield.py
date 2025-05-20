import os
import sys
import plotly.express as px
import pandas as pd
from stables.visualization.components import plot_stable_chain_data


class Yield:
    """Yield class"""

    def __init__(self, pool: str, llama_yield_data: pd.DataFrame):
        """
        Args:
            pool: str, pool address
            llama_yield_data: pd.DataFrame, yield data from llama api, pools endpoint
        """
        self.pool = pool
        self.yield_data = self._filter_data(llama_yield_data)

    def __getitem__(self, key):
        """Allow accessing DataFrame columns using square bracket notation."""
        return self.yield_data[key].iloc[0]

    def yield_attributes(self):
        """Return a list of available column names that can be accessed."""
        return list(self.yield_data.columns)

    def _filter_data(self, df: pd.DataFrame):
        df = df[df["pool"] == self.pool]
        return df
