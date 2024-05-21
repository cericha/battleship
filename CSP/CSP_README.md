# Running
To run this program using the CSP solution, run:
```
python3 Battleship.py csp_game.json
```
Some notable variables/configurations you may want to change:
- display: whether or not we show the board
- times_to_run: how many times we run the simulated game
- cores_to_use: how many cores to be used for parallel simulation

After the games run, there will be average metrics printed to console and 3 metric graphs created

# Objective
Find the hidden board with the smallest amount of guesses. 

# Implementation

CSP:
1. Variables
    - placement of ship
2. Domain
    - coordinate of head and verticality, (X,Y,V)
3. Constraints
    - No ship may overlap another
    - No ship may overlap a miss
    - No ship may go out of bounds
    - The ship must match the hidden enemy board
    - Soft Constraint: ships should overlap cells that have been hit

We will be tracking an assignment for the CSP, and sometimes coordinates that have been hit for hunting

### Normal GetMove
The default is to run backtracking on our current assignment, then once a non-failure result is given, we save the guess that started it all and retrieve a coordinate to return as the proposed move. However, upon further investigation, because of the nature of this problem we can return our backtracking extremely early (on the first step!) because the most important data is from hitting the board, not from looking forward to see if a solution works. The ordered domain values are a good enough heuristic for making a guess on the board.
### Updating based on previous move
If we miss, we just update the assignment so that no option has a ship overlapping the missed spot
If we hit, we enter the hunting subproblem because we can't really reduce the assignment domains until we know which ship has been hit.
If we sink, we update the assignment so no ships overlap the sunk ship's coordinates
### Subproblem for hunting a ship after a hit

The soft constraint of having a ship overlap hit cells is not enough. For many cases this makes sense, because if 2 hits are in the same row they have a good chance to belong to the same ship. However, this is not always the case and so we cannot make that full assumption. Instead, we hunt until we find that no ship can satisfy that constraint. When that happens, we know we've found an edge case where ships are stacked next to each other. When that happens, we shift our hunting problem to instead be a list of hunting problems, and we begin going through them until we sink a ship. When hunting we allow ourselves to apply the soft constraint to our assignment and then run the normal CSP backtracking algorithm, which sets the best guess possible based on our assignment.


### How to Choose
Pure CSP is not enough, there is a hidden part to our normal constraints: Our solution must match the hidden enemy board. Our goal is to find this solution with the minimum number of guesses, so each guess should remove as many possibilities as possible.

This is how we decided the heuristic to determine the ordered domain values: We imagine an instance where our guess is 100% correct and one where we miss the board. We then sum up how many domain values were removed from those decisions. Then the first value we try is the one that removes the most. This yielded very good results


# Future work/potential improvements

- There could definitely be runtime improvements.
- The modeling of the edge cases for hunting could be a bit more clear