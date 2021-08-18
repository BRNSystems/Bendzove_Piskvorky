import aioconsole
import websockets
import asyncio
import json

IP = "localhost:8765"

player_id = 0
ws = websockets.connect("ws://" + IP)
connected = False

got_message = False


async def connect():
    global ws
    global connected
    async with websockets.connect("ws://localhost:8765") as wsx:
        ws = wsx
        connected = True
        while True:
            await asyncio.sleep(10)


async def recieve_data_to_server():
    while not connected:
        await asyncio.sleep(1)
    global ws
    global player_id
    global got_message
    while True:
        async for message in ws:
            try:
                data = json.loads(message)
                if data["action"] == "redraw":
                    print(data["data"])
                    got_message = True
                elif data["action"] == "info":
                    print(data["data"])
                    got_message = True
                elif data["action"] == "id":
                    player_id = data["id"]
                if got_message:
                    print("Enter command:\n")
            except Exception as e:
                print(e)
                print(message)


async def send_data_to_server():
    while not connected:
        await asyncio.sleep(1)
    global ws
    global player_id
    while True:
        cmd = await aioconsole.ainput("Enter command:\n")
        if cmd == "reset":
            await ws.send(json.dumps({"action": "reset"}))
        elif cmd == "redraw":
            await ws.send(json.dumps({"action": "redraw"}))
        elif cmd.startswith("resize"):
            cmd_args = cmd.split(" ")
            if len(cmd_args) >= 3:
                await ws.send(json.dumps({"action": "resize", "width": cmd_args[1], "height": cmd_args[2]}))
            else:
                print("Incorrect argument number.")
        elif cmd.startswith("add"):
            cmd_args = cmd.split(" ")
            if len(cmd_args) >= 2:
                await ws.send(json.dumps({"action": "add", "col": cmd_args[1], "id": player_id}))
        elif cmd == "help":
            await ws.send(json.dumps({"action": "help"}))
        else:
            print("Unknown command. Type 'help' to list all commands.")


loop = asyncio.get_event_loop()


async def run_stuff():
    await asyncio.gather(connect(), recieve_data_to_server(), send_data_to_server())


asyncio.run(run_stuff())
