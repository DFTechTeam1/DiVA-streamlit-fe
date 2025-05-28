import os
import asyncio
import base64
import streamlit as st
from pathlib import Path
from utils.logger import logging
from utils.diva import fetch
from utils.helper import local_time, to_num, to_page
from utils.render import DivaViewRenderer


class DiVA:
	def __init__(self):
		self.mount_dir = Path(__file__).resolve().parents[2] / 'DiVA-streamlit-be' / 'mount'
		self.page_config()
		self.hide_deploy_ui()
		self.init_session_state()

	def page_config(self):
		st.set_page_config(layout='wide', page_title='DiVA', page_icon='images/logo white - alt 2-01.png')

	def hide_deploy_ui(self):
		st.markdown(
			"""
            <style>
                #MainMenu, footer, .stAppDeployButton, #stDecoration {visibility: hidden;}
            </style>
        """,
			unsafe_allow_html=True,
		)

	def init_session_state(self):
		defaults = {
			'encoded_image': None,
			'threshold': 0.3,
			'page': 1,
			'similar_image': None,
			'total_page': 1,
			'loading': False,
		}
		for key, value in defaults.items():
			if key not in st.session_state:
				st.session_state[key] = value

	def render_sidebar(self):
		with st.sidebar:
			DivaViewRenderer.render_logo()
			st.header('DiVA', help='DiVA stands for DFactory Image Retrieval')
			st.divider()
			self.image_uploader()

			if st.session_state['similar_image']:
				previous_page = st.session_state['page']
				page_options = to_page(st.session_state['total_page'])
				selected_page = st.selectbox(
					label='Page',
					options=page_options,
					help='Select the page number to view similar images.',
					disabled=st.session_state['loading'] is True,
				)

				current_page = to_num(selected_page)

				if current_page != previous_page:
					st.session_state['page'] = current_page
					asyncio.run(self.fetch_similar_image())

	def image_uploader(self):
		uploaded_image = st.file_uploader(
			'Upload image file', help='Accepts jpeg, jpg, png.', type=['jpeg', 'jpg', 'png'], accept_multiple_files=False
		)
		if uploaded_image:
			self.handle_image_upload(uploaded_image)
		else:
			st.session_state['encoded_image'] = None
			st.session_state['page'] = 1
			st.session_state['total_page'] = 1
			st.session_state['similar_image'] = None

	def handle_image_upload(self, uploaded_image):
		logging.info(f'Uploaded image {uploaded_image.name}')
		encoded = base64.b64encode(uploaded_image.read()).decode('utf-8')

		if st.session_state['encoded_image'] != encoded:
			logging.info('New image uploaded, updating session state.')
			st.session_state['encoded_image'] = encoded
			st.session_state['page'] = 1
			DivaViewRenderer.render_uploaded_image(encoded, uploaded_image.name)
			asyncio.run(self.fetch_similar_image())
		else:
			logging.info(f"Processing image {uploaded_image.name} again, but it's already in session state.")
			DivaViewRenderer.render_uploaded_image(encoded, uploaded_image.name)
			asyncio.run(self.fetch_similar_image())

	async def fetch_similar_image(self):
		logging.info(f'Proceeding request for image query {st.session_state["encoded_image"][:5]}.')
		start_time = local_time()
		st.session_state['loading'] = True
		data, response_code = await fetch(
			encoded_image=st.session_state['encoded_image'],
			threshold=st.session_state['threshold'],
			page=st.session_state['page'],
		)
		logging.info(f'Elapsed fetching time: {local_time() - start_time}')

		if response_code == 200:
			st.session_state.update({'total_page': data['data']['total_page'], 'similar_image': data['data']['similar_image']})
			logging.info(f'Rendered {len(data["data"]["similar_image"])} similar images on page {st.session_state["page"]}.')
		st.session_state['loading'] = False
		return data, response_code

	def render_similar_images(self):
		if st.session_state['encoded_image'] and st.session_state['similar_image']:
			DivaViewRenderer.render_similar_images(st.session_state['similar_image'], st.session_state['page'], self.mount_dir)
		elif not st.session_state['encoded_image']:
			st.info('Please upload an image to find similar images.')
		else:
			st.warning('Similar images not found.')

	def maintenance_mode(self):
		st.warning('The DiVA application is currently undergoing maintenance.')
		st.stop()

	def run(self):
		self.render_sidebar()
		self.render_similar_images()
		# self.maintenance_mode()
