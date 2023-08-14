import asyncio
import bleak
import aiofiles
from aiocsv import AsyncWriter
from datetime import datetime, date


# Global Variable Definition
CHARACTERISTIC_UUID = "4b974cb0-aa54-48fa-8bcc-e82e030362e2"
mac_addr = "DC:54:75:CA:F1:FD"

async def run_client():

    async def callback_handler(_, data):
        megalist = list(data)
        #print(megalist)
        fsr_list = await split_list(megalist)
        print(fsr_list)
        async with aiofiles.open(csvname, 'a', newline='\n') as csvfile:
            writer = AsyncWriter(csvfile, delimiter=',')
            await writer.writerows(fsr_list)

    async def split_list(input): # Split up the mega-list into a 2D list
        fsr_list = [[0] * 8 for i in range(int(len(input) / 8))]
        for i in range(len(input)):
            fsr_list[int(i / 8)][i % 8] = input[i]
        return fsr_list

    async def spin():
        while True: 
            if not client.is_connected:
                print("Lost connection to FMG Band")
                await client.stop_notify(CHARACTERISTIC_UUID)
                exit()
            try: await asyncio.sleep(1)
            except asyncio.exceptions.CancelledError:
                    try: await client.stop_notify(CHARACTERISTIC_UUID)
                    except bleak.exc.BleakError:
                        pass
                    await asyncio.sleep(0.25) # Wait for the last notifications to be sent
                    print("Operations cancelled by user")
                    exit()

    print("Searching for FMG Band...")
    try: device = await bleak.BleakScanner.find_device_by_name("FMG_Band", timeout=10)
    except asyncio.exceptions.CancelledError:
        print("Operations cancelled by user")
        exit()
    if device is None:
        print("Could not find device")
        exit()

    # Create CSV file for logging data
    now = datetime.now()
    current_date = date.today()
    current_time = now.strftime("%H-%M-%S")
    csvname = "{}_{}.csv".format(current_date, current_time)

    print("Trying to create a client...")
    async with bleak.BleakClient(device) as client:
        print("Connected")
        await client.start_notify(CHARACTERISTIC_UUID, callback_handler)
        await spin()


async def main():
    client_task = run_client()

    await asyncio.gather(client_task)

if __name__ == "__main__":
    asyncio.run(main())