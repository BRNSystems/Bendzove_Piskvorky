import aioconsole
import websockets
import asyncio
import json

IP = "localhost:8765"

player_id = 0
ws = websockets.connect("ws://" + IP)
connected = False


async def connect():
    global ws
    global connected
    async with websockets.connect("ws://localhost:8765") as wsx:
        ws = wsx
        connected = True
        while True:
            await asyncio.sleep(10)


async def recieve_data_from_server():
    while not connected:
        await asyncio.sleep(1)
    global ws
    global player_id
    while True:
        async for message in ws:
            try:
                data = json.loads(message)
                if data["action"] == "print":
                    print(data["data"])
                elif data["action"] == "id":
                    player_id = data["id"]
            except Exception as e:
                print(e)
                print(message)


async def send_data_to_server():
    while not connected:
        await asyncio.sleep(1)
    global ws
    global player_id
    while True:
        cmd = await aioconsole.ainput()
        data = {"action": cmd, "id": player_id}
        print(data)
        await ws.send(json.dumps(data))


loop = asyncio.get_event_loop()


async def run_stuff():
    await asyncio.gather(connect(), recieve_data_from_server(), send_data_to_server())


asyncio.run(run_stuff())
