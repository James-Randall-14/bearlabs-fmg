"""
Async callbacks with a queue and external consumer
--------------------------------------------------

An example showing how async notification callbacks can be used to
send data received through notifications to some external consumer of
that data.

Created on 2021-02-25 by hbldh <henrik.blidh@nedomkull.com>

"""
import time
import asyncio
import logging

from bleak import BleakClient, BleakScanner

# Global Variable Definition
SERVICE_UUID = "e2653d64-d106-4a30-bca9-938b405b9735"
CHARACTERISTIC_UUID = "4b974cb0-aa54-48fa-8bcc-e82e030362e2"

logger = logging.getLogger(__name__)


class DeviceNotFoundError(Exception):
    pass


async def run_ble_client(queue: asyncio.Queue):
    logger.info("starting scan...")

    device = await BleakScanner.find_device_by_address(SERVICE_UUID)
    if device is None:
        logger.error("could not find device with address '%s'", SERVICE_UUID)
        raise DeviceNotFoundError

    logger.info("connecting to device...")

    async def callback_handler(_, data):
        await queue.put((time.time(), data))

    async with BleakClient(device) as client:
        logger.info("connected")
        await client.start_notify(CHARACTERISTIC_UUID, callback_handler)
        await asyncio.sleep(10.0)
        await client.stop_notify(CHARACTERISTIC_UUID)
        # Send an "exit command to the consumer"
        await queue.put((time.time(), None))

    logger.info("disconnected")


async def run_queue_consumer(queue: asyncio.Queue):
    logger.info("Starting queue consumer")

    while True:
        # Use await asyncio.wait_for(queue.get(), timeout=1.0) if you want a timeout for getting data.
        epoch, data = await queue.get()
        if data is None:
            logger.info(
                "Got message from client about disconnection. Exiting consumer loop..."
            )
            break
        else:
            logger.info("Received callback data via async queue at %s: %r", epoch, data)


async def main():
    queue = asyncio.Queue()
    client_task = run_ble_client(queue)
    consumer_task = run_queue_consumer(queue)

    try:
        await asyncio.gather(client_task, consumer_task)
    except DeviceNotFoundError:
        pass

    logger.info("Main method done.")


if __name__ == "__main__":

    log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main())