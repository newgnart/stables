import streamlit as st
import os
import sys

# Add the current directory to the path to find local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import load_data, aggregate_by_chain, aggregate_by_name
from visualization import create_chain_chart, create_name_chart


def main():
    """Main function to run the Streamlit app."""

    # Set page config
    st.set_page_config(
        page_title="Stablecoin Circulation Dashboard",
        page_icon="💰",
        layout="wide",
    )

    # App title and description
    st.title("Stablecoin Circulation Dashboard")
    st.markdown(
        """
        Visualize stablecoin circulation across different blockchains and coins.
        """
    )

    # File path for the data
    data_path = "data/chain_circulating.csv"

    # Load data
    try:
        df = load_data(data_path)
        st.success(f"Successfully loaded data with {len(df)} records")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    # Create sidebar for visualization options
    st.sidebar.header("Visualization Options")

    # Create radio button for selecting visualization type
    viz_type = st.sidebar.radio(
        "Select Visualization By:", ["Blockchain", "Stablecoin"], index=0
    )

    # Display the appropriate visualization based on user selection
    if viz_type == "Blockchain":
        st.subheader("Stablecoin Circulation by Blockchain")

        # Process the data for visualization
        chain_data = aggregate_by_chain(df)

        # Display some stats
        total_circulation = chain_data["circulating"].sum()
        st.metric("Total Circulation (USD)", f"${total_circulation:,.2f}")

        # Create and display the chart
        fig = create_chain_chart(chain_data)
        st.plotly_chart(fig, use_container_width=True)

        # Display the data table
        with st.expander("View Data Table"):
            st.dataframe(chain_data, use_container_width=True)

    else:  # Stablecoin
        st.subheader("Stablecoin Circulation by Coin")

        # Process the data for visualization
        name_data = aggregate_by_name(df)

        # Display some stats
        total_circulation = name_data["circulating"].sum()
        st.metric("Total Circulation (USD)", f"${total_circulation:,.2f}")

        # Create and display the chart
        fig = create_name_chart(name_data)
        st.plotly_chart(fig, use_container_width=True)

        # Display the data table
        with st.expander("View Data Table"):
            st.dataframe(name_data, use_container_width=True)


if __name__ == "__main__":
    main()
