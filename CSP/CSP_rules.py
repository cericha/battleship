from CSP.CSP_helper import *
"""
This contains functions that adjust an assignment based off the rules:
1. No ship can overlap another
2. No ship can occupy a 'miss' space
3. No ship can go outside the bounds of the grid
"""
def out_of_bounds_adjust(var, assignment_map):
    size = int(var[1])
    to_be_removed = []
    for X,Y,V in assignment_map[var]:
        if V == True and Y > 10-size: # magic 10, sorry. just grid size
            to_be_removed.append((X,Y,V)) # goes down too much
        elif V == False and X < size-1:
            to_be_removed.append((X,Y,V)) # goes left too much
    for item in to_be_removed:
        assignment_map[var].remove(item)


def adjust_assignment( ship, value, assignment_map):
    assignment_map[ship] = [value]
    size = int(ship[1])
    hit_ship_coords = get_full_ship_coords(value, size)
    to_be_adjusted = []
    for other_ship in assignment_map.keys():
        if other_ship != ship and len(assignment_map[other_ship])!=1:
            to_be_removed = []
            for other_value in assignment_map[other_ship]:
                other_coords = get_full_ship_coords(other_value, int(other_ship[1]))
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
        
        adjust_assignment(other_ship, assignment_map[other_ship][0], assignment_map)
def is_solved(assignment_map):
    for variable in assignment_map.keys():
        if len(assignment_map[variable]) != 1:
            return False
    return True
    
def sunk_adjust_assignment(sunk_coord, hunting, board, assignment_map):
    """
    If we've sunk a ship, travel in the opposite direction that was used for hunting until we've marked all hits.
    Edge case if we accidentally sink a ship that was not originally hit
    """
    # 1. Find direction to move based on hunting coord
    direction = 'IDKYET'
    
    hx, hy = hunting[0][0]
    sx, sy = sunk_coord
    direction = get_direction_to_coord(sunk_coord, hunting[0][0])
    # 2. Get ship label
    size = board.map[sy][sx].size
    ship_id = 'S' + str(size)

    if board.map[sy][sx].size == 3:
        ship_id = size_3_ship_id(assignment_map)
    # 3. Begin checking the board
    if direction == 'UP':
        count = 1
        while count < size:
            hunting[0].remove((sx, sy-count))
            count += 1
        val = (sx, sy-count+1, True)
        adjust_assignment(ship_id, (sx, sy-count+1, True), assignment_map)
    elif direction == 'DOWN':
        count = 1
        while count < size:
            hunting[0].remove((sx, sy+count))
            count += 1
        val = (sx, sy, True)
        adjust_assignment(ship_id, (sx, sy, True), assignment_map)
    elif direction == 'LEFT':
        count = 1
        while count < size:
            hunting[0].remove((sx-count, sy))
            count += 1
        val = (sx, sy, False)
        adjust_assignment(ship_id, val, assignment_map)
    elif direction == 'RIGHT':
        count = 1
        while count < size:
            hunting[0].remove((sx+count, sy))
            count += 1
        val = (sx+count-1, sy, False)
        adjust_assignment(ship_id, val, assignment_map)
    while hunting != False and len(hunting[0]) == 0:
        hunting.pop(0)
        if len(hunting) == 0:
            hunting = False
    return hunting
    

def miss_adjust_assignment(miss_coord, assignment_map):
    """
    If we miss on some coord, any assignment that places the ship on that coord is invalid
    """
    # TODO: fix!! this isn't working right
    x_miss, y_miss = miss_coord
    if x_miss < 0 or y_miss < 0:
        print("something went wrong!!")
        
    for ship in assignment_map.keys():
        size = int(ship[1])
        to_be_removed = []
        for X,Y,V in assignment_map[ship]:
            ship_coords = get_full_ship_coords((X,Y,V), size)
            if miss_coord in ship_coords:
                to_be_removed.append((X,Y,V))
        for item in to_be_removed:
            assignment_map[ship].remove(item)
def hit_adjust_assignment(ship, hit_coords, assignment_map):
    """
    if we know there's a hit, we can reduce the assignment based on intersections
    """
    size = int(ship[1])
    to_be_removed = []
    
    for X,Y,V in assignment_map[ship]:
        ship_coords = get_full_ship_coords((X,Y,V), size)
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
    
