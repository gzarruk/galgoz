from galgoz import Galgoz, DATA_FOLDER
import pandas as pd
from pathlib import Path

gz = Galgoz()


def test_fetch_instruments():
    instruments = gz.fetch_instruments()
    instruments_dict = {instrument["name"]: instrument for instrument in instruments}
    assert len(instruments) > 0
    assert "GBP_JPY" in instruments_dict


def test_store_data():
    gz.instrument = "EUR_USD"
    gz.store_data(date_from="2024-12-17T00:00:00Z", date_to="2024-12-18T00:00:00Z")
    old_file = Path(DATA_FOLDER) / "EUR_USD_H1.pkl"
    new_file = Path(DATA_FOLDER) / "file_for_testing.pkl"
    old_file.rename(new_file)
    assert Path(new_file).exists(), f"File {new_file} does not exist"
    
    # Retreive the file_for_testing.pkl as a dataframe and check that the length is > 0
    df = pd.read_pickle(new_file)
    assert len(df) > 0, "Dataframe is empty"
    
    
    
if __name__ == "__main__":
    test_store_data()
