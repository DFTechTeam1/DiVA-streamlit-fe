import base64
import streamlit as st
from utils.logger import logging

class DivaViewRenderer:
    @staticmethod
    def render_logo():
        with open('images/Logo - Black.png', 'rb') as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
        st.markdown(
            f"""
                <div style="display: flex; justify-content: center;">
                    <img src="data:image/png;base64,{encoded_string}" width="200">
                </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True)

    @staticmethod
    def render_uploaded_image(encoded_image, filename):
        st.image(
            base64.b64decode(encoded_image),
            caption=filename,
            use_container_width=True
        )

    @staticmethod
    def render_similar_images(images, page, mount_dir):
        seen = set()
        unique = []
        if images:
            unique = [img for img in images if tuple(img.items()) not in seen and not seen.add(tuple(img.items()))]

        sorted_imgs = sorted(unique, key=lambda x: x['score'], reverse=True)

        if sorted_imgs:
            st.spinner('Rendering images...')
            st.write(f"#### Similar Images (Page {page})")
            st.divider()

            for i in range(0, len(sorted_imgs), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(sorted_imgs):
                        img_data = sorted_imgs[i + j]
                        relative = img_data['path'].replace(str(mount_dir), "")
                        url = img_data['image_stream']

                        col.image(url, use_container_width=True)
                        col.write(f'**Project path: {relative}**')
                        col.write(f'*Similarity score: {img_data["score"]}%*')

            logging.info(f'Rendered {len(sorted_imgs)} similar images on page {page}.')
        else:
            st.warning('Similar images not found.')