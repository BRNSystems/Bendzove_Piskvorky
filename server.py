import asyncio
import json
import random
import websockets
import threading

width = 10
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
    exitit = 0
    connected.add(ws)
    this_id = random.randint(0, 100000)
    i = 0
    players.append({"ws": ws, "id": this_id})
    if len(players) >= 3:
        await socket_broadcast(json.dumps({"action": "print", "data": f"Warning {len(players)} players are connected"}))
    await ws.send(json.dumps({"action": "id", "id": this_id}))
    try:
        await ws.send(await draw(grid, True))
        for player in players:
            if player["ws"] == ws:
                await ws.send(json.dumps({"action": "print", "data": f"It is your turn, type 'add (number of column from 0 to {width - 1})' :"}))
            else:
                ws.send(json.dumps({"action": "print", "data": f"It is player{player_on_turn} 's turn."}))

        await ws.send(json.dumps({"action": "print", "data": "Enter command:"}))
        while exitit == 0:
            try:
                x = await ws.recv()
                try:
                    temp2 = json.loads(x)
                    print(str(temp2))
                    cmd_args = str(temp2["action"]).split(" ")
                    temp = {"action": cmd_args[0], "args": [], "id": temp2["id"]}
                    i = 0
                    for cmd_arg in cmd_args:
                        if i != 0:
                            temp["args"].append(cmd_arg)
                        i = i + 1
                    print(str(temp))

                    if str(temp["action"]) == "reset":
                        await reset()
                        await draw(grid)
                        await socket_broadcast(
                            json.dumps({"action": "print", "data": f"It is player{player_on_turn} 's turn."}))
                        await players[player_on_turn]['ws'].send(json.dumps(
                            {"action": "print",
                             "data": f"It is your turn, input column number from 0 to {width - 1}:"}))

                    elif str(temp["action"]) == "redraw":
                        await ws.send(await draw(grid, True))

                    elif str(temp["action"]) == "resize":
                        try:
                            if len(temp["args"]) >= 2:
                                width = int(temp["args"][0])
                                height = int(temp["args"][1])
                                await reset()
                                await ws.send(await draw(grid, True))
                                await socket_broadcast(
                                    json.dumps({"action": "print", "data": f"It is player{player_on_turn} 's turn."}))
                                await players[player_on_turn]['ws'].send(json.dumps({"action": "print",
                                                                                     "data": f"It is your turn, type 'add (number of column from 0 to {width - 1})' :"}))
                        except ValueError:
                            await ws.send(json.dumps({"action": "print", "data": "Invalid arguments to resize."}))

                    elif str(temp["action"]) == "add":
                        if len(temp["args"]) >= 1:
                            plx = 0
                            for player in players:
                                if int(temp["id"]) == int(player["id"]):
                                    if plx == player_on_turn:
                                        res = await add(grid, temp["args"][0])
                                        if res == 1:
                                            await apply_gravity(grid)
                                            await socket_broadcast(await draw(grid, True))
                                            await socket_broadcast(json.dumps(
                                                {"action": "print", "data": f"It is player{player_on_turn} 's turn."}))
                                            await players[player_on_turn]['ws'].send(json.dumps({"action": "print",
                                                                                                 "data": f"It is your turn, input 'add (0 to {width - 1})':"}))
                                        elif res == 2:
                                            await players[player_on_turn]['ws'].send(json.dumps({"action": "print",
                                                                                                 "data": f"Oops you have entered '{temp['col']}' which is not a valid input. Please try again player{player_on_turn}:"}))
                                        elif res == 0:
                                            await players[player_on_turn]['ws'].send(json.dumps({"action": "print",
                                                                                                 "data": f"Oops you have entered '{temp['col']}' which is full. Please try again player{player_on_turn}:"}))
                                plx = plx + 1

                    elif str(temp["action"]) == "version":
                        await ws.send(json.dumps(
                            {"action": "print",
                             "data": "Bendžove Piškvorky\n'Jeminé, Bruno nemáš tam algorytmus' edition"}))

                    elif str(temp["action"]) == "help":
                        await ws.send(json.dumps({"action": "print",
                                                  "data": f"\n'reset' - Resets the game\n'redraw' - Sends you the current state of the board\n'resize' - Resizes the playing board and resets it usage: 'resize (width) (height)'\n'add' - Adds your character to a column, usage: 'add (column number from 0 to {width - 1})\n'version' - Prints version of the server\n'help' - Prints this help message"}))

                    else:
                        await ws.send(json.dumps(
                            {"action": "print", "data": "Unknown command. Type 'help' to list all commands."}))
                    await ws.send(json.dumps({"action": "print", "data": "Enter command:"}))
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
                connected.remove(ws)
                exitit = 1
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
    tmp = ""
    for i in range((width * 4) - 7):
        tmp = tmp + "‗"
    tmp = tmp + "\n/"
    for i in range((width * 2) - 1):
        tmp = tmp + " "
    tmp = tmp + "\\"
    tmp = tmp + "\n│"
    for i in range(0, width):
        tmp = tmp + f"{i}│"
    tmp = tmp + "\n│"
    for y in range(0, height):
        for x in range(0, width):
            tmp = tmp + gridx[x][y] + "│"
        tmp = tmp + "\n│"
    tmp = tmp[:-1]
    tmp = tmp + "\\"
    for i in range((width * 2) - 1):
        tmp = tmp + " "
    tmp = tmp + "/\n"
    for i in range((width * 2) + 1):
        tmp = tmp + "‾"
    print(tmp)
    if return_data:
        return json.dumps({"action": "print", "data": tmp})
    else:
        await socket_broadcast(json.dumps({"action": "print", "data": tmp}))


start_server = websockets.serve(hello, "localhost", 8765)

loop = asyncio.get_event_loop()
loop.run_until_complete(reset())


def loop_in_thread():
    loop.run_until_complete(start_server)
    loop.run_forever()


thread = threading.Thread(loop_in_thread())
thread.start()
