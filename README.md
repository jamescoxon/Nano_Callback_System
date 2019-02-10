# Nano_Callback_System
## Introduction
This is a simple system for detecting new blocks being sent to a Nano address, this is achieved by a server script which listens for new blocks via the Nano node callback and then can be setup to forward the block details over a websocket connection to listening clients. By using the node callback you can trigger an event as soon as a block is seen (and voted on) on devices and systems that don't have the capacity or the need to run a full node for example embedded systems.
The system works in this order:
* The 'client' system connects to the 'server' via a websockets connection and sends a json containing a Nano address to track.
* The server adds this Nano address to an internal dictionary
* The server monitors the callback and if it sees a transaction being sent to any of the addresses in its internal dictionary it then forwards this block to the client over the websockets connection.

Currently a test server is running: `ws://yapraiwallet.space/call` (currently does not require an API key, just use "0")

## Why and Why Nano?
You don't need to hold a wallet (either full or light) on a device that just needs to initiate an action based on a Nano transaction, just need to detect the incoming block and trigger the action.
Nano is ideal for this as its feeless and fast enough to do this all in real time, the user will get a very quick response back from the device/system. In theory you could do the same with any crypto however you won't get the same advantages.

## Use Cases
### Embedded Hardware
An internet connected embedded hardware device can connect via websockets to the callback server and monitor for activity of a particular address, this allows a low powered device not to need a full node to function. 

Example 1 - a Nano controlled parking meter:
* The local council could create a Nano address assigned to a particular device on their Nano node (they hold the private key securely)
* A internet connected parking meter could connect to the callback server and monitor for send transactions to this address
* A user would scan a QR code on the parking meter and send a fixed amount to the parking meters address
* The callback server would detect the incoming send block and push this block to the parking meter
* The parking meter checks the block and amount and if correct will trigger the parking meter to turn on
* The council's Nano node processes the pending blocks in their own time.

Example 2 - USB charger in an airport paid for with Nano
* Prototype is based on ESP32 Heltec WiFi board with SSD1306 OLED screen
* User connects a device to the USB port
* User sends a set amount of Nano to the displayed address (scan the QR code)
* The callback server detects the incoming send block and pushes the data over the websockets connection to the ESP32
* The device checks the block and turns on the USB port (time depends on amount of Nano sent)
* This has been implemented, see [arduino_esp32](https://github.com/jamescoxon/Nano_Callback_System/tree/master/arduino_esp32) for more infomation.

![usbcharger1](https://github.com/jamescoxon/Nano_Callback_System/blob/master/doc/usbchargerscreen1.png)

* [Youtube - Simple example of triggering with a send block](https://youtu.be/LOb4rLssOxY)
* [Youtube - Example of Hardware](https://www.youtube.com/watch?v=FJB87_jbJ6k&feature=youtu.be) (please note this is an old implementation of the concept.)

### Desktop Notifications
Requirements - python3.7

#### OS X

`pip3 install pync asyncio websockets json decimal`

`python3 osx_client.py ws://yapraiwallet.space/call 0 xrb_1w4h9mk7nyzjdy8bt3o5u46uwrpdt6e4xaosja7yduz55jfiecmirdxhnz9z`

This will run a python script that connects to the callback server and waits for a transaction to the address you've inputed.

![osx_screenshot](https://github.com/jamescoxon/Nano_Callback_System/blob/master/doc/osx_screenshot.png)


#### Windows
On Windows if you install `win10toast` you can have pop up notifications of transactions. Installation depends on how you have installed python on your windows system (may need to execute the script using powershell).

`python3 nano_iot_client.py ws://yapraiwallet.space/call 0 xrb_1w4h9mk7nyzjdy8bt3o5u46uwrpdt6e4xaosja7yduz55jfiecmirdxhnz9z`

#### Linux
The linux python client will only show blocks in the terminal.
`python3 nano_iot_client.py ws://yapraiwallet.space/call 0 xrb_1w4h9mk7nyzjdy8bt3o5u46uwrpdt6e4xaosja7yduz55jfiecmirdxhnz9z`

## Status
Currently the system lacks any true authentication or security however this is something that will be implemented, it will be up to the service provider to decided how much they want to implement (it may be acceptable to have less security if your transactions are very small). Authentication will likely include the use of an api key but also will add the ability to actually track the account and check the hash/state blocks themselves.
