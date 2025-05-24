import os
import asyncio
import base64
from pathlib import Path

import streamlit as st

from utils.logger import logging
from utils.diva import fetch
from utils.helper import local_time, to_num, to_page


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
                        relative = img_data['path'].replace(mount_dir, '')
                        url = img_data['image_stream'].replace('http://0.0.0.0:14000', 'http://localhost:14000')

                        col.image(url, use_container_width=True)
                        col.write(f'**Project path: {relative}**')
                        col.write(f'*Similarity score: {img_data["score"]}%*')

            logging.info(f'Rendered {len(sorted_imgs)} similar images on page {page}.')
        else:
            st.warning('Similar images not found.')


class DiVA:
    def __init__(self):
        self.mount_dir = os.path.join(Path(__file__).resolve().parents[1], 'mount')
        self.page_config()
        self.hide_deploy_ui()
        self.init_session_state()

    def page_config(self):
        st.set_page_config(layout='wide', page_title='DiVA', page_icon='images/logo white - alt 2-01.png')

    def hide_deploy_ui(self):
        st.markdown("""
            <style>
                #MainMenu, footer, .stAppDeployButton, #stDecoration {visibility: hidden;}
            </style>
        """, unsafe_allow_html=True)

    def init_session_state(self):
        defaults = {
            'encoded_image': None,
            'threshold': 0.3,
            'page': 1,
            'similar_image': None,
            'total_page': 0,
            'page_changed': False,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def render_sidebar(self):
        with st.sidebar:
            DivaViewRenderer.render_logo()
            st.markdown("<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True)
            st.header('DiVA', help='DiVA stands for DFactory Image Retrieval')
            st.divider()

            self.image_uploader()

            threshold = st.slider(
                label='Minimum classification accuracy',
                min_value=0.1,
                max_value=0.7,
                value=0.3,
                help='Set the minimum accuracy required for retrieval results.',
            )
            if threshold != st.session_state['threshold']:
                logging.info(f'Threshold changed from {st.session_state["threshold"]} to {threshold}')
                st.session_state['page'] = 1
                st.session_state['threshold'] = threshold
                print(st.session_state['total_page'])
                print(st.session_state['page'])
                print(st.session_state['threshold'])
                asyncio.run(self.update_similar_images())

            if st.session_state['encoded_image']:
                page = st.selectbox(
                    label='Page',
                    options=to_page(int(st.session_state['total_page'])),
                    index=st.session_state['page'] - 1,
                    help='Select the page number to view similar images.',
                    disabled=st.session_state['similar_image'] is None
                )

                if page != f"Page {st.session_state['page']}":
                    st.session_state['page'] = to_num(page)
                    st.session_state['page_changed'] = True

    async def fetch_similar_image(self):
        start_time = local_time()
        data, response_code = await fetch(
            encoded_image=st.session_state['encoded_image'],
            threshold=st.session_state['threshold'],
            page=st.session_state['page'],
        )
        logging.info(f"Elapsed fetching time: {local_time() - start_time}")
        return data, response_code

    def handle_threshold_change(self):
        st.session_state['page'] = 1
        asyncio.run(self.update_similar_images())

    def handle_image_upload(self, uploaded_image):
        logging.info(f'Uploaded image {uploaded_image.name}')
        encoded = base64.b64encode(uploaded_image.read()).decode('utf-8')
        st.session_state['encoded_image'] = encoded
        st.session_state['page'] = 1
        DivaViewRenderer.render_uploaded_image(encoded, uploaded_image.name)
        with st.spinner('Searching for similar images...'):
            asyncio.run(self.update_similar_images())

    async def update_similar_images(self):
        response, code = await self.fetch_similar_image()
        if code == 200:
            st.session_state.update({
                'total_page': response['data']['total_page'],
                'similar_image': response['data']['similar_image']
            })
        else:
            st.warning('Similar imaes not found, please lower the threshold.')
            st.session_state['similar_image'] = None

    def render_similar_images(self):
        if st.session_state.get('page_changed', False):
            with st.spinner('Loading new page...'):
                asyncio.run(self.update_similar_images())
            st.session_state['page_changed'] = False

        if st.session_state['encoded_image']:
            DivaViewRenderer.render_similar_images(
                st.session_state.get('similar_image', []),
                st.session_state['page'],
                self.mount_dir
            )

    def image_uploader(self):
        uploaded_image = st.file_uploader(
            'Upload image file',
            help='Accepts jpeg, jpg, png.',
            type=['jpeg', 'jpg', 'png'],
            accept_multiple_files=False
        )
        if uploaded_image:
            self.handle_image_upload(uploaded_image)

    def maintenance_mode(self):
        st.warning('The DiVA application is currently undergoing maintenance.')
        st.stop()

    def run(self):
        self.render_sidebar()
        self.render_similar_images()
        # self.maintenance_mode()