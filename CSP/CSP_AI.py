import copy
from typing import Tuple
from Grid_10 import Grid
from PlayerAI_10 import MoveStrategy
from Metrics_10 import Metrics
from Displayer_10 import Displayer
# TODO: fix these bugs:
# 1. sinking is janky because of the way we hunt
# 2. hunting 
displayer = Displayer()

VARIABLES = ["S5", "S4", "S31", "S32", "S2"]

DOMAIN = set()
for x in range(10):
    for y in range(10):
        for v in [True, False]:
            DOMAIN.add((x,y,v))
FAILURE = 'Failure'

class Assignment:
    """
    Object so we can do proper deep copies
    """
    def __init__(self, assignment_map):
        self.map = assignment_map
    def copy(self):
        return copy.deepcopy(self)

class CSPAI(MoveStrategy):
    def __init__(self):
        self.prev_move = None # Setting this so we can track the board response
        self.hunting = False # for subproblem, coordinates of a hit
        self.assignment = self.default_assignment()
        self.sunk = []
        self.best_guess = None # to track first move of backtracking
        self.metrics = Metrics(0,0)
    
    def move_from_guess(self, board):
        x,y,v = self.best_guess
        
        # This can accidentally fire our shot far
        while board.map[y][x] != Grid.SPACE['empty']:
            if v == True:
                y += 1
            else:
                x -= 1
        if self.hunting != False and (x,y) != self.hunting[0][0]:
            
            direction = self.get_direction_to_coord((x,y), self.hunting[0][0])
            
            closest_shot = self.move_towards(direction, (x,y), self.hunting[0][0], board)
            
            self.best_guess = (closest_shot[0], closest_shot[1], v)
            self.prev_move = closest_shot
            return closest_shot
        self.prev_move = (x,y)
        return (x,y)
    def get_move(self, board: Grid) -> Tuple[int, int]:
        prev_result = self.get_prev_move_result(board)
        
        # In sub-problem of hunting
        if self.hunting != False and prev_result != 'sunk':
            self.hunt(board, self.assignment)
            return self.move_from_guess(board)

        # Adjust Alogirthm based on prev_move (if appropriate)
        elif prev_result == 'hit':
            self.hunting = [[]]
            self.hunt(board, self.assignment)
            return self.move_from_guess(board)
        elif prev_result == 'sunk':
            self.sunk_adjust_assignment(self.prev_move, board, self.assignment)
            # try get move again incase our sunk ship doesn't account for all hit spaces 
            if self.hunting != False:
                self.hunt(board, self.assignment)
                return self.move_from_guess(board)
            self.prev_move = None
            return self.get_move(board) # TODO: this may cause infinite looping
        elif prev_result == 'miss':
            
            total = self.sum_domains(self.assignment.map)
            self.miss_adjust_assignment(self.prev_move, self.assignment.map)
            
        
        # If we already know for sure where everything is, just start going for it
        if self.is_solved(self.assignment):
            
            
            for variable in VARIABLES:
                if variable not in self.sunk:
                    self.best_guess = self.assignment.map[variable].pop()
                    self.assignment.map[variable] = self.best_guess
                    return self.move_from_guess(board)

        # Run augmented CSP 'backtracking'. the backtracking sets up our "best guess"
        self.backtrack(board, self.assignment)
        return self.move_from_guess(board)
    
    # ------------ Algorithms -----------------

    def backtrack(self, board, assignment: Assignment):
        """
        CSP root algorithm, once a hypothetical solution is found it sets self.best_guess to the first assumed value
        """
        if self.is_solved(assignment):
            return assignment
        MRV_ship = self.get_MRV_ship(assignment.map)
        if len(assignment.map[MRV_ship]) == 0:
            return FAILURE
        ordered_domains = self.ordered_domain_values(MRV_ship, assignment)
        for X, Y, V in ordered_domains:
            new_assignment = assignment.copy()
            self.adjust_assignment(MRV_ship, (X,Y,V), new_assignment.map)
            result = self.backtrack(board, new_assignment)
            if result != FAILURE:
                # Since we're ordering the domain by how restrictive it is, our best shot is the first assumption we make
                self.best_guess = (X,Y,V)
                return result
        
        return FAILURE
    def ordered_domain_values(self, ship, assignment: Assignment):
        """
        returns sorted list of domain values for some ship
        """
        sum_domain = self.sum_domains(assignment.map)
        domain_values = []
        for X, Y, V in assignment.map[ship]:
            shot = (X, Y) # just doing this for clarity
            pretend_hit_assignment = assignment.copy()
            pretend_miss_assignment = assignment.copy()
            self.adjust_assignment(ship, (X,Y,V), pretend_hit_assignment.map)
            self.miss_adjust_assignment(shot, pretend_miss_assignment.map)
            hit_reduction = sum_domain - self.sum_domains(pretend_hit_assignment.map)
            miss_reduction = sum_domain - self.sum_domains(pretend_miss_assignment.map)
            total_reduction = hit_reduction + miss_reduction
            domain_values.append((total_reduction, (X,Y,V)))
        ordered_values_pairs = sorted(domain_values, key=lambda item: item[0])
        ordered_values_pairs.reverse()
        ordered_values = [value for _, value in ordered_values_pairs]
        return ordered_values
    
    def hunt(self, board, assignment):
        """
        If we know we've hit a boat, first adjust the mrv_ship and then try best guess
        """
        # TODO: adjust implementation
        
        # 1. Adjust based on last move
        if self.get_prev_move_result(board) == 'miss':
            self.miss_adjust_assignment(self.prev_move, self.assignment.map)
        elif self.get_prev_move_result(board) == 'hit':
            self.hunting[0].append(self.prev_move)
        
        # 2. try to find potential valid ship to use
        MRV_ship = self.get_MRV_ship(assignment.map)
        new_assignment = assignment.copy()
        
        # 2.a if there are multiple hunting lists, make sure to disinclude the others
        if len(self.hunting) > 1:
            
            for i in range(1,len(self.hunting)):
                self.miss_adjust_assignment(self.hunting[i][0], new_assignment.map)
        self.hit_adjust_assignment(MRV_ship, self.hunting[0], new_assignment.map)
        result = self.backtrack(board, new_assignment)
        while result == FAILURE:
            
            
            MRV_ship_size = int(MRV_ship[1])
            new_size = MRV_ship_size - 1
            if new_size==3:
                
                MRV_ship = self.size_3_ship_id()
            elif new_size != 1:
                MRV_ship = 'S' + str(new_size)
            else:
                
                break
            
            new_assignment = self.assignment.copy()
            self.hit_adjust_assignment(MRV_ship, self.hunting[0], new_assignment.map)
            result = self.backtrack(board, new_assignment)
        
        # 3. check for single option edge case
        if len(new_assignment.map[MRV_ship]) == 1:
            self.best_guess = new_assignment.map[MRV_ship].pop()
            guess_coords = self.get_full_ship_coords(self.best_guess, int(MRV_ship[1]))
            show_coords([(x,y,self.best_guess[2]) for x,y in guess_coords])
            for x,y in guess_coords:
                # 3.a it's valid because there's an empty space we can fire on
                if board.map[y][x] == Grid.SPACE['empty']:
                    return
            
            # 4. it's not valid because there are no empty spaces
            # two options:
            # 4.a both ends cut off, each coord is its own hunting problem
            # 4.b some end must be free, return that for now
            x,y,v = self.best_guess
            
            size = int(MRV_ship[1])
            if v == True:
                above_empty = board.map[y-1][x] == Grid.SPACE['empty'] and y > 0
                below_empty = board.map[y+size][x] == Grid.SPACE['empty'] and y+size <= 9
                # 4.a # TODO: fix 4.a for both options, we have to also make sure it's known that the other options in hunting cannot be a part of each other
                if not above_empty and not below_empty:
                    
                    new_hunting = []
                    for coord in self.hunting[0]:
                        new_hunting.append([coord])
                    self.hunting = new_hunting
                    return self.hunt(board, assignment)
                # 4.b
                elif above_empty:
                    self.best_guess = (x,y-1,v)
                elif below_empty:
                    self.best_guess = (x,y+size,v)
            elif v == False:
                left_empty = board.map[y][x+1] == Grid.SPACE['empty'] and x < 9
                right_empty = board.map[y][x-size] == Grid.SPACE['empty'] and x-size >= 0
                # 4.a
                if not left_empty and not right_empty:
                    
                    new_hunting = []
                    for coord in self.hunting[0]:
                        new_hunting.append([coord])
                    self.hunting = new_hunting
                    return self.hunt(board, assignment)
                # 4.b
                elif left_empty:
                    self.best_guess = (x+1,y,v)
                elif right_empty:
                    self.best_guess = (x-size,y,v)
        
        show_ship(MRV_ship, self.best_guess)

    # ------------ Helper ---------------------
    def get_MRV_ship(self, assignment_map):
        """
        will not return length 1 assignments
        will return length 0 assignment for error
        will return other lengths as possible assignments
        """
        mrv_ship = 'X'
        mrv_ship_domain = 201
        for ship in VARIABLES:
            ship_domain = len(assignment_map[ship])
            if ship_domain < mrv_ship_domain and ship_domain != 1:
                mrv_ship = ship
                mrv_ship_domain = ship_domain
        return mrv_ship
    def sum_domains(self, assignment_map):
        sum_total = 0
        for ship in VARIABLES:
            sum_total += len(assignment_map[ship])
        return sum_total

    def adjust_assignment(self, ship, value, assignment_map):
        assignment_map[ship] = [value]
        size = int(ship[1])
        hit_ship_coords = self.get_full_ship_coords(value, size)
        to_be_adjusted = []
        for other_ship in VARIABLES:
            if other_ship != ship and len(assignment_map[other_ship])!=1:
                to_be_removed = []
                for other_value in assignment_map[other_ship]:
                    other_coords = self.get_full_ship_coords(other_value, int(other_ship[1]))
                    for cell in other_coords:
                        # if this assignment overlaps at all with the sunk ship, then remove it
                        if cell in hit_ship_coords:
                            to_be_removed.append(other_value)
                            break
                for item in to_be_removed:
                    assignment_map[other_ship].remove(item)
                if len(assignment_map[other_ship]) == 1:
                    to_be_adjusted.append(other_ship)
                elif len(assignment_map[other_ship]) == 0:
                    return
        for other_ship in to_be_adjusted:
            
            self.adjust_assignment(other_ship, assignment_map[other_ship][0], assignment_map)
    def is_solved(self, assignment):
        for variable in VARIABLES:
            if len(assignment.map[variable]) != 1:
                return False
        return True
        
    def sunk_adjust_assignment(self, sunk_coord, board, assignment_map):
        """
        If we've sunk a ship, travel in the opposite direction that was used for hunting until we've marked all hits.
        Edge case if we accidentally sink a ship that was not originally hit
        """
        # 1. Find direction to move based on hunting coord
        direction = 'IDKYET'
        
        hx, hy = self.hunting[0][0]
        sx, sy = sunk_coord
        direction = self.get_direction_to_coord(sunk_coord, self.hunting[0][0])
        # 2. Get ship label
        size = board.map[sy][sx].size
        ship_id = 'S' + str(size)
        
        
        
        
        if board.map[sy][sx].size == 3:
            ship_id = self.size_3_ship_id()
        # 3. Begin checking the board
        if direction == 'UP':
            count = 1
            while count < size:
                self.hunting[0].remove((sx, sy-count))
                count += 1
            self.adjust_assignment(ship_id, (sx, sy-count+1, True), self.assignment.map)
        elif direction == 'DOWN':
            count = 1
            while count < size:
                self.hunting[0].remove((sx, sy+count))
                count += 1
            self.adjust_assignment(ship_id, (sx, sy, True), self.assignment.map)
        elif direction == 'LEFT':
            count = 1
            while count < size:
                self.hunting[0].remove((sx-count, sy))
                count += 1
            self.adjust_assignment(ship_id, (sx, sy, False), self.assignment.map)
        elif direction == 'RIGHT':
            count = 1
            while count < size:
                self.hunting[0].remove((sx+count, sy))
                count += 1
            self.adjust_assignment(ship_id, (sx+count-1, sy, False), self.assignment.map)
        while self.hunting != False and len(self.hunting[0]) == 0:
            self.hunting.pop(0)
            if len(self.hunting) == 0:
                self.hunting = False
        # If we keep traveling the direction and see a hit, that means we need to continue hunting
        
        show_ship(ship_id, self.assignment.map[ship_id][0])
        self.sunk.append(ship_id)
        

    def miss_adjust_assignment(self, coord, assignment_map):
        """
        If we miss on some coord, any assignment that places the ship on that coord is invalid
        """
        # TODO: fix!! this isn't working right
        x_miss, y_miss = coord
        if x_miss <0 or y_miss < 0:
            print("something went wrong!!")
            
        for ship in VARIABLES:
            size = int(ship[1])
            
            to_be_removed = []
            for X,Y,V in assignment_map[ship]:
                ship_coords = self.get_full_ship_coords((X,Y,V), size)
                if coord in ship_coords:
                    to_be_removed.append((X,Y,V))
            for item in to_be_removed:
                assignment_map[ship].remove(item)
    def hit_adjust_assignment(self, ship, hit_coords, assignment_map):
        """
        if we know there's a hit, we can reduce the assignment based on intersections
        """
        size = int(ship[1])
        to_be_removed = []
        
        for X,Y,V in assignment_map[ship]:
            ship_coords = self.get_full_ship_coords((X,Y,V), size)
            full_intersect = True
            for hit_coord in hit_coords:
                if hit_coord not in ship_coords:
                    # 
                    # show_ship(ship, (X,Y,V))
                    # 
                    # show_coords([(x,y,True) for x,y in hit_coords])
                    full_intersect = False
                    break
            if full_intersect != True:
                to_be_removed.append((X,Y,V))
        for item in to_be_removed:
            assignment_map[ship].remove(item)
        # 
        # 
        # for value in assignment_map[ship]:
        #     show_ship(ship, value)
        #     show_coords([(x,y,True) for x,y in hit_coords])


    def size_3_ship_id(self):
        """
        since there are 2 ships with size 3, we want to distinguish them when needing a label
        """
        if len(self.assignment.map['S31']) == 1:
            return 'S32'
        return 'S31'
    def get_full_ship_coords(self, value, size):
        hit_coords = []
        x, y, v = value
        if v == True:
            for i in range(size):
                hit_coords.append((x, y+i))
        else:
            for i in range(size):
                hit_coords.append((x-i, y))
        return hit_coords
    def get_direction_to_coord(self, from_coord, to_coord):
        direction = 'idkyet'
        fx, fy = from_coord
        tx, ty = to_coord
        # if same column
        if fx == tx:
            # above
            if ty < fy:
                direction = 'UP'
            # below
            else:
                direction = 'DOWN'
        # if same row
        elif fy == ty:
            # left
            if tx < fx:
                direction = 'LEFT'
            # right
            else:
                direction = 'RIGHT'
        return direction
    def move_towards(self, direction, from_coord, to_coord, board: Grid):
        """
        assuming from and to are on either the same row or col, move in a direction until you reach it
        """
        fx, fy = from_coord
        tx, ty = to_coord
        
        if direction == 'UP':
            while fy > ty+1 and board.map[fy-1][fx] == Grid.SPACE['empty']:
                fy -= 1
        if direction == 'DOWN':
            while fy < ty-1 and board.map[fy+1][fx] == Grid.SPACE['empty']:
                fy += 1
        if direction == 'LEFT':
            while fx > tx+1 and board.map[fy][fx-1] == Grid.SPACE['empty']:
                fx -= 1
        if direction == 'RIGHT':
            while fx < tx-1 and board.map[fy][fx+1] == Grid.SPACE['empty']:
                fx += 1
        
        return (fx, fy)

    def default_assignment(self):
        """
        All placements for ships that are in bounds
        """
        assignment_map = {}
        for var in VARIABLES:
            assignment_map[var] = set(DOMAIN)
            self.out_of_bounds_adjust(var, assignment_map)
        return Assignment(assignment_map)
    
    def out_of_bounds_adjust(self, var, assignment_map):
        size = int(var[1])
        to_be_removed = []
        for X,Y,V in assignment_map[var]:
            if V == True and Y > 10-size: # magic 10, sorry. just grid size
                to_be_removed.append((X,Y,V)) # goes down too much
            elif V == False and X < size-1:
                to_be_removed.append((X,Y,V)) # goes left too much
        for item in to_be_removed:
            assignment_map[var].remove(item)


def show_coords(value_list):
    pretend_board = Grid()
    for x,y,v in value_list:
        pretend_board.map[y][x] = 'X'
    displayer.display(pretend_board)
def show_ship(ship, value):
    pretend_board = Grid()
    size = int(ship[1])
    x,y,v = value
    if v == True:
        for i in range(size):
            pretend_board.map[y+i][x] = 1
    else:
        for i in range(size):
            pretend_board.map[y][x-i] = 1
    displayer.display(pretend_board)
