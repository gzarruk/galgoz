from ..indicators.base import Indicator
import pandas as pd
from talib import WILLR, RSI as rsi


class WPR(Indicator):
    row: int = 2
    window: int = 14

    def __init__(self, data: pd.DataFrame, window: int = window, **kwargs):
        super().__init__(name="WPR", data=data)
        self.window = window
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Williams %R (window={self.window})"

    def run(self):
        res = WILLR(
            self.data["mid_h"],
            self.data["mid_l"],
            self.data["mid_c"],
            timeperiod=self.window,
        )
        self.output = pd.Series(res, index=self.data.index, name="WPR")

    def update(self, new_data: pd.DataFrame | None):
        self.data = new_data
        self.run()


class RSI(Indicator):
    row: int = 2
    window: int = 14

    def __init__(self, data: pd.DataFrame, window: int = window, **kwargs):
        super().__init__(name="RSI", data=data)
        self.window = window
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Relative Strength Index (window={self.window})"

    def run(self):
        res = rsi(
            self.data.values,
            timeperiod=self.window,
        )
        self.output = pd.Series(res, index=self.data.index, name="RSI")

    def update(self, new_data: pd.DataFrame | None):
        self.data = new_data
        self.run()
