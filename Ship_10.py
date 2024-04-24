from enum import Enum


class Direction(Enum):
    VERTICAL = 1
    HORIZONTAL = 2


class Ship:
    def __init__(self, size: int, name: str) -> None:
        self.name = name
        self.size = size
        self.life = size

    def hit(self) -> str:
        self.life -= 1
        if self.life == 0:
            return "sunk"
        else:
            return "hit"

    def __hash__(self) -> int:
        return hash(self.name)
