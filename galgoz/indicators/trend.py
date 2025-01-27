import pandas as pd
import numpy as np
from scipy import signal  # type: ignore
from ..indicators.base import Indicator


class SG(Indicator):
    window: int = 250
    order: int = 2
    line_color: str = "blue"

    def __init__(
        self, data: pd.DataFrame, window: int = window, order: int = order, **kwargs
    ):
        super().__init__(name="SG", data=data)
        self.window = window
        self.order = order
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Savitzky-Golay Filter (window={self.window}, order={self.order})"

    def run(self):
        res = signal.savgol_filter(
            self.data.mid_c.values, window_length=self.window, polyorder=self.order
        )
        self.output = pd.Series(res, index=self.data.index, name="SG")

    def update(self, new_data: pd.DataFrame | None):
        self.data = new_data
        self.run()


class HMA(Indicator):
    window: int = 100
    line_color: str = "blue"

    def __init__(self, data: pd.DataFrame, window: int = window, **kwargs):
        super().__init__(name="HMA", data=data)
        self.window = window
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Hull Moving Average (window={self.window})"

    def run(self):
        wma1 = 2 * self.data.mid_c.rolling(window=self.window // 2).mean()
        wma2 = self.data.mid_c.rolling(window=self.window).mean()
        diff = wma1 - wma2
        self.output = diff.rolling(window=int(np.sqrt(self.window))).mean()

    def update(self, new_data: pd.DataFrame | None):
        self.data = new_data
        self.run()
