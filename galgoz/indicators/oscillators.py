from ..indicators.base import Indicator
import pandas as pd
import numpy as np
from talib import WILLR
from talib import RSI as rsi


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
            self.data.mid_c,
            timeperiod=self.window,
        )
        self.output = pd.Series(res, index=self.data.index, name="RSI")

    def update(self, new_data: pd.DataFrame | None):
        self.data = new_data
        self.run()


class QQE(Indicator):
    row: int = 2
    length: int = 8
    smooth: int = 1
    factor: float = 1.618
    mode: list = ["lines", "lines"]
    line: list = [dict(color="green", width=2), dict(color="maroon", width=2)]
    marker: list = [
        dict(size=5, color="blue", symbol="circle"),
        dict(size=5, color="blue", symbol="circle"),
    ]

    def __init__(
        self,
        data: pd.DataFrame,
        length: int = length,
        smooth: int = smooth,
        factor: float = factor,
        **kwargs,
    ):
        super().__init__(name="QQE", data=data)
        self.length = length
        self.smooth = smooth
        self.factor = factor
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Quantitative Qualitative Estimation (length={self.length})"

    def run(self):
        result = qqe(
            self.data, length=self.length, smooth=self.smooth, factor=self.factor
        )
        self.output = result[["qqe_fast", "qqe_slow"]]

    def update(self, new_data: pd.DataFrame | None):
        self.data = new_data
        self.run()


def qqe(
    data: pd.DataFrame, length: int = 8, smooth: int = 1, factor: float = 1.618
) -> pd.DataFrame:
    df = data.copy()
    _rsi = rsi(df["mid_c"].to_numpy(dtype=np.float64), timeperiod=length)
    _qqe_fast = pd.Series(data=_rsi, index=df.index).ewm(span=smooth).mean().to_numpy()
    df["qqe_fast"] = _qqe_fast
    rsi_delta = df["qqe_fast"].diff().abs().values
    wmma = np.zeros(len(df))
    atr_rsi = np.zeros(len(df))
    for i in range(1, len(df)):
        wmma[i] = rsi_delta[i] / length + (1 - 1 / length) * (
            wmma[i - 1] if not np.isnan(wmma[i - 1]) else 0
        )
        atr_rsi[i] = wmma[i] / length + (1 - 1 / length) * (
            atr_rsi[i - 1] if not np.isnan(atr_rsi[i - 1]) else 0
        )
    qqe_up = _qqe_fast + atr_rsi * factor
    qqe_down = _qqe_fast - atr_rsi * factor

    qqe_slow = np.zeros(len(df))
    for i in range(1, len(df)):
        if qqe_up[i] < (qqe_slow[i - 1] if not np.isnan(qqe_slow[i - 1]) else 0):
            qqe_slow[i] = qqe_up[i]
        elif _qqe_fast[i] > (
            qqe_slow[i - 1] if not np.isnan(qqe_slow[i - 1]) else 0
        ) and _qqe_fast[i - 1] < (
            qqe_slow[i - 1] if not np.isnan(qqe_slow[i - 1]) else 0
        ):
            qqe_slow[i] = qqe_down[i]
        elif qqe_down[i] > (qqe_slow[i - 1] if not np.isnan(qqe_slow[i - 1]) else 0):
            qqe_slow[i] = qqe_down[i]
        elif _qqe_fast[i] < (
            qqe_slow[i - 1] if not np.isnan(qqe_slow[i - 1]) else 0
        ) and _qqe_fast[i - 1] > (
            qqe_slow[i - 1] if not np.isnan(qqe_slow[i - 1]) else 0
        ):
            qqe_slow[i] = qqe_up[i]
        else:
            qqe_slow[i] = qqe_slow[i - 1]

    df["qqe_slow"] = qqe_slow
    return df
