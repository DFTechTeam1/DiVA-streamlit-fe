import pandas as pd
from pandas.core.frame import DataFrame


def convert_dataframe(data: dict) -> DataFrame:
    df = pd.DataFrame(list(data.items()), columns=["Label", "Confidence"])
    df["Confidence"] = df["Confidence"] * 100
    return df
