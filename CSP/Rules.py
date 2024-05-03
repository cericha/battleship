from CSPAI import VARIABLES, DOMAIN, SHIP_LABELS

# def no_out_of_bounds(assignment_map, params = None):
#     """
#     ships can't be placed so their body goes out of bounds
#     """
    
#     for ship in SHIP_LABELS:
#         size = int(ship)
#         to_be_removed = []
#         for value in assignment_map[ship]:
#             x = value[0]
#             y = value[1]
#             v = value[2]
#             # if vertical
#             if v == True:
#                 if y > 10 - size: # magic 10, is the size of our board 
#                     to_be_removed.append(value)
#             # if horizontal
#             if v == False:
#                 if x < size-1:
#                     to_be_removed.append(value)
#         for value in to_be_removed:
#             assignment_map[ship].remove(value)

# def no_overlap(assignment_map, params):
#     """
#     If a ship is assigned, other ships cannot have options that overlap
#     params must be of form:
#     [ship_label]
#     """

#     # find assigned ships 
#     sunken = []
#     not_sunken = []
#     for ship in SHIP_LABELS:
#         if len(assignment_map[ship]) == 1:
#             sunken.append(ship)
#         else:
#             not_sunken.append(ship)

#     # for each fully assigned ship, find squares that it occupies
#     for sunk_ship in sunken:
#         x = assignment_map[sunk_ship][0]
#         y = assignment_map[sunk_ship][1]
#         v = assignment_map[sunk_ship][2]
#         sunk_size = int(sunk_ship[0])
#         # first need to know which squares are taken
#         coords_hit = [(x,y)]
#         for i in range(1,sunk_size):
#             if v:
#                 coords_hit.append((x, y+i))
#             else:
#                 coords_hit.append((x+i, y))
    
#     # then remove bad placements
#     to_be_removed = []
#     for ship in not_sunken:
#         x = assignment_map[ship][0]
#         y = assignment_map[ship][1]
#         v = assignment_map[ship][2]
#         if (x,y) in coords_hit:


# ---------- SPLIT ------------


def vertical_domain(assignment_map):
    """
    any V variable can only be True or False
    """
    for var in VARIABLES:
        if var[0] == 'V':
            for value in DOMAIN:
                if value != True or value != False:
                    assignment_map[var].remove(value)

def coord_domain(assignment_map):
    """
    any X or Y variable can only be numeric
    """
    for var in VARIABLES:
        if var[0] == 'X' or var[0] == 'Y':
            for value in DOMAIN:
                if value == True or value == False:
                    assignment_map[var].remove(value)

def no_out_of_bounds_v(assignment_map):
    pass


def no_ship_overlap(assignment_map):
    """
    if all 3 variables for a ship are assigned, we know certain spots that cannot be possible for X, Y of other ships
    only call this after completing the sub_problem of sinking a ship
    """
    fully_assigned = []
    not_fully = []
    # find ships 
    for ship in SHIP_LABELS:
        X_assigned = len(assignment_map['X'+ship]) == 1
        Y_assigned = len(assignment_map['Y'+ship]) == 1
        V_assigned = len(assignment_map['V'+ship]) == 1
        if X_assigned and Y_assigned and V_assigned:
            fully_assigned.append(ship)
        elif V_assigned:
            not_fully.append(ship)
    # for each fully assigned ship, remove the squares that it occupies from the X,Y of not_full ships
    for sunk_ship in fully_assigned:
        # THIS IS WHERE I REALIZED
        for ship in not_fully:
            pass