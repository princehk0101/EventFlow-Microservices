import asyncio
import json
import os
import threading

import nats


class NATSConsumer:

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

        nats_url = os.getenv(
            "NATS_URL",
            "nats://localhost:4222"
        )

        self.nc = await nats.connect(nats_url)

        self.js = self.nc.jetstream()

        # Create stream if it does not exist
        try:
            await self.js.add_stream(
                name="USER_EVENTS",
                subjects=["user.created"]
            )
            print("USER_EVENTS stream created")

        except Exception:
            print("USER_EVENTS stream already exists")

        async def message_handler(msg):

            try:
                data = json.loads(msg.data.decode())

                print("Received event:")
                print(data)

                # Acknowledge message
                await msg.ack()

                print("Message acknowledged")

            except Exception as error:
                print("Error processing message:", error)

        await self.js.subscribe(
            "user.created",
            durable="notification-service",
            stream="USER_EVENTS",
            cb=message_handler,
        )

        self.ready.set()

        print("NATS connected successfully")
        print("Notification Service is listening...")


nats_consumer = NATSConsumer()


if __name__ == "__main__":
    nats_consumer.start()

    while True:
        pass