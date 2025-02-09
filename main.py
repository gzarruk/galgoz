from galgoz import DATA_FOLDER
from galgoz.utils import set_data_index_and_time_str
from vectorbt import IndicatorFactory as IF
import pandas as pd
from galgoz.indicators.trend import supertrend

if __name__ == "__main__":
    data = pd.read_pickle(DATA_FOLDER / "GBP_JPY_H1.pkl")
    data = set_data_index_and_time_str(data)
    SSTT = IF(
        input_names=["high", "low", "close"],
        param_names=["period", "multiplier"],
        output_names=["trend", "dir", "long", "short"],
    ).from_apply_func(supertrend)

    st_vbt = SSTT.run(data.mid_h, data.mid_l, data.mid_c, period=14, multiplier=6.5)
    print(st_vbt)
