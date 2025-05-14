from pytz import timezone
from datetime import datetime


class CustomHelper:
    def local_time(self, zone: str = "Asia/Jakarta") -> datetime:
        return datetime.now(timezone(zone)).replace(tzinfo=None)

    def convert_page(self, total_page: int) -> list:
        return [f"Page {i + 1}" for i in range(total_page)]

    def convert_to_num(self, page: str) -> int:
        return int(page.split()[-1])
