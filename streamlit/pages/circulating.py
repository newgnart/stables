import streamlit as st
import os
import sys
import plotly.express as px

# Add the current directory to the path to find local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import (
    load_data,
    aggregate_by_chain,
    aggregate_by_name,
    filter_by_chain,
    calculate_movers_by_chain,
    calculate_movers_by_coin,
    calculate_detailed_movers,
    categorize_movers,
)
from visualization import (
    create_chain_chart,
    create_name_chart,
    create_chain_coins_chart,
    create_movers_scatter_plot,
    create_movers_bar_chart,
)


def show_by_chain_tab(df):
    """Display the 'By chain' tab content."""
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


def show_by_stable_tab(df):
    """Display the 'By stable' tab content."""
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


def show_by_specific_chain_tab(df):
    """Display the 'By specific chain' tab content."""
    st.subheader("Stablecoin Circulation on Specific Blockchain")

    # Get unique chains for selection box
    chains = df["chain"].unique().tolist()
    chains.sort()

    # Create selection box
    selected_chain = st.selectbox("Select a blockchain", chains)

    # Filter data for the selected chain
    chain_coins_data = filter_by_chain(df, selected_chain)

    # Display some stats
    chain_total = chain_coins_data["circulating"].sum()
    st.metric(f"Total Circulation on {selected_chain} (USD)", f"${chain_total:,.2f}")

    # Create and display the chart
    fig = create_chain_coins_chart(chain_coins_data, selected_chain)
    st.plotly_chart(fig, use_container_width=True)

    # Display the data table
    with st.expander("View Data Table"):
        st.dataframe(chain_coins_data, use_container_width=True)


