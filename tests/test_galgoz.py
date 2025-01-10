from galgoz import Galgoz, DATA_FOLDER
import pandas as pd
from pathlib import Path
from plotly import graph_objects as go  # type: ignore

gz = Galgoz()


def test_fetch_instruments():
    instruments = gz.fetch_instruments()
    instruments_dict = {instrument["name"]: instrument for instrument in instruments}
    assert len(instruments) > 0
    assert "GBP_JPY" in instruments_dict


def test_store_data():
    gz.instrument = "EUR_USD"
    gz.store_data(date_from="2024-12-17T00:00:00Z", date_to="2024-12-18T00:00:00Z")
    old_file = Path(DATA_FOLDER) / "EUR_USD_H1.pkl"
    new_file = Path(DATA_FOLDER) / "file_for_testing.pkl"
    old_file.rename(new_file)
    assert Path(new_file).exists(), f"File {new_file} does not exist"

    # Retreive the file_for_testing.pkl as a dataframe and check that the length is > 0
    df = pd.read_pickle(new_file)
    assert len(df) > 0, "Dataframe is empty"


def test_plot_candles():
    df_plot = pd.read_pickle(Path(DATA_FOLDER) / "file_for_testing.pkl")
    fig = gz.plot_candles(df_plot, show=False)
    assert isinstance(fig, go.Figure), "Plot is not a Plotly Figure"


def test_candles_df():
    df = gz.candles_df(price="MBA")
    assert isinstance(df, pd.DataFrame), "Data is not a DataFrame"
    assert len(df) > 0, "Dataframe is empty"
    assert "time" in df.columns, "Column 'time' is not in the dataframe"
    assert (
        df["time"].apply(lambda x: isinstance(x, str)).all()
    ), "Not all values in 'time' column are strings"
    expected_columns = [
        "mid_c",
        "mid_o",
        "mid_l",
        "mid_h",
        "bid_c",
        "bid_o",
        "bid_l",
        "bid_h",
        "ask_c",
        "ask_o",
        "ask_l",
        "ask_h",
        "volume",
    ]
    for column in expected_columns:
        assert column in df.columns, f"Column '{column}' is not in the dataframe"
        assert (
            df[column].apply(lambda x: isinstance(x, float)).all()
        ), f"Not all values in '{column}' column are floats"
