import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils.streamlit import DiVA

diva = DiVA()
diva.run()
