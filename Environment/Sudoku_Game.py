import math
import numpy as np
from threading import Lock

class Sudoku_Game:
    def __init__(self, sudoku_game, guessing=True):
        self.__original_sudoku_game = np.array(sudoku_game)
        self.__sudoku_game = np.array(sudoku_game)
        self.__createGroups()
        
        self.__guess = [] if guessing else None
    
    def valid_sudoku_game(self):
        for grouping in self.__groups:
            for group in grouping:
                seen = []
                for square in group:
                    game_square = self.__active_game_board[square]
                    if game_square.value in seen:
                        return False
                    elif (game_square.value != None):
                        seen.append(game_square.value)  
        return True
        
    def __instantiateEmpyGroups(self):
        r,c = self.__sudoku_game.shape
        groups = [
            [],
            [],
            [],
        ]
        for x in range(r):
            groups[0].append(set())
            groups[1].append(set())
            groups[2].append(set())
        return groups
        
    def __createGroups(self):
        r,c = self.__sudoku_game.shape
        groups = self.__instantiateEmpyGroups()
        game_board = {}
        for row in range(r):
            for col in range(c):
                box = math.floor(col/3) + 3*math.floor(row/3)
                value = self.__sudoku_game[row,col]
                value = value if value != 0 else None
                groups[0][row].add((row, col))
                groups[1][col].add((row, col))
                groups[2][box].add((row, col))
                game_board[(row,col)] = self.__Sudoku_Square(row, col, value = value)
        self.__active_game_board = game_board
        self.__groups = groups
    
    def __update_sudoku_game(self, row, col, value):
        self.__sudoku_game[row, col] = value
    
    def is_guessing(self):
        return self.__guess != None and len(self.__guess) > 0
    
    def update_game_square(self, dims, possibility, isGuess=False):  
        game_square = self.__active_game_board[dims]
        lock = game_square.lock
        with lock:
            if isGuess:
                game_square = self.__active_game_board[dims]
                game_square.update_square(possibility, None)
                self.__update_sudoku_game(dims[0], dims[1], game_square.value)
            elif game_square.value == None:
                game_square = self.__active_game_board[dims]
                game_square.remove_possibility(possibility)
                if game_square.value != None:
                    self.__update_sudoku_game(dims[0], dims[1], game_square.value)
    
    def view_sudoku_square(self, dims):
        game_square = self.__active_game_board[dims]
        return game_square.value if game_square.value != None else game_square.possibilities
    
    def get_sudoku_group(self, group):
        grouping = math.floor(group/9)
        g = group % 9
        return self.__groups[grouping][g]
    
    def get_allsquares(self):
        print(self.__active_game_board)
    
    def view_board(self):
        print("+ " * 16 )
        for i, row in enumerate(self.__sudoku_game):
            if i == 3 or i == 6:
                print('+'+('-'*9 + '+')*3)
            print( f"|{(' '*9 + '|') * 3 }\n| {'  '.join([str(x)if x != None else '0' for x in row[0:3]] )} | {'  '.join([str(x)if x != None else '0' for x in row[3:6]])} | {'  '.join([str(x)if x != None else '0'  for x in row[6:9]])} |" )
        
        print("+ " * 16 )
        
    def propose_guess(self, square, guess):
        if self.__guess != None:
            self.__guess.append( {
                "square": square,
                "guess" : guess,
                "prev_state": np.copy(self.__sudoku_game),
                "prev_possibilities": self.__get_current_possibilities()
            })
            self.update_game_square(square, guess, isGuess=True)
            return True
        else:
            return False
        
    def __get_current_possibilities(self):
        possibilities = {}
        for square in self.__active_game_board:
            p = self.__active_game_board[square].possibilities 
            v = self.__active_game_board[square].value
            possibilities[square] = v if v != None else set(list(p))
        return possibilities
    def revert_guess(self):
        if self.__guess != None:
            last_guess = self.__guess.pop()
            s = last_guess["square"]
            g = last_guess["guess"]
            state = last_guess["prev_state"]
            possibilities = last_guess["prev_possibilities"]
            if isinstance(possibilities[s], set):
                if g in possibilities[s]:
                    possibilities[s].remove(g)
                    if len(possibilities[s]) == 1:
                        possibilities[s] = list(possibilities[s])[0]
            for r, c in self.__active_game_board:
                if state[r,c] == 0 and isinstance(possibilities[(r,c)], set):
                    self.__active_game_board[(r,c)].update_square(None, possibilities[(r,c)])
                else:
                    self.__active_game_board[(r,c)].update_square(possibilities[(r,c)], None)
            self.__sudoku_game = state
            return True
        else:
            return False
        
    class __Sudoku_Square:
        
        def __init__ (self, row, col, value=None, possibilities=[1,2,3,4,5,6,7,8,9]):
            self.__row = row
            self.__col = col
            self.lock = Lock()
            self.value = value
            self.possibilities = None if value != None else set(possibilities)
        
        def __repr__ (self):
            return f"({self.__row},{self.__col})->[{self.value if self.value != None else ','.join([str(a) for a in self.possibilities])}]"
        
        def get_row(self):
            return self.__row
        
        def get_col(self):
            return self.__col
        
        def update_square(self, value, possibilities):
            self.value = value
            self.possibilities = possibilities
        
        def remove_possibility (self, p):
            if self.possibilities != None:
                if p in self.possibilities:
                    self.possibilities.remove(p)
                    if len(self.possibilities) == 1:
                        self.value = list(self.possibilities)[0]
                        self.possibilities = None
            


      
