import streamlit as st
from config.settings import Setting
from config.view import View


class DiVA:
	def __init__(self, config: Setting, view: View):
		self.view = view
		self.config = config
		self.view.render_sidebar()
		self.config.page_setup()
		self.config.remove_deploy_btn()
		self.config.session_state()


	def render_similar_images(self):
		if st.session_state['encoded_image'] and st.session_state['similar_image']:
			self.view.render_similar_images(st.session_state['similar_image'], st.session_state['page'], self.config.mount_dir)
		elif not st.session_state['encoded_image']:
			st.info('Please upload an image to find similar images.')
		else:
			st.warning('Similar images not found.')


	def run(self):
		self.render_similar_images()
