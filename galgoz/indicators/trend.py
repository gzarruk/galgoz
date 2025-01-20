import pandas as pd
import numpy as np
from scipy import signal  # type: ignore
from ..indicators.base import Indicator
from whittaker_eilers import WhittakerSmoother


class SG(Indicator):
    window: int = 250
    order: int = 2
    line_color: str = "blue"

    def __init__(
        self, data: pd.Series, window: int = window, order: int = order, **kwargs
    ):
        super().__init__(name="Savitzky-Golay Filter", data=data)
        self.window = window
        self.order = order
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Savitzky-Golay Filter (window={self.window}, order={self.order})"

    def run(self):
        res = signal.savgol_filter(
            self.data.values, window_length=self.window, polyorder=self.order
        )
        self.output = pd.Series(res, index=self.data.index, name="SG")


class SGrt(Indicator):
    window: int = 250
    order: int = 2
    line_color: str = "blue"

    def __init__(
        self, data: pd.Series, window: int = window, order: int = order, **kwargs
    ):
        super().__init__(name="Savitzky-Golay Filter", data=data)
        self.window = window
        self.order = order
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Savitzky-Golay Filter (window={self.window}, order={self.order})"

    def run(self):
        res = self.data.rolling(window=self.window, min_periods=self.window).apply(
            lambda x: signal.savgol_filter(
                x, window_length=self.window, polyorder=self.order
            )[-1],
            raw=True,
        )
        self.output = pd.Series(res, index=self.data.index, name="SG")


class WS(Indicator):
    lmbda: float = 1e6
    order: int = 2
    optimal: bool = False

    def __init__(
        self,
        data: pd.Series,
        lmbda: float = lmbda,
        order: int = order,
        optimal: bool = optimal,
        **kwargs,
    ):
        super().__init__(name="Whittaker Smoother", data=data)
        self.lmbda = lmbda
        self.order = order
        self.optimal = optimal
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Whittaker Smoother (lambda={self.lmbda}, order={self.order})"

    def run(self):
        ws = WhittakerSmoother(
            lmbda=self.lmbda, order=self.order, data_length=len(self.data)
        )
        if self.optimal:
            res = ws.smooth_optimal(self.data.values)
        res = ws.smooth(self.data)
        self.output = pd.Series(res, index=self.data.index, name="WSmooth")


class WSrt(Indicator):
    lmbda: float = 1e6
    order: int = 2

    def __init__(
        self,
        data: pd.Series,
        lmbda: float = lmbda,
        order: int = order,
        **kwargs,
    ):
        super().__init__(name="Whittaker Smoother", data=data)
        self.lmbda = lmbda
        self.order = order
        if data is not None:
            self.run()
        self._update_attributes(kwargs)

    def __str__(self):
        return f"Whittaker Smoother (lambda={self.lmbda}, order={self.order})"

    def run(self):
        res = pd.Series(index=self.data.index, data=np.nan)
        for i in range(self.order + 1, len(self.data)):
            data_for_ws = self.data.iloc[:i].values
            ws = WhittakerSmoother(
                lmbda=self.lmbda, order=self.order, data_length=len(data_for_ws)
            )
            res.iloc[i] = ws.smooth(data_for_ws)[-1]

        self.output = pd.Series(res, index=self.data.index, name="WSmooth")
