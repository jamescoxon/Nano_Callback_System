import asyncio
import websockets
from sys import argv, exit
import json, pync, time
from decimal import Decimal

def get_details(block):
    try:
        amount_raw = block["amount"]
        # block contents need another json format
        contents = json.loads(block["block"])
        destination = contents["link_as_account"]
        return amount_raw, destination
    except Exception as e:
        print(f"Failed to get block info: {e}")
        return None, None

def convert_amount(raw):
    return str(float(raw)/1e30)

async def test(server, api_key, account):

    async with websockets.connect(server) as websocket:

        await websocket.send(json.dumps({"address": account, "api_key": api_key}))

        while True:
            response = await websocket.recv()
            block = json.loads(response)
            print("Block received! Printing contents after JSON format...\n\n{}\n\n".format(block))

            amount_raw, destination = get_details(block)
            if amount_raw is None or destination is None:
                continue
            
            amount_NANO = convert_amount(amount_raw)
            print("{}: {:.3} NANO received on {}".format(time.strftime("%d/%m/%Y %H:%M:%S"), Decimal(amount_NANO), destination))
            pync.notify("{:.3} NANO received on {}".format(Decimal(amount_NANO), destination), title='Nano Notifier')

def main():
    
    argc = len(argv)
    if argc < 4:
        print("Usage: {} SERVER API_KEY ACCOUNT".format(argv[0]))
        exit(0)
    
    server = argv[1]
    key = argv[2]
    account = argv[3]

    asyncio.get_event_loop().run_until_complete(test(server, key, account))

if __name__ == "__main__":
    main()
