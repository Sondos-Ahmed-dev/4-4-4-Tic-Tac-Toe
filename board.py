import numpy as np

class Board:
    def __init__(self):
        self.size = 4
        self.board = [[[0 for _ in range(self.size)] for _ in range(self.size)] for _ in range(self.size)]

    def make_move(self, z, y, x, player):
        self.board[z][y][x] = player
        
    def is_valid_move(self, z, y, x):
        if not (0 <= z < self.size and 0 <= y < self.size and 0 <= x < self.size):
            return False
        if self.board[z][y][x] == 0:
            return True
        else:
            return False

    def get_available_moves(self):
        moves = []
        for z in range(self.size):
            for y in range(self.size):
                for x in range(self.size):
                    if self.board[z][y][x] == 0:
                        moves.append((z, y, x))
        return moves

    def get_winning_line(self, player):

        N = self.size
        board = self.board
        
        def check_line(positions):
            
            if all(board[z][y][x] == player for z,y,x in positions):
                return positions
            return None

        
        for z in range(N):
            
            for y in range(N):
                for x in range(N - 3):
                    line = [(z,y,x), (z,y,x+1), (z,y,x+2), (z,y,x+3)]
                    result = check_line(line)
                    if result:
                        return result
            
            
            for x in range(N):
                for y in range(N - 3):
                    line = [(z,y,x), (z,y+1,x), (z,y+2,x), (z,y+3,x)]
                    result = check_line(line)
                    if result:
                        return result
            
            
            line = [(z,0,0), (z,1,1), (z,2,2), (z,3,3)]
            result = check_line(line)
            if result:
                return result
            
            line = [(z,0,3), (z,1,2), (z,2,1), (z,3,0)]
            result = check_line(line)
            if result:
                return result
                
        
        for y in range(N):
            for x in range(N):
                line = [(0,y,x), (1,y,x), (2,y,x), (3,y,x)]
                result = check_line(line)
                if result:
                    return result
                    
        
        for y in range(N):
            line = [(0,y,0), (1,y,1), (2,y,2), (3,y,3)]
            result = check_line(line)
            if result:
                return result
            
            line = [(0,y,3), (1,y,2), (2,y,1), (3,y,0)]
            result = check_line(line)
            if result:
                return result
        
        for x in range(N):
            line = [(0,0,x), (1,1,x), (2,2,x), (3,3,x)]
            result = check_line(line)
            if result:
                return result
            
            line = [(0,3,x), (1,2,x), (2,1,x), (3,0,x)]
            result = check_line(line)
            if result:
                return result
                
        
        line = [(0,0,0), (1,1,1), (2,2,2), (3,3,3)]
        result = check_line(line)
        if result:
            return result
        
        line = [(0,0,3), (1,1,2), (2,2,1), (3,3,0)]
        result = check_line(line)
        if result:
            return result
        
        line = [(0,3,0), (1,2,1), (2,1,2), (3,0,3)]
        result = check_line(line)
        if result:
            return result
        
        line = [(0,3,3), (1,2,2), (2,1,1), (3,0,0)]
        result = check_line(line)
        if result:
            return result
            
        return None

    def check_win(self, board, player):
        return self.get_winning_line(player) is not None

    def is_game_over(self):
        if self.check_win(self.board, 1):
            return True
        if self.check_win(self.board, -1):
            return True
        if not self.get_available_moves():
            return True
        return False

    def print_board(self):
        N = self.size
        for z in range(N):
            print(f"\n--- Layer {z} ---")
            for y in range(N):
                row_display = ""
                for x in range(N):
                    if self.board[z][y][x] == 1:
                        char = 'X'
                    elif self.board[z][y][x] == -1:
                        char = 'O'
                    else:
                        char = '.'
                    row_display += f"{char} "
                print(row_display)
        print("------------------")