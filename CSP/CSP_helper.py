from typing import Tuple
from Grid_10 import Grid


def sum_domains(assignment_map: dict) -> int:
    sum_total = 0
    for ship in assignment_map.keys():
        sum_total += len(assignment_map[ship])
    return sum_total


def size_3_ship_id(assignment_map: dict) -> str:
    """
    since there are 2 ships with size 3, we want to distinguish them when needing a label
    """
    # this function sucks, should be more precise with purpose
    if len(assignment_map['S31']) == 1:
        return 'S32'
    return 'S31'
def get_full_ship_coords(value: Tuple[int,int,bool], size: int):
    hit_coords = []
    x, y, v = value
    if v == True:
        for i in range(size):
            hit_coords.append((x, y+i))
    else:
        for i in range(size):
            hit_coords.append((x-i, y))
    return hit_coords
def ship_has_empty_spaces(board: Grid, ship: str, assignment):
    value = assignment.map[ship].pop()
    assignment.map[ship] = [value]
    size = int(ship[1])
    for x, y in get_full_ship_coords(value, size):
        if board.map[y][x] == Grid.SPACE['empty']:
            return True
    return False
def get_direction_to_coord(from_coord: Tuple[int,int], to_coord: Tuple[int,int]) -> str:
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
def move_towards(direction: str, from_coord: Tuple[int,int], to_coord: Tuple[int,int], board: Grid):
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
