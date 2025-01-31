from .indicators.base import Indicator
import pandas as pd


def generate_indicators(*indicators: Indicator):
    """
    Generates a list of indicators with plotting metadata.

    Args:
        *indicators: Variable length argument list of Indicator types.

    Returns:
        list: A list of dictionaries, each containing the attributes and plotting metadata.
    """
    indicators_list = []
    for indicator in indicators:
        indicators_list.append(
            {
                "name": indicator.name,
                "data": indicator.data,
                "mode": indicator.mode,
                "row": indicator.row,
                "line": indicator.line,
                "marker": indicator.marker,
                "output": indicator.output,
            }
        )
    return indicators_list


def set_data_index_and_time_str(df: pd.Series | pd.DataFrame):
    """
    Sets the time column as the index and creates a column with time as a string.
    This assumes that the df has a 'time' column that is a string. Or that the original df has a 'time' column that was set as the index.

    Args:
        df (pd.Series | pd.DataFrame): The DataFrame or Series to fix.

    Returns:
        pd.Series | pd.DataFrame: The fixed DataFrame or Series.
    """
    # Just to make sure time is not already set as the index
    df.reset_index(inplace=True)
    df["time"] = pd.to_datetime(df["time"])
    df["time_str"] = df["time"].dt.strftime(" %-b %d, '%y %H:%M")
    df.set_index("time", inplace=True)
    return df
