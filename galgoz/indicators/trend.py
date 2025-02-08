import pandas as pd
import numpy as np
from scipy import signal  # type: ignore
from ..indicators.base import Indicator
import talib
from vectorbt import IndicatorFactory as IF


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
    window: int = 169
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


class SuperTrend(Indicator):
    atr_period: int = 14
    multiplier: float = 6.5
    line_color: str = "green"

    def __init__(
        self,
        data: pd.DataFrame,
        atr_period: int = atr_period,
        multiplier: float = multiplier,
        **kwargs,
    ):
        super().__init__(name=self.__class__.__name__, data=data)
        self.atr_period = atr_period
        self.multiplier = multiplier
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return (
            f"Supertrend (ATR period={self.atr_period}, multiplier={self.multiplier})"
        )

    def run(self):
        high = self.data["mid_h"]
        low = self.data["mid_l"]
        close = self.data["mid_c"]

        # Calculate ATR
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.atr_period).mean()

        # Calculate Supertrend
        hl2 = (high + low) / 2
        upper_band = hl2 + (self.multiplier * atr)
        lower_band = hl2 - (self.multiplier * atr)

        final_upper_band = upper_band.copy()
        final_lower_band = lower_band.copy()

        for i in range(1, len(self.data)):
            if close.iloc[i] > final_upper_band.iloc[i - 1]:
                final_upper_band.iloc[i] = upper_band.iloc[i]
            else:
                final_upper_band.iloc[i] = min(
                    upper_band.iloc[i], final_upper_band.iloc[i - 1]
                )

            if close.iloc[i] < final_lower_band.iloc[i - 1]:
                final_lower_band.iloc[i] = lower_band.iloc[i]
            else:
                final_lower_band.iloc[i] = max(
                    lower_band.iloc[i], final_lower_band.iloc[i - 1]
                )

        supertrend = pd.Series(index=self.data.index)
        in_uptrend = True
        for i in range(1, len(self.data)):
            if close.iloc[i] > final_upper_band.iloc[i - 1]:
                in_uptrend = True
            elif close.iloc[i] < final_lower_band.iloc[i - 1]:
                in_uptrend = False

            if in_uptrend:
                supertrend.iloc[i] = final_lower_band.iloc[i]
            else:
                supertrend.iloc[i] = final_upper_band.iloc[i]

        self.output = supertrend

    def update(self, new_data: pd.DataFrame | None):
        self.data = new_data
        self.run()

def _supertrend(data, atr_period=14, multiplier=6.5):
    # Instance of supertrend indicator used to generate the SuperTrend class
    res = supertrend(data.mid_h, data.mid_l, data.mid_c, atr_period, multiplier)
    return res

def supertrend(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
    multiplier: float = 6.5,
):
    """
    Calculate the Supertrend indicator. Adapted from https://medium.datadriveninvestor.com/superfast-supertrend-6269a3af0c2a

    Args:
        high (pd.Series): The high prices.
        low (pd.Series): The low prices.
        close (pd.Series): The close prices.
        period (int, optional): The ATR period. Defaults to 14.
        multiplier (float, optional): The multiplier. Defaults to 6.5.

    Returns:
        pd.Series: The Supertrend indicator.
    """
    # USe squeeze to convert 2D array to 1D. This is necessary for talib and vectorbt to work well together
    high_ = pd.Series(np.squeeze(high))
    low_ = pd.Series(np.squeeze(low))
    close_ = pd.Series(np.squeeze(close))
    avg_price = talib.MEDPRICE(high_.values.astype(float), low_.values.astype(float))
    atr = talib.ATR(
        high_.values.astype(float),
        low_.values.astype(float),
        close_.values.astype(float),
        period,
    )
    upper, lower = get_basic_bands(avg_price, atr, multiplier)
    upper = pd.Series(upper, index=close_.index)
    lower = pd.Series(lower, index=close_.index)
    trend, direction, long_, short = get_final_bands(close_, upper, lower)
    return trend, direction, long_, short


def get_basic_bands(med_price, atr, multiplier):
    matr = multiplier * atr
    upper = med_price + matr
    lower = med_price - matr
    return upper, lower


def get_final_bands(close, upper, lower):
    trend = pd.Series(np.full(close.shape, np.nan), index=close.index)
    dir_ = pd.Series(np.full(close.shape, 1), index=close.index)
    long_ = pd.Series(np.full(close.shape, np.nan), index=close.index)
    short = pd.Series(np.full(close.shape, np.nan), index=close.index)

    for i in range(1, close.shape[0]):
        if close.iloc[i] > upper.iloc[i - 1]:
            dir_.iloc[i] = 1
        elif close.iloc[i] < lower.iloc[i - 1]:
            dir_.iloc[i] = -1
        else:
            dir_.iloc[i] = dir_.iloc[i - 1]
            if dir_.iloc[i] > 0 and lower.iloc[i] < lower.iloc[i - 1]:
                lower.iloc[i] = lower.iloc[i - 1]
            if dir_.iloc[i] < 0 and upper.iloc[i] > upper.iloc[i - 1]:
                upper.iloc[i] = upper.iloc[i - 1]

        if dir_.iloc[i] > 0:
            trend.iloc[i] = long_.iloc[i] = lower.iloc[i]
        else:
            trend.iloc[i] = short.iloc[i] = upper.iloc[i]

    return trend, dir_, long_, short
