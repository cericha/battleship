class Metrics:
    """
    Contains information that we want to collect about an instance of playing the game
    """

    def __init__(self, time: float, moves: int) -> None:
        self.time = time
        self.moves = moves
