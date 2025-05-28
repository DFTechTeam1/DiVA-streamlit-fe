import base64
import asyncio
from pathlib import Path
import streamlit as st

from utils.helper import local_time, to_num, to_page
from utils.logger import logging
from services.diva import fetch

class View:
    def render_logo(self, image_path: str = 'images/Logo - Black.png'):
        """Render DiVA logo in sidebar."""
        encoded_string = self._encode_image(image_path)
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <img src="data:image/png;base64,{encoded_string}" width="200">
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-bottom: 35px;'></div>", unsafe_allow_html=True)
        st.header('DiVA', help='DiVA stands for DFactory Image Retrieval')
        st.divider()

    def render_image_upload(self, encoded_image: str, filename: str):
        return st.image(base64.b64decode(encoded_image), caption=filename, use_container_width=True)

    def render_sidebar(self):
        with st.sidebar:
            self.render_logo()
            self._image_uploader()
            self._render_page_selector()

    def _image_uploader(self):
        uploaded_image = st.file_uploader(
            'Upload image file',
            help='Accepts jpeg, jpg, png.',
            type=['jpeg', 'jpg', 'png'],
            accept_multiple_files=False
        )
        if uploaded_image:
            self._handle_uploaded_image(uploaded_image)
        else:
            self._reset_session_state()

    def _handle_uploaded_image(self, uploaded_image):
        encoded = base64.b64encode(uploaded_image.read()).decode('utf-8')
        logging.info(f'Uploaded image: {uploaded_image.name}')

        if st.session_state['encoded_image'] != encoded:
            logging.info('New image uploaded, updating session state.')
            st.session_state['encoded_image'] = encoded
            st.session_state['page'] = 1
        else:
            logging.info('Same image detected, reprocessing.')

        self.render_image_upload(encoded, uploaded_image.name)
        asyncio.run(self._fetch_similar_images())

    def _reset_session_state(self):
        st.session_state.update({
            'encoded_image': None,
            'page': 1,
            'total_page': 1,
            'similar_image': None
        })

    def _render_page_selector(self):
        if st.session_state.get('similar_image'):
            previous_page = st.session_state['page']
            page_options = to_page(st.session_state['total_page'])
            selected_page = st.selectbox(
                label='Page',
                options=page_options,
                help='Select the page number to view similar images.',
                disabled=st.session_state['loading'],
            )
            current_page = to_num(selected_page)
            if current_page != previous_page:
                st.session_state['page'] = current_page
                asyncio.run(self._fetch_similar_images())

    async def _fetch_similar_images(self):
        logging.info(f'Fetching similar images for image starting with {st.session_state["encoded_image"][:5]}')
        st.session_state['loading'] = True
        start = local_time()
        data, code = await fetch(
            encoded_image=st.session_state['encoded_image'],
            threshold=st.session_state['threshold'],
            page=st.session_state['page']
        )
        logging.info(f'Elapsed time: {local_time() - start}')
        st.session_state['loading'] = False

        if code == 200:
            st.session_state.update({
                'similar_image': data['data']['similar_image'],
                'total_page': data['data']['total_page']
            })
            logging.info(f'Rendered {len(data["data"]["similar_image"])} similar images on page {st.session_state["page"]}')
        return data, code

    def render_similar_images(self, images: list, page: int, mount_dir: Path):
        seen = set()
        unique_images = [img for img in images if tuple(img.items()) not in seen and not seen.add(tuple(img.items()))]
        sorted_imgs = sorted(unique_images, key=lambda x: x['score'], reverse=True)

        if sorted_imgs:
            st.spinner('Rendering images...')
            st.write(f'#### Similar Images (Page {page})')
            st.divider()

            for i in range(0, len(sorted_imgs), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(sorted_imgs):
                        self._render_image_card(col, sorted_imgs[i + j], mount_dir)
        else:
            st.warning('Similar images not found.')

    def _render_image_card(self, col, img_data, mount_dir):
        relative_path = Path(img_data['path']).relative_to(mount_dir)
        project_name = relative_path.parents[1].name
        project_dir = '\\'*2 + str(relative_path.parents[1]).replace('/', '\\')
        url = img_data['image_stream']

        col.image(url)
        col.write(f'Project name: {project_name}')
        col.write(f'**Similarity: {img_data["score"]}%**')
        col.code(project_dir)

    def _encode_image(self, image_path: str) -> str:
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
