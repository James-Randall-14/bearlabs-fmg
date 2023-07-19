/*
    Video: https://www.youtube.com/watch?v=oCMOYS71NIU
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleNotify.cpp
    Ported to Arduino ESP32 by Evandro Copercini
    updated by chegewara

   Create a BLE server that, once we receive a connection, will send periodic notifications.
   The service advertises itself as: 4fafc201-1fb5-459e-8fcc-c5c9c331914b
   And has a characteristic of: beb5483e-36e1-4688-b7f5-ea07361b26a8

   The design of creating the BLE server is:
   1. Create a BLE Server
   2. Create a BLE Service
   3. Create a BLE Characteristic on the Service
   4. Create a BLE Descriptor on the characteristic
   5. Start the service.
   6. Start advertising.

   A connect hander associated with the server starts a background task that performs notification
   every couple of seconds.
*/
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLE2902.h>
#include <iostream>

BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;
int x; // index variable. Not called index for redefinition reasons
uint16_t fsr_vals[20][8] = {0};


// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID        "e2653d64-d106-4a30-bca9-938b405b9735"
#define CHARACTERISTIC_UUID "4b974cb0-aa54-48fa-8bcc-e82e030362e2"

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
      BLEDevice::startAdvertising();
    };

    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
    }
};

void measure_fsrs(int outer_index) {
  if (outer_index >= sizeof(fsr_vals)/sizeof(fsr_vals[0])) {
    throw std::invalid_argument("Tried to write to an FSR index that was out of bounds");
  }
  for(int i = 0; i < sizeof(fsr_vals[0])/sizeof(fsr_vals[0][0]); i++) {
    uint16_t val = analogRead(i + 1); // Analog input pins are pins 1-8
    fsr_vals[outer_index][i] = val;
  }
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // Tinys3 has a ADC resolution of 12 bits

  // Set pins into input mode
  for (int i = 0; i <= 8; i++) {
    pinMode(i, INPUT);
  }

  // Create the BLE Device
  BLEDevice::init("FMG_Band");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ   |
                      BLECharacteristic::PROPERTY_WRITE  |
                      BLECharacteristic::PROPERTY_NOTIFY |
                      BLECharacteristic::PROPERTY_INDICATE
                    );

  // https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml
  // Create a BLE Descriptor
  pCharacteristic->addDescriptor(new BLE2902());

  // Start the service
  pService->start();

  // Start advertising
  Serial.println("Waiting on a client...");
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);  // set value to 0x00 to not advertise this parameter
  BLEDevice::startAdvertising();
}

void loop() {
    // notify changed value
    if (deviceConnected) {

        measure_fsrs(x);

        pCharacteristic->setValue((uint8_t*)&fsr_vals, 160);
        pCharacteristic->notify();

        x += 1;

        // Reset index so we don't overflow
        if (x >= 20) {
          Serial.println("Reached end of array");
          x = 0;
        }

        //delay(3); // If msgs are sent too quickly, BLE can get congested.
    }

    // disconnecting
    if (!deviceConnected && oldDeviceConnected) {
        Serial.println("Disconnected");
        delay(500); // give the bluetooth stack the chance to get things ready
        pServer->startAdvertising(); // restart advertising
        Serial.println("Restarting advertising");
        oldDeviceConnected = deviceConnected;
    }

    // connecting
    if (deviceConnected && !oldDeviceConnected) {
        Serial.println("Connecting to a new device");
        // do stuff here on connecting
        oldDeviceConnected = deviceConnected;
    }
}
