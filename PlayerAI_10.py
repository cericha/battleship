import random
# This is akin to BaseAI in HW2, each member will make their own class with some method of getting move

class PlayerAI:
    def getMove(self, board):
        x = random.randint(0,9)
        y = random.randint(0,9)
        return (x,y)