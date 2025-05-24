from pytz import timezone
from datetime import datetime


def local_time(zone: str = 'Asia/Jakarta') -> datetime:
	return datetime.now(timezone(zone)).replace(tzinfo=None)


def to_page(total_page: int) -> list:
	return [f'Page {i + 1}' for i in range(total_page)]


def to_num(page: str) -> int:
	return int(page.split()[-1])
