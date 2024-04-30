# Objective
Find the hidden board with the smallest amount of guesses. 


# Analysis
CSP:
1. Variables
2. Domain
3. Constraints

COMPLEXITY:

d = domain, n = variables
base: O(d^n)
c variables per subproblem: O((n/c) \* d^c)

| Variable Options  | Size (n)  | Domain Options | Domain Size (d)| Base Complexity (O(d^n)) | Subproblem Complexity (O(n/c * d^c))
|---|---|---|---|---|---
| Cells  | 100  | hit/miss | 2 | 2^100 = yikes | try in quadrants? 25 spaces each quadrant: 100/25 * 2^25 = 134217728 
| Ship Head Location  | 5  | Cell and Vertical/Horizontal | 200 | 200^5 = smaller yikes | try each ship? 1 ship at a time: 5/1 * 200^1 = 1000 Not Bad! but our model makes this a very awkward approach
| X, Y Coord for head, V verticality for each ship  | 15  | 0-9, True, False | 12 | 12^15 = yikes | try finding V -> X -> Y combo for each ship? 3 variable each iteration: 15/3 * 12^3 = 8640 Technically worse, BUT model is much easier to work with

# Implementation
Decide where to guess based on the selection order for a CSP.
### Subproblem for finding a ship
1. Start with ship of length 5 (MRV)
2. random assumption for V (MRV)
3. Depending on available X/Y for ship 5, start guessing spots that leave the most space for other ships (LCV)
4. Get result of guess:
    1. On Hit: Begin subproblem CSP to find sink the ship that was hit
    2. On Miss: Update All impossible values based on missed shot
6. Run CSP until we find the 3 piece combo, then go to next highest length ship that's not already solved (some may be solved by accident as we're guessing)

### Subproblem for sinking a ship

1. Assume x, y that's hit is the head of a ship
2. guess left/right or up/down to find V
3. guess until sink
4. update the 3 variables associated with the ship


### How to Choose
Pure CSP is not enough, there is a hidden part to our normal constraints: Our solution must match the hidden enemy board. Our goal is to find this solution with the minimum number of guesses.

In deciding how to search through a CSP we consider the following:

1. Which variable should be assigned next?
	1. MRV, minimum remaining values:
		1. V: Technically only 2 possible values for every ship, BUT depending on what's already been missed one may be more likely.
		2. X/Y: The original remaining values depends on the ship length and the assumed V because we don't want our ship going out of bounds.
2. In what order should its values be tried?
	1. LCV, least constraining value:
        - We want to choose coordinates that leave the most space available to the other ships. This means having the boat closer to the center. 
3. Can we detect inevitable failure early?
    1. The only way we find out is after making a move on the board