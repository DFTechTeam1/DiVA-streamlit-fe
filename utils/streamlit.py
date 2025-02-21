import asyncio
import base64
import streamlit as st
from typing import Optional
from utils.logger import logging
from utils.diva import DiVAConnector
from pandas.core.frame import DataFrame
from utils.helper import convert_dataframe



class StreamlitConfiguration:
    def __init__(self) -> None:
        self.diva_connector = DiVAConnector()
        self.update_title()
        self.remove_deploy_btn()
        self.session_state()

    def update_title(self) -> None:
        st.set_page_config(
            layout="wide", 
            page_title="DiVA",
            page_icon="images/logo white - alt 2-01.png"
        )

    def show_logo(self) -> None:
        img_path = "images/Logo - Black.png"
        
        with open(img_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode("utf-8")

        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <img src="data:image/png;base64,{encoded_string}" width="200">
            </div>
            """,
            unsafe_allow_html=True,
        )



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
            st.session_state["page"]: int = 1

        if "image_per_page" not in st.session_state:
            st.session_state["image_per_page"]: int = None

        if "prediction_label" not in st.session_state:
            st.session_state["prediction_label"]: dict = None
            
        if "similar_image" not in st.session_state:
            st.session_state["similar_image"]: list = None

    def sidebar(self) -> None:
        with st.sidebar:
            self.show_logo()
            st.markdown("<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True)
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
                disabled=True if st.session_state["encoded_image"] else False,
            )

            st.session_state["threshold"] = threshold
            st.session_state["image_per_page"] = image_per_page

    def number_input(
        self,
        label: str,
        min_value: int | float,
        max_value: int | float,
        default_value: int | float,
        description: str,
        disabled: bool = False,
    ) -> int | float:
        return st.number_input(
            label=label,
            min_value=min_value,
            max_value=max_value,
            value=default_value,
            help=description,
            disabled=disabled,
        )
        
    def fetch_results(self) -> Optional[dict]:
        with st.spinner("Searching for similar images..."):
            try:
                data = asyncio.run(
                    self.diva_connector.grab_similar(
                        encoded_image=st.session_state["encoded_image"],
                        threshold=st.session_state["threshold"],
                        page=st.session_state["page"],
                        image_per_page=st.session_state["image_per_page"],
                        prediction_label=st.session_state["prediction_label"],
                    )
                )
                
                return data

            except Exception as e:
                logging.error(f"Error during API request: {e}")
                
        return None
    
    
    def render_upload(self, encoded_image: str, filename: str) -> None:
        decoded_image = base64.b64decode(encoded_image)
        st.image(decoded_image, caption=f"{filename}")
        
        
    def render_prediction(self, dataframe: DataFrame, x_column: str, y_column: str) -> None:
        st.text("Prediction Labels")
        st.bar_chart(data=dataframe, x=x_column, y=y_column)
    
    
    def image_uploader(self) -> None:
        st.write("###### Search data by image")
        uploaded_image = st.file_uploader(
            label="Upload image file",
            help="Accept only 1 image data with extensions such as 'jpeg', 'jpg', 'png'.",
            type=["jpeg", "jpg", "png"],
            accept_multiple_files=False
        )
        if uploaded_image:
            logging.info(f"Uploaded image {uploaded_image.name}.")
            
            col1, col2 = st.columns(2)
            
            with st.container():    
                image_bytes = uploaded_image.read()
                encoded_image = base64.b64encode(image_bytes).decode("utf-8")
                
                with col1:
                    self.render_upload(encoded_image=encoded_image, filename=uploaded_image.name)
                    
                st.session_state["encoded_image"] = encoded_image
                response = self.fetch_results()        
                
                
                if response:
                    st.session_state["prediction_label"] = list(response["data"]["prediction_label"].keys())
                    st.session_state["similar_image"] = response["data"]["similar_image"]
                    converted = convert_dataframe(data=response["data"]["prediction_label"])
                    
                    
                    with col2:
                        self.render_prediction(dataframe=converted, x_column="Label", y_column="Confidence")
                else:
                    st.error(body="Failed to predict image.")            
        else:
            logging.warning("No image uploaded.")
            st.session_state["encoded_image"] = None
            st.session_state["prediction_label"] = None
            st.session_state["similar_image"] = None

    def main(self) -> None:
        with st.container():
            self.image_uploader()
            self.sidebar()
