import pandas as pd
from scipy import signal
import numpy as np


def sg_trend(data: pd.Series, len: int = 250, order: int = 2) -> np.ndarray:
    trend = signal.savgol_filter(data.values, window_length=len, polyorder=order)
    res = pd.Series(trend, index=data.index)
    return res
