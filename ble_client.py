import asyncio
import sys
from bleak import BleakClient, BleakScanner

# Global Variable Definition
CHARACTERISTIC_UUID = "4b974cb0-aa54-48fa-8bcc-e82e030362e2"

async def run_client(queue: asyncio.Queue):

    print("Searching for FMG Band...")
    device = await BleakScanner.find_device_by_name("FMG_Band", timeout=10)
    if device is None:
        print("Could not find device")
        exit()

    async def callback_handler(_, data):
        decoded_data = int.from_bytes(data, "big")
        print(decoded_data)

    async def spin():
        while True: 
            await asyncio.sleep(1)
            if not client.is_connected:
                print("Lost connection to FMG Band")
                exit()

    try: 
        async with BleakClient(device) as client:
            print("Connected")
            await client.start_notify(CHARACTERISTIC_UUID, callback_handler)
            await spin()
    except TimeoutError: 
        print("Connection timed out, try running again")
        exit()

async def main():
    queue = asyncio.Queue()
    client_task = run_client(queue)

    await asyncio.gather(client_task)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: 
        print("Operations cancelled by user")
        sys.exit(0)