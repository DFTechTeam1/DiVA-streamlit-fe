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

    def convert_page(self, total_page: int) -> list:
        return [f"Page {i + 1}" for i in range(total_page)]

    def convert_to_num(self, page: str) -> int:
        return int(page.split()[-1])
