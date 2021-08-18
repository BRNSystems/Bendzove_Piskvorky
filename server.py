import asyncio
import json
import random
import websockets
import threading

width = 9
height = 6
player_on_turn = 0

grid = []

connected = set()
cache = [{"player": 0, "col": -1}]


async def socket_broadcast(data):
    for client in connected:
        await client.send(str(data))


players = []


async def hello(ws, _):
    global cache
    global width
    global height
    global player_on_turn
    i = 0
    connected.add(ws)
    this_id = random.randint(0, 100000)
    players.append({"ws": ws, "id": this_id})
    if len(players) >= 3:
        await socket_broadcast(json.dumps({"action": "info", "data": f"Warning {len(players)} players are connected"}))
    await ws.send(json.dumps({"action": "id", "id": this_id}))
    try:
        while i == 0:
            try:
                x = await ws.recv()
                try:
                    temp = json.loads(x)
                    print(str(temp) + " data")
                    if temp["action"] == "reset":
                        await reset()
                        await draw(grid)
                        await socket_broadcast(
                            json.dumps({"action": "info", "data": f"It is player{player_on_turn} 's turn."}))
                        await players[player_on_turn]['ws'].send(json.dumps(
                            {"action": "info", "data": f"It is your turn, input column number from 0 to {width - 1}:"}))
                    elif temp["action"] == "redraw":
                        await ws.send(await draw(grid, True))
                    elif temp["action"] == "resize":
                        try:
                            width = int(temp["width"])
                            height = int(temp["height"])
                            await reset()
                            await ws.send(await draw(grid, True))
                            await socket_broadcast(
                                json.dumps({"action": "info", "data": f"It is player{player_on_turn} 's turn."}))
                            await players[player_on_turn]['ws'].send(json.dumps({"action": "info",
                                                                                 "data": f"It is your turn, type 'add (number of column from 0 to {width - 1}' :"}))
                        except ValueError:
                            await ws.send(json.dumps({"action": "info", "data": "Invalid arguments to resize."}))
                    elif temp["action"] == "add":
                        plx = 0
                        for player in players:
                            if temp["id"] == player["id"]:
                                if plx == player_on_turn:
                                    res = await add(grid, temp["col"])
                                    if res == 1:
                                        await apply_gravity(grid)
                                        await socket_broadcast(await draw(grid, True))
                                        await socket_broadcast(json.dumps(
                                            {"action": "info", "data": f"It is player{player_on_turn} 's turn."}))
                                        await players[player_on_turn]['ws'].send(json.dumps({"action": "info",
                                                                                             "data": f"It is your turn, input column number from 0 to {width - 1}:"}))
                                    elif res == 2:
                                        await players[player_on_turn]['ws'].send(json.dumps({"action": "info",
                                                                                             "data": f"Oops you have entered '{temp['col']}' which is not a valid input. Please try again player{player_on_turn}:"}))
                                    elif res == 0:
                                        await players[player_on_turn]['ws'].send(json.dumps({"action": "info",
                                                                                             "data": f"Oops you have entered '{temp['col']}' which is full. Please try again player{player_on_turn}:"}))
                            plx = plx + 1
                    elif temp["action"] == "help":
                        await ws.send(json.dumps({"action": "info",
                                                  "data": f"\n'reset' - Resets the game, also you must start the game with this\n'redraw' - Sends you the current state of th board\n'resize' - Resizes the playing board and resets it usage: 'resize (width) (height)'\n'add' - Adds your character to a column, usage: 'add (column number from 0 to {width - 1})\n'help' - Prints this help message"}))

                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
                connected.remove(ws)
                i = 1
    finally:
        # Unregister.
        try:
            connected.remove(ws)
            i = 0
            for x in players:
                if x[ws] == ws:
                    players.pop(i)
                i = i + 1
        except Exception as e:
            print(e)


async def reset():
    global grid
    grid = []
    for _ in range(width):
        temp_grid = []
        for _ in range(height):
            temp_grid.append(" ")
        grid.append(temp_grid)


async def apply_gravity(gridx):
    for gr in gridx:
        for _ in range(height):
            for i in range(height - 2, -1, -1):
                if gr[i] == "X" and gr[i + 1] == " ":
                    gr[i + 1] = "X"
                    gr[i] = " "
                if gr[i] == "O" and gr[i + 1] == " ":
                    gr[i + 1] = "O"
                    gr[i] = " "
                if gr[i] == "X" and gr[i + 1] == " ":
                    gr[i + 1] = "X"
                    gr[i] = " "
                if gr[i] == "O" and gr[i + 1] == " ":
                    gr[i + 1] = "O"
                    gr[i] = " "


async def add(gridx, col3):
    try:
        col = int(col3)
    except ValueError:
        return 2
    if -1 < col < width:
        global player_on_turn
        if gridx[col][0] == " ":
            if player_on_turn == 1:
                gridx[col][0] = "O"
                player_on_turn = 0
                return 1
            else:
                gridx[col][0] = "X"
                player_on_turn = 1
                return 1
        else:
            return 0
    return 2


async def draw(gridx, return_data=False):
    temporary_storage = ""
    for _ in range((width * 2) + 1):
        temporary_storage = temporary_storage + "_"
    temporary_storage = temporary_storage + "\n|"
    for i in range(0, width):
        temporary_storage = temporary_storage + f"{i}|"
    temporary_storage = temporary_storage + "\n|"
    for y in range(0, height):
        for x in range(0, width):
            temporary_storage = temporary_storage + gridx[x][y] + "|"
        temporary_storage = temporary_storage + "\n|"
    temporary_storage = temporary_storage[:-1]
    for _ in range((width * 2) + 1):
        temporary_storage = temporary_storage + "¯"
    print(temporary_storage)
    if return_data:
        return json.dumps({"action": "redraw", "data": temporary_storage})
    else:
        await socket_broadcast(json.dumps({"action": "redraw", "data": temporary_storage}))


start_server = websockets.serve(hello, "localhost", 8765)

loop = asyncio.get_event_loop()


def loop_in_thread():
    loop.run_until_complete(start_server)
    loop.run_forever()


thread = threading.Thread(loop_in_thread())
thread.start()
