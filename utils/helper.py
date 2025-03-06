import pandas as pd
from pytz import timezone
from datetime import datetime
from pandas.core.frame import DataFrame


class CustomHelper:
    def convert_dataframe(self, data: dict) -> DataFrame:
        df = pd.DataFrame(list(data.items()), columns=["Label", "Confidence"])
        df["Confidence"] = df["Confidence"] * 100
        return df

    def convert_predicted_label(self, data: dict) -> list:
        return list(data.keys())

    def local_time(self, zone: str = "Asia/Jakarta") -> datetime:
        return datetime.now(timezone(zone)).replace(tzinfo=None)
