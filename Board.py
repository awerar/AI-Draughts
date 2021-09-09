import math
import copy
import numpy as np
from PIL import Image, ImageColor
import IPython.display

from Piece import Piece
from Position import Position
from Graphics import draw_circle


# The Board class keeps the state of the game at a given time. It's most important fields are: whites (a list of all the white pawns on the board), blacks (a list of all the black pawns on the board), world (a two-dimentional list, representing the board. Each field is either null (if there is no piece standing there) or it points to a piece which stands at a given place).
# Therefore, we have a double information about each piece

# White is the player, who moves next (this makes implementation easier: we don't have to 'if' everywhere whose move it is)
# Rows are represented by 'y' axis, columns by 'x' axis. Both are indexed from 0 to 9. (0, 0) is the left-upper square


class Board:
    # Create a new white piece at position (y, x) and add it to the whites list
    def newWhite(self, y, x, king=False):
        white = Piece.whitePiece(y, x, king)
        self.whites += [white]
        return white
    
    
    # Create a new black piece at position (y, x) and add it to the whites list
    def newBlack(self, y, x, king=False):
        black = Piece.blackPiece(y, x, king)
        self.blacks += [black]
        return black
    
    
    # Check if a Position where is on the board
    def on_board(self, where):
        return 0 <= where.y and where.y < 10 and 0 <= where.x and where.x < 10
    
    
    # Check if the given position is on the board and is occupied by a white piece
    def isWhite(self, where):
        # Check, if the Position is on the board
        if not self.on_board(where):
            return False
        # Check, if the Position where is occupied by any piece
        if self.world[where.y][where.x] is None:
            return False
        # Check, if the Position is occupied by a white piece
        return self.world[where.y][where.x].white
    
    
    # Check if the given position is on the board and is occupied by a black piece
    def isBlack(self, where):
        if not self.on_board(where):
            return False
        if self.world[where.y][where.x] is None:
            return False
        return not self.world[where.y][where.x].white
    
    
    # Check if the given position is on the board and isn't occupied
    def isEmpty(self, where):
        if not self.on_board(where):
            return False
        return self.world[where.y][where.x] is None
    
    
    # Check if the white player cannot make any move and therefore has just lost
    def white_lost(self):
        # If white has no pieces left, they cannot make any move and so have lost
        if len(self.whites) == 0:
            return True
     
        # If white can capture an opponents piece, they can make a move and so haven't lost yet
        if self.capture_possible():
            return False
        # If white can make a non-capturing move, they can make a move and so haven't lost yet
        if self.normal_move_possible():
            return False
        return True
    
    
    # Check if it is possible for the white player to capture an opponent's piece
    def capture_possible(self):
        # Iterate over all the white pieces
        for white in self.whites:
            # Consider different cases, depending on wether a piece is a king or not
            if not white.king:
                for i in [-1, 1]:
                    if self.isBlack(white.position().add(1, i)):
                        if self.isEmpty(white.position().add(2, 2*i)):
                            return True
            else:
                # Iterate over possible directions of movement
                for xi in [-1, 1]:
                    for yi in [-1, 1]:
                        where = white.position().add(yi, xi)
                        # Go in that direction, until an occuppied field is found or we reach the end of the board
                        while (self.isEmpty(where)):
                            where = where.add(yi, xi)
                        if self.isBlack(where) and self.isEmpty(where.add(yi, xi)):
                            return True
        return False
    
    
    # Check if a non-capturing move is possible
    def normal_move_possible(self):
        # Iterate over all the white pieces
        for white in self.whites:
            for i in [-1, 1]:
                # If a piece is a man, check only if a forward-left or forward-right field is empty
                if self.isEmpty(white.position().add(1, i)):
                    return True
                # If it's a king, check also if a backward-left or backward-right field is empty
                if white.king and self.isEmpty(white.position().add(-1, i)):
                    return True
        return False
    
    
    # Initializes the board to a starting configuration
    def __init__(self):
        self.whites = []
        self.blacks = []
        # Create white and black pieces on appropriate positions and add them to the board's world
        self.world = [[(self.newWhite(y, x) if y < 3 else self.newBlack(y, x))
                           if ((x + y) % 2 == 0 and (y < 3 or y > 6)) else None 
                    for x in range(10)]
                    for y in range(10)]
    
    
    # Initializes an empty board (with no pieces on it)
    @staticmethod
    def empty_board():
        to_return = Board()
        to_return.whites = []
        to_return.blacks = []
        to_return.world = [[None for x in range(10)] for y in range(10)]
        return to_return
    
    
    # Returns a safe copy of the board - we can edit it without changing the copied board
    def copy(self):
        new_board = Board.empty_board()
        new_board.whites = []
        new_board.blacks = []
        
        for white in self.whites:
            new_board.world[white.y][white.x] = new_board.newWhite(white.y, white.x, white.king)
            
        for black in self.blacks:
            new_board.world[black.y][black.x] = new_board.newBlack(black.y, black.x, black.king)
            
        return new_board
        
        
    # Returns a new board, which is a copy of this board turned around and with all the pieces' colours reversed.
    # We use this function at the end of each move, so that in the
    # internal representation the player who is about to move is always white
    def revert(self):
        new_board = self.copy()
        
        # First, swap the lists of white and black colours
        new_board.whites, new_board.blacks = new_board.blacks, new_board.whites
        # Then change a colour of each piece
        for piece in new_board.whites + new_board.blacks:
            piece.changeColour()

        # Move each piece symmetrically across the board
        # First, change each piece's position
        for piece in new_board.whites + new_board.blacks:
            piece.move_symmetrically()
        # Now modify the world accordingly, so that each piece is kept in board at its correct position
        for x in range(10):
            for y in range(5):
                new_board.world[y][x], new_board.world[9 - y][9 - x] = new_board.world[9 - y][9 - x], new_board.world[y][x]

        return new_board
        
        
    # Return a state of board after a move. Notice that we don't change the state of this board, but return a new board which shows how it will look like after makinhg a move
    # moves should be a list of positions, which a moving place visits between its moves (see Game class for a detailed description)
    def make_move(self, moves):
        if len(moves) < 2:
            raise ValueError("You have to move to a new position", self, moves)
            
        new_board = self.copy()
        for i in range(len(moves) - 1):
            try:
                new_board = new_board.make_single_move(
                    moves[i], moves[i+1],
                    must_capture=(i > 0 or self.capture_possible()), first_move=(i == 0))
            except ValueError as ve:
                raise ve

        # If a piece ends its move on the end of a board, it is crowned
        piece = new_board.world[moves[-1].y][moves[-1].x]
        if piece.y == 9:
            piece.king = True

        # Inverting board at the end of a move, so that the player who moves is white in Board's internal representation
        return new_board.revert()
        
    
    # Return a state of a board after making a single move from one position to another (i. e., a single capture or a single step)
    def make_single_move(self, old, new, must_capture=False, first_move=True):
        #print(self.__str__())

        new_board = self.copy()
        piece = new_board.world[old.y][old.x]
        yi = np.sign(new.y - old.y)
        xi = np.sign(new.x - old.x)
        
        moves_log = {
            'move': [{'y': old.y, 'x': old.x}, {'y': new.y, 'x': new.x}],
            'must_capture': must_capture, 'first_move': first_move}
        if not self.isWhite(old):
            raise ValueError("You have to move your own piece", self, moves_log)
        if not self.isEmpty(new):
            raise ValueError("You have to move to an empty field", self, moves_log)
        
        
        if must_capture:
            if not piece.king:
                if abs(new.y - old.y) != 2 or abs(new.x - old.x) != 2 or (first_move and new.y - old.y != 2):
                    print(self.capture_possible(True))
                    raise ValueError("You have to capture", self, moves_log)
                if not self.isBlack(old.middle(new)):
                    raise ValueError("You have to capture an enemy", self, moves_log)

                # Update the new_board after this move - remove the captured black piece
                for black in new_board.blacks:
                    if black.y == old.y+1 and black.x == old.middle(new).x:
                        new_board.blacks.remove(black)
                        break
                new_board.world[old.middle(new).y][old.middle(new).x] = None
                
            else:
                if abs(new.y - old.y) != abs(new.x - old.x):
                    raise ValueError("You cannot move there - too far", self, [old.__str__(), new.__str__()])
                
                # Check if there is a black piece which was captured
                where = old.add(yi, xi)
                captured = []
                while where.y != new.y:
                    if self.isBlack(where):
                        captured += [where]
                        if not self.isEmpty(where.add(yi, xi)):
                            raise ValueError("You cannot capture more than one piece at one!", self, moves_log)
                    if self.isWhite(where):
                        raise ValueError("You cannot move over your own piece!", self, moves_log)
                    where = where.add(yi, xi)
                    
                if len(captured) == 0:
                    raise ValueError("You have to capture an enemy's piece", self, moves_log)
                
                # Update the new_board after this move - remove the captured black piece
                for captured_position in captured:
                    for black in new_board.blacks:
                        if black.y == captured_position.y and black.x == captured_position.x:
                            new_board.blacks.remove(black)
                            break
                    new_board.world[captured_position.y][captured_position.x] = None
                
        else:
            if not piece.king:
                if new.y - old.y != 1 or abs(new.x - old.x) != 1:
                    raise ValueError("The position is inaccessible for this piece", self, moves_log)
            else:
                if abs(new.y - old.y) != abs(new.x - old.x):
                    raise ValueError("You can only move diagonally", self, moves_log)
                
                where = old.add(yi, xi)
                while where.y != new.y:
                    if not self.isEmpty(where):
                        raise ValueError("You cannot move over this square", self, moves_log)
                    where = where.add(yi, xi)
                
                if not self.isEmpty(where):
                    raise ValueError("You cannot move to this square", self, moves_log)
        
        
        # Update the new_board after this move - change the position of the white piece who moved
        for white in new_board.whites:
            if white.y == old.y and white.x == old.x:
                white.x = new.x
                white.y = new.y
        new_board.world[new.y][new.x] = new_board.world[old.y][old.x]
        new_board.world[old.y][old.x] = None
        
        return new_board
    
    
    # Display the board
    def show(self, black_moves = False):
        if black_moves:
            self.revert().show()
            return
        
        white = (200, 255, 200)
        black = (0, 100, 0)
        
        size = 40
        img = Image.new("RGB", (10 * size, 10 * size))
        
        arr = np.array(img)
        arr[:] = (255, 255, 255)

        indices = np.arange(10)
        col_num = np.repeat(indices, size)
        col_num = np.tile(col_num, (size*10, 1))
        row_num = np.transpose(col_num)
        is_black = (col_num + row_num) % 2 == 0
        arr[is_black] = (0, 0, 0)

        for piece in self.whites + self.blacks:
            draw_circle(arr, size*piece.y + size/2, size*piece.x + size/2, 12, white if piece.white else black)
            if piece.king:
                draw_circle(arr, size*piece.y + size/2, size*piece.x + size/2, 4, black if piece.white else white)

        out = Image.fromarray(arr)
        display(out)

    def __str__(self):
        print("########")
        for y in range(0, 9):
            for x in range(0, 9):
                p = self.world[y][x]

                if p is None:
                    print("  ", end="")
                else:
                    print("w" if p.white else "b", end="")
                    print("k" if p.king else "m", end="")
                print(" ", end="")
            print()
        print("########")
