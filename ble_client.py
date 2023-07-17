import asyncio
import time
from bleak import BleakClient, BleakScanner

# Global Variable Definition
CHARACTERISTIC_UUID = "4b974cb0-aa54-48fa-8bcc-e82e030362e2"

async def run_ble_client(queue: asyncio.Queue):

    print("Searching for FMG Band...")
    device = await BleakScanner.find_device_by_name("FMG_Band")
    if device is None:
        print("Could not find device")
        exit()

    async def callback_handler(_, data):
        print(data)

    async def spin():
        while True:
            await asyncio.sleep(1)

    async with BleakClient(device) as client:
        print("Connected")
        await client.start_notify(CHARACTERISTIC_UUID, callback_handler)
        await spin()
        await client.stop_notify(CHARACTERISTIC_UUID)
        # Send an "exit command to the consumer"
        await queue.put((time.time(), None))

    print("Disconnected")

async def main():
    queue = asyncio.Queue()
    client_task = run_ble_client(queue)

    await asyncio.gather(client_task)

    print("Main Method Completed")


if __name__ == "__main__":
    asyncio.run(main())