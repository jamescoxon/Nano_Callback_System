# python 3.6, windows 10 for toast notification

from sys import argv, exit
import json
import websocket
import time
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except ImportError:
    print("If on Windows 10, pip install win10toast for toast notifications")
    toaster = None

# examples for arguments:
# SERVER = 'ws://yapraiwallet.space/callsocket/'
# API_KEY = '123456'
# ACCOUNT = 'xrb_1dgt79j1bwjbhf9raywnwq51nut988c99dj7suf56yfpgxayaj9efw1hjdkb'

def get_socket(server):
    try:
        ws = websocket.create_connection(server)
        ws.settimeout(2.0)
        print(f"Connected to {server}")
        return ws
    except Exception as e:
        print(f"Unable to connect to {server}: {e}")
        return None


def setup(ws, account, api_key):
    try:
        ws.send(json.dumps({"address": account, "api_key": api_key}))
        return True
    except Exception as e:
        print("Unable to send account")
        return False


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


def main():

    argc = len(argv)
    if argc < 4:
        print(f"Usage: {argv[0]} SERVER API_KEY ACCOUNT")
        exit(0)

    server = argv[1]
    key = argv[2]
    account = argv[3]

    ws = get_socket(server)
    if not ws: exit(1)
    if not setup(ws, account, key): exit(1)
    time_last_msg = time.time()

    while 1:
        try:
            rec = ws.recv()
            time_last_msg = time.time()
            block = json.loads(rec)
            print(f"Block received! Printing contents after JSON format...\n\n{block}\n\n")

            amount_raw, destination = get_details(block)
            if amount_raw is None or destination is None:
                continue

            amount_NANO = convert_amount(amount_raw)

            if toaster:
                toaster.show_toast(
                    "Received some Nano!", f"{amount_NANO} NANO received on {destination}",
                    icon_path="nano.ico",
                    duration=5
                )
            else:
            	print(f"{amount_NANO} NANO received on {destination}")
            continue

        except websocket.WebSocketTimeoutException as e:
            # timeout
            # prevent shadow disconnects by reconnecting every now and then
            if time.time() - time_last_msg > 300:
                ws.close()
                ws = None
                try:
                    while ws is None:
                        ws = get_socket(server)
                        if not ws:
                            time.sleep(2)
                            print("Reconnecting...")
                        if not setup(ws, account, key): exit(1)
                except KeyboardInterrupt:
                    print("\nCtrl-C detected, closing\n")
                    break
            continue
        except KeyboardInterrupt:
            print("\nCtrl-C detected, closing\n")
            break
        except Exception as e:
            print(f"Unexpected error, reconnecting...: {e}")
            raise
            ws.close()
            ws = None
            try:
                while ws is None:
                    ws = get_socket(server)
                    if not ws:
                        time.sleep(2)
                        print("Reconnecting...")
                    if not setup(ws, account, key): exit(1)
            except KeyboardInterrupt:
                print("\nCtrl-C detected, closing\n")
                break
            continue


if __name__ == "__main__":
    main()