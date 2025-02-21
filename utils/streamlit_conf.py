import base64
import json
import streamlit as st

from io import BytesIO
from utils.logger import logging
from typing import Optional

class StreamlitConfiguration:
    def __init__(self) -> None:
        self.update_title()
        self.remove_deploy_btn()
        self.session_state()

    
    def update_title(self) -> None:
        st.set_page_config(layout="wide", page_title="DiVA")
    
    def remove_deploy_btn(self) -> None:
        st.markdown(
            """
            <style>
                .reportview-container {
                    margin-top: -2em;
                }
                #MainMenu {visibility: hidden;}
                .stAppDeployButton  {visibility:hidden;}
                footer {visibility: hidden;}
                #stDecoration {display:none;}
            </style>
            """,
            unsafe_allow_html=True,
        )
    
    def session_state(self) -> None:
        if "encoded_image" not in st.session_state:
            st.session_state["encoded_image"]: str = None
        
        if "threshold" not in st.session_state:
            st.session_state["threshold"]: float = None
            
        if "page" not in st.session_state:
            st.session_state["page"]: int = None
            
        if "image_per_page" not in st.session_state:
            st.session_state["image_per_page"]: int = None
            
        if "prediction_label" not in st.session_state:
            st.session_state["prediction_label"]: list[str] = None
            
            
    
    def sidebar(self) -> None:
        with st.sidebar:
            st.header(body="DiVA", help="Dfactory Image Retrieval")
            st.divider()
            
            image_per_page = self.number_input(
                label="Total retrieve image",
                min_value=1,
                max_value=200,
                default_value=100,
                description="Input total of image that you want to retrieve, accepted with minimum value is 1 and maximum value is 200.",
            )
            
            threshold = self.number_input(
                label="Accuracy threshold",
                min_value=0.1,
                max_value=1.0,
                default_value=0.8,
                description="Set the minimum accuracy required for retrieval results. A higher value ensures more precise matches, while a lower value allows for broader results. The threshold ranges from 0.1 (less strict) to 1.0 (highly strict).",
                disabled=True if st.session_state["encoded_image"] else False
            )
            
            st.session_state["threshold"] = threshold
            st.session_state["image_per_page"] = image_per_page
            
    
    def number_input(
        self, 
        label: str,
        min_value: int|float, 
        max_value: int|float, 
        default_value: int|float,
        description: str,
        disabled: bool = False
    ) -> int|float:
        return st.number_input(
                label=label,
                min_value=min_value,
                max_value=max_value,
                value=default_value,
                help=description,
                disabled=disabled
            )
        
    def image_uploader(self) -> None:
        st.write("#### Search data by image")
        uploaded_image = st.file_uploader(
            label="Upload image file",
            help="Accept only 1 image data with extensions such as 'jpeg', 'jpg', 'png'.",
            type=["jpeg", "jpg", "png"],
        )
        if uploaded_image:
            
            logging.info(f"Uploaded image {uploaded_image.name}.")
            image_bytes = uploaded_image.read()
                        
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            st.session_state["encoded_image"] = encoded_image[:10]
            
            decoded_image = base64.b64decode(encoded_image)
            st.image(decoded_image, caption=f"{uploaded_image.name}", width=400)
        else:
            logging.warning("No image uploaded.")
            st.session_state["encoded_image"] = None
                
    
    def main(self) -> None:
        with st.container():
            self.image_uploader()
            self.sidebar()
            st.write(st.session_state)
            print(st.session_state)
            