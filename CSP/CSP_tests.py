from AI_FINAL_PROJ.battleship.CSP.CSPAI import Assignment, SHIP_LABELS, VARIABLES, DOMAIN
# Assignment
def changing_assignment_copy_doesnt_effect_original():
    original = Assignment()
    copy = original.copy()
    copy.adjust("V5", True)
    assert original == [1, 2, 3], "Changing the copy should not affect the original"

def changing_assignment_original_works():
    original = [1, 2, 3]
    copy = original
    original.append(4)
    assert copy == [1, 2, 3, 4], "Changes to the original should reflect in the copy when assigned directly"

def copy_assignment_works():
    original = [1, 2, 3]
    copy = original.copy()
    copy.append(4)
    assert original == [1, 2, 3], "Changes to the copy should not affect the original when using .copy()"
