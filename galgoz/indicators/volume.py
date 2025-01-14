import pandas as pd
from galgoz.indicators.base import Indicator
from talib import MFI as mfi


class MFI(Indicator):
    row: int = 2
    window: int = 14

    def __init__(self, data: pd.DataFrame, window: int = window, **kwargs):
        super().__init__(name="Money Flow Index", data=data)
        self.window = window
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Money Flow Index (window={self.window})"

    def run(self):
        res = mfi(
            self.data["mid_h"],
            self.data["mid_l"],
            self.data["mid_c"],
            self.data["volume"],
            timeperiod=self.window,
        )
        self.output = pd.Series(res, index=self.data.index, name="MFI")
