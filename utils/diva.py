import httpx
from utils.logger import logging
from src.secret import QUERY_API
from src.schema import ImageQuery


async def fetch(encoded_image: str, threshold: float, page: int):
	payload = ImageQuery()
	payload.encoded_image = encoded_image
	payload.threshold = threshold
	payload.page = page

	print(payload.model_dump())
	try:
		async with httpx.AsyncClient() as client:
			logging.info('Proceeding request for image query.')

			response = await client.post(
				url=QUERY_API,
				json=payload.model_dump(),
				timeout=180,
			)

			data = response.json()

			return data, response.status_code
	except httpx.ConnectError:
		pass
		# raise Exception(
		#     "Unable to connect backend service. Please ensure backend server is ready."
		# )
