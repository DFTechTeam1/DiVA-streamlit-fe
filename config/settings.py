import streamlit as st
from pathlib import Path

class Setting:
    def __init__(self):
        self.mount_dir = self._resolve_mount_dir()

    def _resolve_mount_dir(self) -> Path:
        return Path(__file__).resolve().parents[2] / 'DiVA-streamlit-be' / 'mount'

    def page_setup(self, page_title: str = "DiVA", page_icon: str = "images/logo white - alt 2-01.png", layout: str = 'wide'):
        st.set_page_config(layout=layout, page_title=page_title, page_icon=page_icon)

    def remove_deploy_btn(self):
        st.markdown(
            """
            <style>
                #MainMenu, footer, .stAppDeployButton, #stDecoration {
                    visibility: hidden;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def session_state(self):
        defaults = {
            'encoded_image': None,
            'threshold': 0.3,
            'page': 1,
            'similar_image': None,
            'total_page': 1,
            'loading': False,
        }
        for key, default in defaults.items():
            st.session_state.setdefault(key, default)
