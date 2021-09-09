# A class to keep pieces' positions on a board
# Notice that when we create a Position, we firstly specify y and then x, unlike we are used to!
class Position:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        
    def add(self, y, x):
        return Position(self.y + y, self.x + x)
    
    # Return a position in the middle between this position and another position
    def middle(self, other):
        return Position(int((self.y+other.y)/2), int((self.x+other.x)/2))

    def __str__(self):
        return str(self.x) + " : " + str(self.y)
