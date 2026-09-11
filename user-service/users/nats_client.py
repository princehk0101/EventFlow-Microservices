import asyncio
import json
import threading

import nats
from decouple import config


class NATSClient:

    def __init__(self):
        self.nc = None
        self.js = None
        self.loop = None
        self.thread = None
        self.ready = threading.Event()

    def start(self):
        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self.thread.start()

        if not self.ready.wait(timeout=10):
            raise RuntimeError("NATS connection timeout")

    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.run_until_complete(self._connect())
        self.loop.run_forever()

    async def _connect(self):

        self.nc = await nats.connect(
            config("NATS_URL")
        )

        self.js = self.nc.jetstream()

        self.ready.set()

        print("NATS connected successfully")

    def publish_user_created(self, user):

        message = {
            "event": "user.created",
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
        }

        future = asyncio.run_coroutine_threadsafe(
            self.js.publish(
                "user.created",
                json.dumps(message).encode()
            ),
            self.loop
        )

        future.result(timeout=5)

        print("User created event published")


nats_client = NATSClient()