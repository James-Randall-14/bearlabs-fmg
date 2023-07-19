import asyncio
import sys
from bleak import BleakClient, BleakScanner

# Global Variable Definition
CHARACTERISTIC_UUID = "4b974cb0-aa54-48fa-8bcc-e82e030362e2"
mac_addr = "DC:54:75:CA:F1:FD"

async def run_client(queue: asyncio.Queue):

    async def callback_handler(_, data):
        megalist = list(data)
        fsr_list = await split_list(megalist)
        print(fsr_list)

    async def split_list(input): # Split up the mega-list into a 20x8 2D list
        fsr_list = [[0]*8]*20
        for i in range(len(input)):
            fsr_list[int(i / 8)][i % 8] = input[i]
        return fsr_list

    async def spin():
        while True: 
            await asyncio.sleep(1)
            if not client.is_connected:
                print("Lost connection to FMG Band")
                exit()


    print("Searching for FMG Band...")
    device = await BleakScanner.find_device_by_name("FMG_Band", timeout=10)
    if device is None:
        print("Could not find device")
        exit()

    print("Trying to create a client...")
    client = BleakClient(device)
    print("Client Created")
    async with client:
        print("Connected")
            #await client.start_notify(CHARACTERISTIC_UUID, callback_handler)
            #await spin()
    #except TimeoutError:

    #    print("Connection timed out, try running again")
    #    if client is not None:
    #        await client.disconnect()
    #    exit()

async def main():
    queue = asyncio.Queue()
    client_task = run_client(queue)

    await asyncio.gather(client_task)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: 
        print("Operations cancelled by user")
        sys.exit(0)