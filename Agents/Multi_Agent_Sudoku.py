import random
import time
from threading import Thread

class Multi_Agent_Sudoku:
    class Group_Agent:
        def __init__(self, group_num, sudoku_game):
            self.game = sudoku_game
            self.group = sudoku_game.get_sudoku_group(group_num)
            self.id = group_num
            self.seen = set()
            self.__status = "In Progress"
            self.__unknown = set(sudoku_game.get_sudoku_group(group_num))
            self.__active = True
            self.__thread = Thread(target=self.__solve_group, args=()).start()
        
        def __solve_group(self):
            self.__status = "In Progress"
            while len(self.__unknown) > 0 and self.game.valid_sudoku_game() and self.__active:
                self.__status = "In Progress"
                trash = set()
                for square in self.__unknown:
                    s = self.game.view_sudoku_square(square)
                    if isinstance(s, set):
                        s = list(s)
                        for p in s:
                            if p in self.seen:
                                self.game.update_game_square(square, p)
                    elif s not in self.seen:
                        self.seen.add(s)
                        trash.add(square)
                if len(trash) > 0:
                    self.__unknown = self.__unknown - trash
                else: 
                    self.__status = "Guessing"
            if len(self.__unknown) == 0:
                self.__status = "Complete"
            else: 
                self.status = "Invalid"
        
        def getStatus(self):
            return self.__status
        
        def kill(self):
            self.__active = False
        
        def reset(self):
            self.__active = True
            self.__thread = Thread(target=self.__solve_group, args=()).start()
        
        def getGuess(self):
            s_guess, s_guess_val, probability = None, None, -1
            for square in self.__unknown:
                s = self.game.view_sudoku_square(square)
                if isinstance(s, set):
                    p = 1.0 / len(s)
                    if probability < p:
                        probability = p
                        s_guess = square
                        s_guess_val = random.choice(list(s))
            return s_guess, s_guess_val, probability
    
    def __init__(self, sudoku_game):
        self.__start = time.perf_counter()
        self.__game = sudoku_game
        self.__agents = [self.Group_Agent(a, sudoku_game)  for a in range(27)]
        self.__completed = set()
        self.__guessBoard = self.__getGuessBoard()
        self.__guessing = lambda : self.__game.is_guessing()
        self.__status = "Solving"
        self.__solveSudoku()
    
    def __solveSudoku(self):
        
        guess_count = 0
        while self.__status == "Solving":
            if not self.__game.valid_sudoku_game(): 
                if self.__guessing():
                    self.__kill_agents()
                    self.__game.revert_guess()
                    self.__wakeup_agents()
                else:
                    self.__status = "unSolvable"
            else:
                guessBoard = self.__getGuessBoard()
                if len(guessBoard) == 0:
                    self.__status="Complete"
                elif sum(guessBoard) == len(guessBoard):
                    square, best_guess = self.__getBestGuess()
                    if square == None or best_guess == None:
                        if self.__guessing():
                            self.__kill_agents()
                            self.__game.revert_guess()
                            self.__wakeup_agents()
                        else:
                            self.__status = "unSolvable"
                    else:
                        guess_count += 1
                        self.__game.propose_guess(square, best_guess)
        end = time.perf_counter()
        print(f"Multi-Agent Stats:\n\nTime taken: {end - self.__start}\nFinal Status: {self.__status}\nNumber of Guesses: {guess_count}\nBoard:")
        self.__game.view_board()
    
    def __getBestGuess(self):
        guesses = [(a.getGuess()) for a in self.__agents]
        guesses = filter(lambda g : g[2] > 0 and g[1] != None and g[0] != None, guesses ) 
        guesses = (sorted(guesses, key = lambda x: -x[2]))
        return guesses[0][0], guesses[0][1]
    
    def getStatus(self):
        print(self.__status)
    
    def __wakeup_agents(self):
        for a in self.__agents:
            a.reset()
    
    def __kill_agents(self):
        for a in self.__agents:
            a.kill()
    
    def __getGuessBoard (self):
        board = [0 if a.getStatus() == "In Progress" else (None if a.getStatus() == "Complete" else 1) for a in self.__agents]
        return [i for i in board if i is not None]

