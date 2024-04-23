from colorama import init, Fore, Back

colorMap = {
    "Aircraft"      : 107,
    "Battleship"    : 46,
    "Cruiser"       : 106,
    "Destroyer"     : 44,
    "Submarine"     : 104,
}


class Displayer():
    def __init__(self):
        pass

    # TODO: Adapt to whichever hit miss values we give it
    def display(self, grid):
        for i in range(3 * 10):
            for j in range(10):
                v = i // 3

                if grid[v][j] == "-":
                    color = Fore.LIGHTBLACK_EX
                elif grid[v][j] == "O":
                    color = Fore.WHITE
                elif grid[v][j] == "X":
                    color = Fore.RED
                else:
                    color = Fore.WHITE

                if i % 3 == 1:
                    string = str(grid[v][j]).center(7, " ")
                else:
                    string = " "

                print(f"{color}{Back.BLACK}{string} ", end="")
            print()

            if i % 3 == 2:
                print()