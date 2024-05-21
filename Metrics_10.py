from typing import List


class Metrics:
    """
    Contains information that we want to collect about an instance of playing the game
    """

    def __init__(self, board, game_time: float, move_times: List[float], max_ram_usage: int) -> None:
        """
        Metrics for a given board:
        - enemy_board (just to store)
        - total_running_time
        - individual_move_times
        - total_moves
        - max_ram_usage
        """
        self.enemy_board = board
        self.total_running_time = game_time
        self.individual_move_times = move_times
        self.total_moves = len(self.individual_move_times)
        self.max_ram_usage = max_ram_usage
