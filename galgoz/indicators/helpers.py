from ..indicators.base import Indicator
import pandas as pd


class Hline(Indicator):
    yvalue: float = 0
    row: int = 2
    line: list[dict] = [dict(color="grey", width=1)]

    def __init__(self, data: pd.DataFrame, yvalue: float = yvalue, **kwargs):
        super().__init__(name="hline")
        self.yvalue = yvalue
        self._initialize_data(data, **kwargs)

    def __str__(self):
        return f"Horizontal Line (yvalue={self.yvalue})"

    def run(self, data: pd.DataFrame | None = None, **kwargs):
        if data is not None:
            self.output = pd.Series(
                [self.yvalue] * len(data), index=data.index, name="hline"
            )
        else:
            self.output = None
