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
We will be tracking an assignment for the CSP, and sometimes coordinates that have been hit for hunting
### Normal GetMove
The default is to run backtracking on our current assignment, then once a non-failure result is given, we save the guess that started it all and retrieve a coordinate to return as the proposed move.
### Updating based on previous move
If we miss, we just update the assignment so that no option has a ship overlapping the missed spot
If we hit, we enter the hunting subproblem because we can't really reduce the assignment domains until we know which ship has been hit.
If we sink, we update the assignment so no ships overlap the sunk ship's coordinates
### Subproblem for hunting a ship after a hit
#### Those dang edge cases

### How to Choose
Pure CSP is not enough, there is a hidden part to our normal constraints: Our solution must match the hidden enemy board. Our goal is to find this solution with the minimum number of guesses.

In deciding how to search through a CSP we consider the following:

1. Which variable should be assigned next?
	1. MRV, minimum remaining values:
		1. simply check the size of domains
2. In what order should its values be tried?
	1. LCV, least constraining value:
       - This actually isn't entirely appropriate for this augmented problem
    2. Instead, we try to make future guesses more likely to hit something, so we're trying to restrict future variables as much as we can
3. Can we detect inevitable failure early?
    1. The only way we find out is after making a move on the board, but as we go along we adjust our assignment

Issue with the amount of global constraints that exist when we model the problem as each ship has 3 variables

# Results
Average metrics over 100 games:
total_time_average: 9.667350461483002
total_move_average: 42.69
max_ram_usage_average: 12.871875

# Future work/potential improvements
