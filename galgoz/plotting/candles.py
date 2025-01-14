from re import sub
from typing import Optional
import pandas as pd
from typing import List
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore


def plot(
    df: Optional[pd.DataFrame] = None,
    instrument: Optional[str] = None,
    indicators: Optional[List] = None,
    row_heights: Optional[List[int]] = None,
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
        indicators (Optional[List[Dict[str, Union[str, pd.Series, pd.DataFrame, Dict[str, Union[str, int]]]]]]): List of dictionaries containing indicator data.
            Each dictionary must include:
                - "name" (str): Name of the indicator.
                - "data" (pd.Series or pd.DataFrame): Data for the indicator.
                - "mode" (str): Mode for the plot (e.g., "lines").
                - "row" (int): Row number for the subplot.
                - "line" (Dict[str, Union[str, int]]): Line properties (e.g., color, width).
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

    # Number of rows (subplota) in the Figure
    if indicators is not None:
        max_rows = max([indicator["row"] for indicator in indicators])
        if max_rows != 1:
            row_heights = [0.8] + [0.2 / (max_rows - 1)] * (max_rows - 1)
        else:
            row_heights = [1]
    else:
        max_rows = 1
        row_heights = [1]

    fig = make_subplots(
        rows=max_rows, cols=1, row_heights=row_heights, vertical_spacing=0.03
    )

    fig.add_trace(
        go.Candlestick(
            x=df_plot.time_str,
            open=df_plot[f"{price}_o"],
            high=df_plot[f"{price}_h"],
            low=df_plot[f"{price}_l"],
            close=df_plot[f"{price}_c"],
            name=f"{instrument}",
            showlegend=True,
            line=dict(width=1),
            opacity=1,
            increasing_fillcolor="darkseagreen",
            increasing_line_color="darkseagreen",
            decreasing_fillcolor="red",
            decreasing_line_color="red",
        ),
        row=1,
        col=1,
    )

    add_indicators_to_plot(indicators, fig)
    _candle_plot_layout(width, height, df_plot, fig)

    return fig


def add_indicators_to_plot(indicators, fig):
    if indicators is not None:
        for indicator in indicators:
            xdata = pd.Series(indicator["data"].index).dt.strftime(" %-b %d, '%y %H:%M")
            fig.add_trace(
                go.Scatter(
                    x=xdata,
                    y=indicator["data"],
                    mode=indicator["mode"],
                    line=indicator["line"],
                    marker=indicator["marker"],
                    name=indicator["name"],
                ),
                row=indicator["row"],
                col=1,
            )
            fig.update_yaxes(
                title_text=indicator["name"],
                row=indicator["row"],
                col=1,
                showticklabels=True,
            )
            if indicator["row"] != 1:
                fig.update_xaxes(
                    showticklabels=False,
                    row=indicator["row"],
                    col=1,
                )


def _candle_plot_layout(width, height, df_plot, fig):
    fig.update_layout(
        legend=dict(
            x=0,
            y=1.03,
            traceorder="normal",
            font=dict(family="sans-serif", size=10, color="black"),
            bgcolor="rgba(255,255,255,0)",
            orientation="h",
        ),
        yaxis_title="Price",
        width=width,
        height=height,
        xaxis_rangeslider_visible=False,
        hoverlabel=dict(bgcolor="rgba(255,255,255,0.5)"),
        hovermode="x unified",
        margin=dict(t=50, b=20),
    )
    fig.update_traces(hoverinfo="y+x")

    fig.update_yaxes(
        showspikes=True,
        spikecolor="green",
        spikemode="across",
        spikesnap="cursor",
        showline=True,
    )

    # Display only a percentage of the xticks based on the length of the dataset
    num_ticks = len(df_plot) // 10  # Show 10% of the ticks
    fig.update_xaxes(
        tickvals=df_plot.time_str[::num_ticks],
        showspikes=True,
        spikecolor="green",
        spikemode="across",
        spikesnap="cursor",
        showline=True,
        matches="x",
    )
    fig.update_traces(xaxis="x1")  # This is to show the spikes across all subplots
