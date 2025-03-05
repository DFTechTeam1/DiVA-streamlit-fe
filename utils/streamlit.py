import asyncio
import base64
import streamlit as st
from typing import Union
from PIL import Image
from utils.logger import logging
from utils.diva import DiVAConnector
from utils.helper import CustomHelper


class StreamlitConfiguration:
    def __init__(self) -> None:
        self.diva_connector = DiVAConnector()
        self.helper = CustomHelper()

    def update_title(self) -> None:
        st.set_page_config(
            layout="wide",
            page_title="DiVA",
            page_icon="images/logo white - alt 2-01.png",
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
            st.session_state["threshold"]: float = 0.3

        if "page" not in st.session_state:
            st.session_state["page"]: int = 1

        if "image_per_page" not in st.session_state:
            st.session_state["image_per_page"]: int = 100

        if "prediction_label" not in st.session_state:
            st.session_state["prediction_label"]: list = None

        if "raw_prediction_label" not in st.session_state:
            st.session_state["raw_prediction_label"]: list = None

        if "raw_total_page" not in st.session_state:
            st.session_state["raw_total_page"]: int = None

        if "similar_image" not in st.session_state:
            st.session_state["similar_image"]: list = []

        if "image_uploaded_once" not in st.session_state:
            st.session_state["image_uploaded_once"]: bool = False

        if "image_filename" not in st.session_state:
            st.session_state["image_filename"]: str = False

    def sidebar(self) -> None:
        with st.sidebar:
            self.show_logo()
            st.markdown(
                "<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True
            )
            st.header(body="DiVA", help="DiVA stands for DFactory Image Retrieval")
            st.divider()

            is_image_uploaded = bool(st.session_state["encoded_image"])

            threshold = self.number_input(
                label="Accuracy threshold",
                min_value=0.1,
                max_value=1.0,
                default_value=0.3,
                description="Set the minimum accuracy required for retrieval results. A higher value ensures more precise matches, while a lower value allows for broader results. The threshold ranges from 0.1 (less strict) to 1.0 (highly strict).",
                disabled=is_image_uploaded,
            )

            st.session_state["threshold"] = threshold

            if st.session_state["encoded_image"] and st.session_state["image_filename"]:
                st.write("##### Uploaded image")
                self.render_uploaded_image(
                    encoded_image=st.session_state["encoded_image"],
                    filename=st.session_state["image_filename"],
                )

            images = st.session_state["similar_image"]

            if images:
                is_total_page_reached = (
                    True
                    if int(st.session_state["raw_total_page"])
                    == int(st.session_state["page"])
                    else False
                )
                if is_total_page_reached:
                    st.warning("Reached maximum page.")

                self.custom_btn(
                    label="Load more",
                    description="Load more similar images.",
                    on_click=self.handle_load_more_btn,
                    disabled=is_total_page_reached,
                )

    def number_input(
        self,
        label: str,
        min_value: Union[int, float],
        max_value: Union[int, float],
        default_value: Union[int, float],
        description: str,
        disabled: bool = False,
    ) -> Union[int, float]:
        return st.number_input(
            label=label,
            min_value=min_value,
            max_value=max_value,
            value=default_value,
            help=description,
            disabled=disabled,
        )

    def select_box(self, label: str, options: list, disabled: bool = False) -> str:
        return st.selectbox(label=label, options=options, disabled=disabled)

    def custom_btn(
        self,
        label: str,
        description: str,
        on_click: callable = None,
        disabled: bool = False,
    ) -> int:
        return st.button(
            label=label, help=description, disabled=disabled, on_click=on_click
        )

    def handle_load_more_btn(self) -> None:
        st.session_state["page"] += 1

        with st.spinner("Fetching prediction..."):
            response = self.fetch_similar_image()

        st.session_state["similar_image"].extend(response["data"]["similar_image"])

    def fetch_similar_image(self) -> dict:
        return asyncio.run(
            self.diva_connector.grab_similar(
                encoded_image=st.session_state["encoded_image"],
                threshold=st.session_state["threshold"],
                page=st.session_state["page"],
                image_per_page=st.session_state["image_per_page"],
                prediction_label=st.session_state["prediction_label"],
            )
        )

    def render_uploaded_image(self, encoded_image: str, filename: str) -> None:
        logging.info("Rendering uploaded image.")
        decoded_image = base64.b64decode(encoded_image)
        st.image(decoded_image, caption=f"{filename}", use_container_width=True)

    def render_predicted_label(self, predicted_label: dict) -> None:
        logging.info("Rendering predicted label.")
        converted = self.helper.convert_dataframe(data=predicted_label)
        st.text("Prediction Labels")
        st.bar_chart(data=converted, x="Label", y="Confidence")

    def render_similar_image(self) -> None:
        logging.info("Rendering similar images.")
        start_time = self.helper.local_time()
        images = st.session_state["similar_image"]
        images.sort(key=lambda x: x["accuracy"], reverse=True)

        if not images and st.session_state["encoded_image"]:
            st.warning("No similar images found.")

        if images:
            st.write("#### Similar Image")
            st.divider()

        with st.spinner("Loading similar images..."):
            num_columns = 3
            for i in range(0, len(images), num_columns):
                cols = st.columns(num_columns)
                for j, col in enumerate(cols):
                    if i + j < len(images):
                        image_data = images[i + j]
                        image_path = image_data["filepath"]
                        accuracy = image_data["accuracy"]

                        try:
                            image = Image.open(image_path)
                            col.image(image, use_container_width=True)
                        except Exception:
                            col.error(f"Failed to load image: {image_path[6:]}")

                        col.caption(f"Path: {image_path[6:]}")
                        col.caption(f"Accuracy: {accuracy:.2f}")
        if images:
            is_total_page_reached = (
                True
                if int(st.session_state["raw_total_page"])
                == int(st.session_state["page"])
                else False
            )
            if is_total_page_reached:
                st.warning("Reached maximum page.")

        end_time = self.helper.local_time()
        elapsed_time = end_time - start_time
        logging.info(f"Elapsed rendering time time: {elapsed_time}")

    def image_uploader(self) -> None:
        st.write("#### Search data by image")
        uploaded_image = st.file_uploader(
            label="Upload image file",
            help="Accept only 1 image data with extensions such as 'jpeg', 'jpg', 'png'.",
            type=["jpeg", "jpg", "png"],
            accept_multiple_files=False,
        )

        col1, col2 = st.columns(2)

        if uploaded_image:
            logging.info(f"Uploaded image {uploaded_image.name}.")
            image_bytes = uploaded_image.read()
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            st.session_state["image_filename"] = uploaded_image.name

            if st.session_state["encoded_image"] != encoded_image:
                st.session_state["encoded_image"] = encoded_image
                st.session_state["similar_image"] = []
                st.session_state["image_uploaded_once"] = False

            with col1:
                self.render_uploaded_image(
                    encoded_image=encoded_image, filename=uploaded_image.name
                )

            if not st.session_state["image_uploaded_once"]:
                with col2:
                    with st.spinner("Fetching prediction..."):
                        response_api = self.fetch_similar_image()

                if response_api:
                    st.session_state["raw_total_page"] = response_api["data"][
                        "total_page"
                    ]
                    st.session_state["raw_prediction_label"] = response_api["data"][
                        "prediction_label"
                    ]
                    st.session_state["similar_image"] = response_api["data"][
                        "similar_image"
                    ]
                    st.session_state["prediction_label"] = (
                        self.helper.convert_predicted_label(
                            response_api["data"]["prediction_label"]
                        )
                    )
                    st.session_state["image_uploaded_once"] = True

                else:
                    st.error("Failed predicting image.")
            with col2:
                self.render_predicted_label(
                    predicted_label=st.session_state["raw_prediction_label"]
                )
        else:
            st.warning("Please upload an image")
            st.session_state["encoded_image"] = None
            st.session_state["similar_image"] = []
            st.session_state["image_filename"] = None
            st.session_state["image_uploaded_once"] = False

    def main(self) -> None:
        self.update_title()
        self.remove_deploy_btn()
        self.session_state()
        self.image_uploader()
        self.sidebar()
        self.render_similar_image()
