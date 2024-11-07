import asyncio
from queue import Queue
from typing import Dict

message_queue = Queue()
responses = {}  # Store responses by message ID
response_ready = asyncio.Event()  # Event to signal when response is ready
