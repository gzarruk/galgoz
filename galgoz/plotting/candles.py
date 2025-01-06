from typing import Optional
import pandas as pd
import plotly.graph_objects as go  # type: ignore


def plot(
    df: Optional[pd.DataFrame] = None,
    instrument: Optional[str] = None,
    price: str = "mid",
    width: int = 2000,
    height: int = 1000,
):
    """
    Plots candlestick data.

    Args:
        df (Optional[pd.DataFrame]): DataFrame containing the candlestick data.
            Must include columns for time, open, high, low, and close prices.
        price (str): Prefix for the price columns in the DataFrame. Defaults to "mid". Options are: "mid", "bid", or "ask".
        width (int): Width of the plot. Defaults to 2000.
        height (int): Height of the plot. Defaults to 1000.
    Raises:
        ValueError: If no DataFrame is provided.
    Returns:
        None
    """
    if df is None:
        raise ValueError("No data received")
    else:
        df_plot = df.copy()
        df_plot.reset_index(inplace=True)
        df_plot["time"] = pd.to_datetime(df_plot["time"])
        df_plot["time_str"] = df_plot["time"].dt.strftime(" %-b %d, '%y %H:%M")
        
    if instrument is None:
        instrument = "Instrument"

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df_plot.time_str,
                open=df_plot[f"{price}_o"],
                high=df_plot[f"{price}_h"],
                low=df_plot[f"{price}_l"],
                close=df_plot[f"{price}_c"],
                name=f"{instrument}",
                showlegend=True,
            )
        ]
    )
    fig.update_layout(
        legend=dict(
            x=0,
            y=1,
            traceorder="normal",
            font=dict(family="sans-serif", size=10, color="black"),
            bgcolor="rgba(255,255,255,0)",
        )
    )
    fig.update_traces(hoverinfo="y+x")

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Price",
        width=width,
        height=height,
        xaxis_rangeslider_visible=False,
        hoverlabel=dict(bgcolor="rgba(255,255,255,0.5)"),
        hovermode="x unified",
    )

    fig.update_xaxes(
        showspikes=True,
        spikecolor="green",
        spikemode="across",
        spikesnap="cursor",
        showline=True,
    )
    fig.update_yaxes(
        showspikes=True,
        spikecolor="green",
        spikemode="across",
        spikesnap="cursor",
        showline=True,
    )

    # Display only a percentage of the xticks based on the length of the dataset
    num_ticks = len(df_plot) // 10  # Show 10% of the ticks
    fig.update_xaxes(tickvals=df_plot.time_str[::num_ticks])
    fig.update_layout()

    return fig
