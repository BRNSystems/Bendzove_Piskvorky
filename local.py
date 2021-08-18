width = 9
height = 6

grid = []

for _ in range(width):
    temp_grid = []
    for _ in range(height):
        temp_grid.append(" ")
    grid.append(temp_grid)

player = 0


def apply_gravity(gridx):
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


def add(gridx, col3):
    try:
        col = int(col3)
    except ValueError:
        return 2
    if -1 < col < width:
        global player
        if gridx[col][0] == " ":
            if player == 1:
                gridx[col][0] = "O"
                player = 0
                return 1
            else:
                gridx[col][0] = "X"
                player = 1
                return 1
        else:
            return 0
    return 2


def draw(gridx):
    tempstorage = ""
    for _ in range((width * 2) + 1):
        tempstorage = tempstorage + "_"
    tempstorage = tempstorage + "\n|"
    for i in range(0, width):
        tempstorage = tempstorage + f"{i}|"
    tempstorage = tempstorage + "\n|"
    for y in range(0, height):
        for x in range(0, width):
            tempstorage = tempstorage + gridx[x][y] + "|"
        tempstorage = tempstorage + "\n|"
    tempstorage = tempstorage[:-1]
    for _ in range((width * 2) + 1):
        tempstorage = tempstorage + "¯"
    print(tempstorage)


while True:
    draw(grid)
    col2 = input(f"It is player{player} 's turn, input column number from 0 to {width - 1}:")
    success = add(grid, col2)
    while success != 1:
        if success == 2:
            col2 = input(f"Oops you have entered '{col2}' which is not a valid input. Please try again player{player}:")
        elif success == 0:
            col2 = input(f"Oops you have entered '{col2}' which is full. Please try again player{player}:")
        success = add(grid, col2)
    apply_gravity(grid)
    draw(grid)
