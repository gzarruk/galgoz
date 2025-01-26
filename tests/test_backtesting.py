from galgoz import DATA_FOLDER
from galgoz.backtesting import Backtest
import pandas as pd
import numpy as np

from galgoz.indicators.oscillators import WPR

data = pd.read_pickle(DATA_FOLDER / "GBP_JPY_H1.pkl")

def test_indicator_updates_correctly():
    data_length = 1000
    data_slice = data.iloc[:data_length].copy()
    # Run the default strategy and indictors (WPR is one of them) with the data slice
    bt = Backtest(data=data_slice)
    wpr = WPR(data=data_slice).output
    print(bt.data.tail())
    assert np.isnan(bt.data["WPR"].iloc[bt.init_rows])
    assert not np.isnan(bt.data["WPR"].iloc[bt.init_rows-1])
    # TODO: Run the backtest and check that the WPR indicator is updated correctly. The WPR in data should be the same as the WPR in wpr for bt.init_rows
    bt.run()
    assert bt.data["WPR"].iloc[bt.init_rows] == wpr.iloc[bt.init_rows]
