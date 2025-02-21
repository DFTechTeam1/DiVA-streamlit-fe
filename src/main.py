import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.streamlit import StreamlitConfiguration

streamlit = StreamlitConfiguration()
streamlit.main()
