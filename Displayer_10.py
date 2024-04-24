from colorama import Back, Fore

from Grid_10 import Grid

colorMap = {
    "Aircraft": 107,
    "Battleship": 46,
    "Cruiser": 106,
    "Destroyer": 44,
    "Submarine": 104,
}


class Displayer:
    def __init__(self) -> None:
        pass

    # TODO: Adapt to whichever hit miss values we give it
    def display(self, grid: Grid) -> None:
        print(f"{Back.WHITE}{' ' * 24}{Back.BLACK}")
        for i in range(10):
            print(f"{Back.WHITE}{' ' * 2}{Back.BLACK}", end="")
            for j in range(10):
                value = grid.map[i][j]
                if value == 0:
                    color = Fore.LIGHTBLACK_EX
                elif value == 1:
                    color = Fore.WHITE
                elif value == "X":
                    color = Fore.RED
                else:
                    color = Fore.BLUE
                    value = grid.map[i][j].name

                print(f"{color}{Back.BLACK}{value} ", end="")
            print(f"{Back.WHITE}{' ' * 2}{Back.BLACK}")
        print(f"{Back.WHITE}{' ' * 24}{Back.BLACK}")
        print(f"{Fore.WHITE}")