def show_movers_tab(df):
    """Display the 'Movers' tab content."""
    st.subheader("Stablecoin Circulation Movers")

    # Time period selector
    time_period_options = {
        "Yesterday": "PrevDay",
        "Last Week": "PrevWeek",
        "Last Month": "PrevMonth",
    }
    time_period_selection = st.radio(
        "Compare current circulation with:",
        options=list(time_period_options.keys()),
        horizontal=True,
    )
    time_period = time_period_options[time_period_selection]

    # Create columns for threshold controls
    col1, col2 = st.columns(2)

    with col1:
        circ_threshold = st.slider(
            "Circulation Size Threshold (percentile)",
            min_value=50,
            max_value=95,
            value=75,
            step=5,
            help="Percentile threshold to separate 'large' from 'small' circulation",
        )

    with col2:
        change_threshold = st.slider(
            "Significant Change Threshold (%)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Percentage change threshold to identify significant movers",
        )

    # Entity type selector (chains or coins)
    entity_options = ["Chains", "Coins", "Detailed (Chain-Coin pairs)"]
    entity_selection = st.radio("Analyze by:", options=entity_options, horizontal=True)

    # Calculate mover data based on selection
    if entity_selection == "Chains":
        movers_data = calculate_movers_by_chain(df, time_period)
        entity_type = "chain"
    elif entity_selection == "Coins":
        movers_data = calculate_movers_by_coin(df, time_period)
        entity_type = "coin"
    else:  # Detailed analysis
        movers_data = calculate_detailed_movers(df, time_period)
        entity_type = "pair"

    # Categorize the movers
    categorized_data = categorize_movers(movers_data, circ_threshold, change_threshold)

    # Display summary statistics
    st.subheader("Movement Summary")

    # Create metric columns
    metric_cols = st.columns(4)

    with metric_cols[0]:
        total_growing = len(categorized_data[categorized_data["pct_change"] > 0])
        total_entities = len(categorized_data)
        st.metric("Growing", f"{total_growing} ({total_growing/total_entities:.1%})")

    with metric_cols[1]:
        total_declining = len(categorized_data[categorized_data["pct_change"] < 0])
        st.metric(
            "Declining", f"{total_declining} ({total_declining/total_entities:.1%})"
        )

    with metric_cols[2]:
        net_change = categorized_data["abs_change"].sum()
        st.metric("Net Change", f"${net_change:,.2f}")

    with metric_cols[3]:
        avg_pct_change = categorized_data["pct_change"].mean()
        st.metric("Avg % Change", f"{avg_pct_change:.2f}%")

    # Display charts
    st.subheader("Visualizations")

    # Create tabs for different visualizations
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(
        ["Quadrant Plot", "Top Movers", "Category Breakdown"]
    )

    with chart_tab1:
        scatter_log_scale = st.checkbox(
            "Use logarithmic scale for circulation", value=True
        )
        fig1 = create_movers_scatter_plot(
            categorized_data, entity_type, scatter_log_scale
        )
        st.plotly_chart(fig1, use_container_width=True)

    with chart_tab2:
        top_n = st.slider("Number of top movers to display", 5, 20, 10)
        fig2 = create_movers_bar_chart(categorized_data, entity_type, top_n)
        st.plotly_chart(fig2, use_container_width=True)

    with chart_tab3:
        # Category distribution
        category_counts = categorized_data["category"].value_counts().reset_index()
        category_counts.columns = ["Category", "Count"]

        fig3 = px.pie(
            category_counts,
            values="Count",
            names="Category",
            title="Distribution of Movement Categories",
            color="Category",
            color_discrete_map={
                "Rising Stars": "#00CC96",
                "Major Growers": "#636EFA",
                "Declining Leaders": "#EF553B",
                "Fading Coins": "#FFA15A",
                "Stable": "#CCCCCC",
            },
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Display the data table
    st.subheader("Data Table")

    # Format the DataFrame for display
    display_data = categorized_data.copy()
    if entity_type != "pair":
        display_cols = [
            entity_type,
            "circulating",
            "pct_change",
            "abs_change",
            "category",
        ]
    else:
        display_cols = [
            "chain",
            "name",
            "circulating",
            "pct_change",
            "abs_change",
            "category",
        ]

    # Add option to view full dataset
    show_all = st.checkbox("Show all data", value=False)

    if show_all:
        st.dataframe(
            display_data[display_cols],
            use_container_width=True,
            column_config={
                "circulating": st.column_config.NumberColumn(
                    "Circulation", format="$%.2f"
                ),
                "pct_change": st.column_config.NumberColumn(
                    "% Change", format="%.2f%%"
                ),
                "abs_change": st.column_config.NumberColumn(
                    "Absolute Change", format="$%.2f"
                ),
            },
        )
    else:
        # Show only significant movers (not Stable)
        significant_movers = display_data[display_data["category"] != "Stable"]
        st.dataframe(
            significant_movers[display_cols],
            use_container_width=True,
            column_config={
                "circulating": st.column_config.NumberColumn(
                    "Circulation", format="$%.2f"
                ),
                "pct_change": st.column_config.NumberColumn(
                    "% Change", format="%.2f%%"
                ),
                "abs_change": st.column_config.NumberColumn(
                    "Absolute Change", format="$%.2f"
                ),
            },
        )


def show_circulating_page():
    """Page to display stablecoin circulation data."""

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

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["By chain", "By stable", "By specific chain", "Movers"]
    )

    # Display the appropriate content for each tab
    with tab1:
        show_by_chain_tab(df)

    with tab2:
        show_by_stable_tab(df)

    with tab3:
        show_by_specific_chain_tab(df)

    with tab4:
        show_movers_tab(df)


def main():
    """Main function to run the Streamlit app."""

    # Set page config
    st.set_page_config(
        page_title="Stablecoin Circulation Dashboard",
        page_icon="💰",
        layout="wide",
    )

    # Create a dictionary of pages
    pages = {
        "circulating": show_circulating_page,
    }

    # Display the selected page
    pages["circulating"]()


if __name__ == "__main__":
    main()
