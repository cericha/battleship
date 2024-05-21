from typing import List
import matplotlib.pyplot as plt
import numpy as np

from Metrics_10 import Metrics

def make_statistics_graphs(all_game_metrics: List[Metrics]):

    # 1. Histogram of the number of games by total moves
    total_moves = [game.total_moves for game in all_game_metrics]
    plt.figure(figsize=(10, 6))
    hist_values, bin_edges, _ = plt.hist(total_moves, bins=range(min(total_moves), max(total_moves) + 1, 1), edgecolor='black')
    plt.xlabel('Total Moves')
    plt.ylabel('Number of Games')
    plt.title('Histogram of Total Moves in Games')
    plt.grid(axis='y')
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])  # Calculate the center of each bin
    plt.xticks(bin_centers, [str(int(x)) for x in bin_centers])  # Set x-tick labels to move counts

    plt.show()

    # 2. Bar chart showing which move number has the highest average time
    max_moves = max(total_moves)
    move_times = np.zeros(max_moves)
    move_counts = np.zeros(max_moves)

    for game in all_game_metrics:
        for move, move_time in game.individual_move_times:
            move_times[move-1] += move_time
            move_counts[move-1] += 1

    average_move_times = (move_times / move_counts) * 1000
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, max_moves + 1), average_move_times, edgecolor='black')
    plt.xlabel('Move Number')
    plt.ylabel('Average Move Time (ms)')
    plt.title('Average Move Time by Move Number')
    plt.grid(axis='y')
    plt.show()

    # 3. Scatter plot comparing total running time to total moves
    total_running_time = [game.total_running_time for game in all_game_metrics]
    plt.figure(figsize=(10, 6))
    plt.scatter(total_moves, total_running_time, edgecolor='black')
    plt.xlabel('Total Moves')
    plt.ylabel('Total Running Time (s)')
    plt.title('Total Running Time vs Total Moves')
    plt.grid(True)
    plt.show()
