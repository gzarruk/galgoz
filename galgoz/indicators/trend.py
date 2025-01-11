import pandas as pd
from scipy import signal  # type: ignore
from galgoz.indicators.base import Indicator
from talib import MFI as mfi


class SG(Indicator):
    window: int = 250
    order: int = 2

    def __init__(self, data: pd.Series, window: int = 250, order: int = 2):
        super().__init__(name="Savitzky-Golay Filter", data=data)
        self.window = window
        self.order = order
        if data is not None:
            self.run()

    def __str__(self):
        return f"Savitzky-Golay Filter (window={self.window}, order={self.order})"

    def run(self):
        res = signal.savgol_filter(
            self.data.values, window_length=self.window, polyorder=self.order
        )
        self.output = pd.Series(res, index=self.data.index, name="SG")
