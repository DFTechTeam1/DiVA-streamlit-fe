import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.streamlit import DiVA
from config.settings import Setting
from config.view import View


def main():
	config = Setting()
	view = View()
	app = DiVA(config, view)
	app.run()


if __name__ == '__main__':
	main()
