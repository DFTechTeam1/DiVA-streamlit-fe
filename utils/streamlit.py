import os
import asyncio
import base64
import streamlit as st
from typing import Union, Literal
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
                #MainMenu, footer, .stAppDeployButton, #stDecoration {visibility: hidden;}
            </style>
            """,
            unsafe_allow_html=True,
        )

    def session_state(self) -> None:
        defaults = {
            "encoded_image": None,
            "threshold": 0.3,
            "page": 1,
            "filename": None,
            "prediction": None,
            "raw_prediction": None,
            "raw_total_page": None,
            "similar_image": [],
            "image_uploaded_once": False,
            "image_filename": None,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def sidebar(self) -> None:
        with st.sidebar:
            self.show_logo()
            st.markdown(
                "<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True
            )
            st.header("DiVA", help="DiVA stands for DFactory Image Retrieval")
            st.divider()

            self.image_uploader()
            is_image_uploaded = bool(st.session_state["encoded_image"])

            threshold = self.slider_input(
                label="Minimum classification accuracy",
                min_value=0.1,
                max_value=0.7,
                default_value=0.15,
                description="Set the minimum accuracy required for retrieval results. A higher value ensures more precise matches, while a lower value allows for broader results. The threshold ranges from 0.1 (less strict) to 1.0 (highly strict).",
                disabled=is_image_uploaded,
            )

            st.session_state["threshold"] = threshold

            if st.session_state["similar_image"]:
                raw_page = int(st.session_state["raw_total_page"])
                page_options = self.helper.convert_page(total_page=raw_page)
                page = self.select_box(label="Page", options=page_options)
                if page != st.session_state["page"]:
                    st.session_state["page"] = page

                    with st.spinner("Fetching more images..."):
                        response, status_code = asyncio.run(self.fetch_similar_image())

                    if status_code == 200:
                        st.session_state["similar_image"] = response["data"][
                            "similar_image"
                        ]
                        st.session_state["raw_total_page"] = response["data"][
                            "total_page"
                        ]
                    else:
                        st.error("Error loading more similar images.")

    def slider_input(
        self,
        label: str,
        min_value: Union[int, float],
        max_value: Union[int, float],
        default_value: Union[int, float],
        description: str,
        disabled: bool = False,
    ) -> Union[int, float]:
        return st.slider(
            label,
            min_value,
            max_value,
            default_value,
            help=description,
            disabled=disabled,
        )

    def select_box(
        self,
        label: str,
        options: list,
        disabled: bool = False,
        on_change: callable = None,
    ) -> int:
        page = st.selectbox(
            label=label, options=options, on_change=on_change, disabled=disabled
        )
        page_num = self.helper.convert_to_num(page=page)
        return page_num

    def custom_btn(
        self,
        label: str,
        description: str,
        on_click: callable = None,
        disabled: bool = False,
        type: Literal["primary", "secondary", "tertiary"] = "secondary",
    ) -> None:
        st.button(
            label, help=description, disabled=disabled, on_click=on_click, type=type
        )

    async def fetch_similar_image(self) -> dict:
        start_time = self.helper.local_time()
        data, response_code = await self.diva_connector.grab_similar(
            filename=st.session_state["filename"],
            encoded_image=st.session_state["encoded_image"],
            threshold=st.session_state["threshold"],
            page=st.session_state["page"],
            prediction=st.session_state["prediction"],
        )
        end_time = self.helper.local_time()
        elapsed_time = end_time - start_time
        logging.info(f"Elapsed fetching similar image time: {elapsed_time}")

        return data, response_code

    def handle_change_page(self) -> bool:
        if st.session_state["page"] != st.session_state["page"]:
            return True
        return False

    def render_uploaded_image(self) -> None:
        st.image(
            base64.b64decode(st.session_state["encoded_image"]),
            caption=st.session_state["image_filename"],
            use_container_width=True,
        )
        logging.info(f"Rendered image {st.session_state['image_filename']}.")

    def render_similar_image(self) -> None:
        seen = set()
        unique_images = []
        for img in st.session_state["similar_image"]:
            img_tuple = tuple(img.items())
            if img_tuple not in seen:
                seen.add(img_tuple)
                unique_images.append(img)

        images = sorted(unique_images, key=lambda x: x["score"], reverse=True)

        if not images and st.session_state["encoded_image"]:
            st.warning("No similar images found. Try lowering the accuracy threshold.")

        if images:
            logging.info("Rendering similar images.")
            with st.spinner("Rendering images..."):
                total_page = int(st.session_state["raw_total_page"])
                current_page = int(st.session_state["page"])
                total_page - current_page

                st.write(f"#### Similar Images (Page {st.session_state['page']})")
                st.divider()

                num_columns = 3
                for i in range(0, len(images), num_columns):
                    cols = st.columns(num_columns)
                    for j, col in enumerate(cols):
                        if i + j < len(images):
                            image_data = images[i + j]
                            image_path = image_data["path"]
                            directory_path = os.path.dirname(image_path)
                            relative_path = directory_path.replace(
                                "/home/dfactory/Project/DiVA-streamlit-be/mount/", ""
                            )
                            removed_preview = relative_path.replace("/PREVIEW", "")
                            accuracy = int(float(image_data["score"]) * 100)
                            stream_image = image_data["image_stream"]

                            col.image(stream_image, use_container_width=True)
                            col.write(f"**Path: {removed_preview}**")
                            col.write(f"*Similarity score: {accuracy}%*")

                logging.info(f"Loaded page: {st.session_state['page']}.")
                logging.info(f"Rendered {len(images)} similar images.")

    def image_uploader(self) -> None:
        uploaded_image = st.file_uploader(
            "Upload image file",
            help="Accepts single image file with extension jpeg, jpg, png.",
            type=["jpeg", "jpg", "png"],
            accept_multiple_files=False,
        )

        if uploaded_image:
            logging.info(f"Uploaded image {uploaded_image.name}.")
            image_bytes = uploaded_image.read()
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")

            if st.session_state["encoded_image"] != encoded_image:
                st.session_state.update(
                    {
                        "filename": uploaded_image.name,
                        "encoded_image": encoded_image,
                        "image_filename": uploaded_image.name,
                        "similar_image": [],
                        "image_uploaded_once": False,
                        "page": 1,
                    }
                )

            st.write("##### Uploaded image")
            self.render_uploaded_image()

            if not st.session_state["image_uploaded_once"]:
                with st.spinner("Searching for similar images..."):

                    async def fetch_prediction():
                        response_api, response_code = await self.fetch_similar_image()
                        if response_code == 200:
                            st.session_state.update(
                                {
                                    "raw_total_page": response_api["data"][
                                        "total_page"
                                    ],
                                    "raw_prediction": response_api["data"][
                                        "prediction"
                                    ],
                                    "similar_image": response_api["data"][
                                        "similar_image"
                                    ],
                                    "prediction": response_api["data"]["prediction"],
                                    "image_uploaded_once": True,
                                }
                            )

                    asyncio.run(fetch_prediction())
        else:
            st.warning("Please upload an image.")
            st.session_state.update(
                {
                    "filename": None,
                    "encoded_image": None,
                    "threshold": 0.3,
                    "page": 1,
                    "prediction": None,
                    "query_image": 100,
                    "raw_predictions": None,
                    "raw_total_page": None,
                    "similar_image": [],
                    "image_uploaded_once": False,
                    "image_filename": None,
                }
            )

    def maintenance(self) -> None:
        st.warning(
            "The DiVA application is currently undergoing maintenance. Please check back later."
        )
        st.stop()

    def main(self) -> None:
        self.update_title()
        self.remove_deploy_btn()
        self.session_state()
        self.sidebar()
        self.render_similar_image()
        # self.maintenance()
