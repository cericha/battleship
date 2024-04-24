from time import perf_counter


class TimerError(Exception):
    def __init__(self, message="Timer has not been started."):
        super().__init__(message)


class Timer:
    def __init__(
        self, time_limit: float = float("inf"), allowance: float = 0.0
    ) -> None:
        """Timer class allowing to set a timer and check if time is up.

        Defaults values for time_limit allow for infinite time.

        Args:
            time_limit (float, optional): Defaults to float("inf").
            allowance (float, optional): Defaults to 0.0.
        """
        self.time_limit = time_limit
        self.allowance = allowance
        self.max_time = self.time_limit + self.allowance
        self.start_time = None

    def start_timer(self) -> None:
        """Allows for starting and restarting timer"""
        self.start_time = perf_counter()

    def elapsed_time(self) -> float:
        if self.start_time is None:
            raise TimerError("Timer has not been started.")
        return perf_counter() - self.start_time

    def time_left(self) -> float:
        if self.start_time is None:
            raise TimerError("Timer has not been started.")
        return max(0.0, self.max_time - (perf_counter() - self.start_time))

    def is_time_up(self) -> bool:
        if self.start_time is None:
            raise TimerError("Timer has not been started.")
        return (perf_counter() - self.start_time) > self.max_time
