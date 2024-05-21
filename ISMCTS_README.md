# Running
Run Information Set Monte Carlo Tree Search solution with below
```
python3 Battleship.py ISMCTS.json
```
Some notable variables/configurations you may want to change:
- display: whether or not we show the board
- times_to_run: how many times we run the simulated game
- cores_to_use: how many cores to be used for parallel simulation
- Current number of iterations is set to 100 in Battleship.py

After the games run, there will be average metrics printed to console and 3 metric graphs created


# Objective

Find the hidden board with the smallest amount of guesses. 

# Implementation

Information Set Monte Carlo Tree Search
- Given that battleship is a POMDP, implements Information Set MCTS which is meant to be used for games or contexts of hidden information


# Future work/potential improvements

- Taking a random distribution of random ship placements, and then catoring the algorithm such that it knows the probability of a ship in a cell could improve results.

- Improvements in the information set generation could lead to more efficient results, as well as have more directed determinizations.

- Ignoring nodes which read the same "board" as other nodes have chosen, or having that be part of the calculation (if two nodes reach the same determinization from different steps, it's the same board state at that time)

- Using other UCT / UCB1 algorithms, changing the weights, and seeing if the results improve

- Smaller boards show better results, as large boards have very large information sets, and the depth of the tree is as a result smaller. 