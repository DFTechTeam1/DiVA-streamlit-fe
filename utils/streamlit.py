import asyncio
import base64
import streamlit as st
from typing import Optional, Union
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
            st.session_state["encoded_image"] = None

        if "threshold" not in st.session_state:
            st.session_state["threshold"] = None

        if "page" not in st.session_state:
            st.session_state["page"] = 1

        if "image_per_page" not in st.session_state:
            st.session_state["image_per_page"] = 100

        if "prediction_label" not in st.session_state:
            st.session_state["prediction_label"] = None

        if "similar_image" not in st.session_state:
            st.session_state["similar_image"] = []

        if "base_model" not in st.session_state:
            st.session_state["base_model"] = "clip-ViT-B-32"

    def sidebar(self) -> None:
        with st.sidebar:
            self.show_logo()
            st.markdown(
                "<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True
            )
            st.header(body="DiVA", help="DiVA stands for DFactory Image Retrieval")
            st.divider()

            is_image_uploaded = bool(st.session_state.get("encoded_image"))

            threshold = self.number_input(
                label="Accuracy threshold",
                min_value=0.1,
                max_value=1.0,
                default_value=0.3,
                description="Set the minimum accuracy required for retrieval results. A higher value ensures more precise matches, while a lower value allows for broader results. The threshold ranges from 0.1 (less strict) to 1.0 (highly strict).",
                disabled=is_image_uploaded,
            )

            st.session_state["threshold"] = threshold

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

    def select_box(self, label: str, options: list, disabled: bool) -> str:
        return st.selectbox(label=label, options=options, disabled=disabled)

    def custom_btn(self, label: str, description: str, disabled: bool) -> int:
        return st.button(label=label, help=description, disabled=disabled)

    def fetch_similar_image(self) -> Optional[dict]:
        data = asyncio.run(
            self.diva_connector.grab_similar(
                base_model=st.session_state["base_model"],
                encoded_image=st.session_state["encoded_image"],
                threshold=st.session_state["threshold"],
                page=st.session_state["page"],
                image_per_page=st.session_state["image_per_page"],
                prediction_label=st.session_state["prediction_label"],
            )
        )

        if not data:
            logging.info("Failed to fetch similar images.")
            st.session_state["similar_image"] = []
            return None

        st.session_state["similar_image"] = data["data"]["similar_image"]
        return data

    def render_uploaded_image(self, encoded_image: str, filename: str) -> None:
        decoded_image = base64.b64decode(encoded_image)
        st.image(decoded_image, caption=f"{filename}", use_container_width=True)

    def render_predicted_label(self, predicted_label: dict) -> None:
        converted = self.helper.convert_dataframe(data=predicted_label)
        st.text("Prediction Labels")
        st.bar_chart(data=converted, x="Label", y="Confidence")

    def render_similar_image(self) -> None:
        images = st.session_state.get("similar_image", [])

        if not images and st.session_state["encoded_image"]:
            st.warning("No similar images found.")

        if st.session_state["similar_image"]:
            st.write("#### Similar Image")
            st.divider()

        with st.spinner("Loading similar images..."):
            num_columns = 5
            for i in range(0, len(images), num_columns):
                cols = st.columns(num_columns)
                for j, col in enumerate(cols):
                    if i + j < len(images):
                        image_data = images[i + j]
                        image_path = image_data["filepath"]
                        accuracy = image_data["accuracy"]

                        try:
                            with open(image_path, "rb") as img_file:
                                encoded_string = base64.b64encode(
                                    img_file.read()
                                ).decode("utf-8")
                            col.image(
                                f"data:image/png;base64,{encoded_string}",
                                use_container_width=True,
                            )
                        except Exception:
                            col.error(f"Failed to load image: {image_path[6:]}")

                        col.write(f"**Path:** {image_path[6:]}")
                        col.write(f"**Accuracy:** {accuracy:.2f}")

        self.custom_btn(
            label="Load more", description="Load more similar images", disabled=False
        )

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
            st.session_state["encoded_image"] = encoded_image

            with col1:
                self.render_uploaded_image(
                    encoded_image=encoded_image, filename=uploaded_image.name
                )
            with col2:
                with st.spinner("Fetching prediction..."):
                    response_api = self.fetch_similar_image()

            if response_api:
                with col2:
                    self.render_predicted_label(
                        predicted_label=response_api["data"]["prediction_label"]
                    )
            else:
                st.error("Failed predicting image.")
        else:
            logging.warning("No image uploaded.")
            st.warning("Please upload an image")
            st.session_state["encoded_image"] = None
            st.session_state["similar_image"] = []

    def main(self) -> None:
        self.update_title()
        self.remove_deploy_btn()
        self.session_state()
        self.image_uploader()
        self.render_similar_image()
        self.sidebar()
