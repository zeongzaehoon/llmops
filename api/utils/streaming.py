import asyncio
import uuid


class ResponseQueue:
	def __init__(self, request_id: str):
		self.event = asyncio.Event()
		self.queue = asyncio.Queue()
		self.request_id = request_id or uuid.uuid4()


def get_response_queue():
	return ResponseQueue(request_id=str(uuid.uuid4()))