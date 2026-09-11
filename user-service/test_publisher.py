import asyncio
import json
import nats


async def main():
    nc = await nats.connect("nats://localhost:4222")

    message = {
        "event": "user.created",
        "user_id": 1,
        "name": "Prince",
        "email": "prince@example.com"
    }

    await nc.publish(
        "user.created",
        json.dumps(message).encode()
    )

    await nc.flush()
    await nc.close()

    print("Message published successfully")


asyncio.run(main())