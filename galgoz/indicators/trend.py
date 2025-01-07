import pandas as pd
from scipy import signal  # type: ignore


def sg(data: pd.Series, len: int = 250, order: int = 2) -> pd.Series:
    res = signal.savgol_filter(data.values, window_length=len, polyorder=order)
    trend = pd.Series(res, index=data.index)
    return trend
