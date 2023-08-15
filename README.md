# BEAR LABS Wireless Force Myography Band

This repository contains all the CAD files, software, and information for the Wireless FMG band project. 
It's a work-in-progress, and the goal of this repository is to make it easier for people without prior experience on this project to continue working on it.

This README has three sections:

  - [Mechanical and Electrical Details](#mechanical-and-electrical-details)
    - [Parts](#parts)
    - [Housings](#housings)
  - [Software Details](#software-details)
  - [Issues and Future Improvements](#issues-and-future-improvements)

## Mechanical and Electrical Details

### Parts
* [Unexpected Maker TinyS3 ESP32 Microcontroller](https://esp32s3.com/tinys3.html).

It's got support for Bluetooth Low Energy, and 9 analog inputs, which is one more than we need.

* [Force Sening Resistors](https://buyinterlinkelectronics.com/products/fsr-400-short)

8 total, one per housing unit.

* Generic Boa Clip

We've got several in the lab, any one of them is fine.

* [200mAh LiPo Battery](https://a.co/d/5Q56SUB)

Having 3 of these on hand gives us the ability to run the FMG band indefinitely, because batteries can be easily swapped out.

### Housings

All housings are printed from PLA, and have a TPE pad between the PLA and subject's skin. 
Each housing has a rectangular channel, with two circular holes on either side. The rectangular channel is for passing wires through, and the circular holes are for the boa clip wires. This would ideally allow the distance between the housings to change as the band is tightened/loosened.

The TPE pad makes wearing the band more comfortable, and has a 100% infill cylinder to activate the FSR.
There are 8 total housings, and each one has an FSR, but some are larger so that they can carry extra hardware.

#### There are 3 types of housing:

The **main housing** contains the ESP32 Microcontroller, has an FSR cutout on the bottom, and it's super wide so that we can stick the boa lace on the top. There is only one of these housings.

The **battery housing** is also very large, so that we can fit the battery inside. It's also got an FSR cutout on the bottom. Currently, there is only one of these housings, but in the future it would be possible to replace generic housings with these guys to extend battery life.

The **generic housing** is much smaller, and is essentially just a home for a force sensor. At current spec, there are 6 of these, bringing the total number of housings to 8.

All housing CAD models can be found in the cad_files folder.

## Software Details

The software is comparatively much simpler. 

In the ble_server file there is some arduino code that runs on the microcontroller. It creates a Bluetooth Low Energy server which waits for a client connection, and then broadcasts data read from the analog inputs.

Every time a BLE Server sends data, there's a delay, because it has to wait for a confirmation from the client. 
So to minimize this delay, the microcontroller samples 64 times, and then sends that data as an array of length 512. If you want to understand this more thoroughly, [here is an excellent article](https://interrupt.memfault.com/blog/ble-throughput-primer).

The BLE client program creates a connection to the BLE server, and it's responsible for parsing the long array back into the samples from the FSRs. For now, it just records the data into a .csv file. Take a look at `example.csv` to see what that looks like.

## Issues and Future Improvements
As the project stands right now, the band itself is unassembled. The PLA housings have all been finalized and printed, but the TPE pads have yet to be manufactured.

There are several major areas that need to be completed before the band is finished.

* Electrical assembly is not done
* The boa clip has not yet been integrated into the band
* There is a bug in `ble_client` that causes the connection to time out occasionally
* The FSRs need to be embedded into the housings and connected to the microcontroller
* The TPE pads need to be printed and attached to the housings.

If there are any questions, please email me at randallj24@student.jhs.net or text me at 801-347-6334.

---
Written by James Randall, Jesuit High School '24