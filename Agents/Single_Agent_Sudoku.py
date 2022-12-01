import random
import time
from threading import Thread

class Single_Agent_Sudoku:
    def __init__(self, sudoku_game):
        self.__start = time.perf_counter()
        self.game = sudoku_game
        self.__status = "In Progress"
        self.__guessing = lambda : self.game.is_guessing()
        self.__thread = Thread(target=self.__solve, args=()).start()
        
    def __solve(self):
        self.__groups = {}
        self.__group_status = {}
        guess_count = 0
        for group_num in range(27):
            self.__groups[group_num] = self.game.get_sudoku_group(group_num)
            self.__group_status[group_num] = "In Progress"
        while self.__status == "In Progress":
            for group_id in self.__groups:
                self.__group_status[group_id] = self.__filter_group(group_id)
            # invalid_groups = dict(filter(lambda x: x[1] == "Invalid", self.__group_status.items()))
            guessing_groups = dict(filter(lambda x: x[1] == "Guessing", self.__group_status.items()))
            complete_groups = dict(filter(lambda x: x[1] == "Complete", self.__group_status.items()))
            
            if not self.game.valid_sudoku_game():
                if self.__guessing():
                    self.game.revert_guess()
                else:
                    self.__status = "unSolvable"
            else:
                if len(complete_groups) == len(self.__group_status):
                    self.__status = "Complete"
                    
                elif len(guessing_groups) ==  len(self.__group_status) - len(complete_groups):
                        square, best_guess = self.__getBestGuess()
                        if square == None or best_guess == None:
                            if self.__guessing():
                                self.game.revert_guess()
                            else:
                                self.__status = "unSolvable"
                        else:
                            guess_count += 1
                            self.game.propose_guess(square, best_guess)  
        end = time.perf_counter()
        print(f"Single-Agent Stats:\n\nTime taken: {end - self.__start}\nFinal Status: {self.__status}\nNumber of Guesses: {guess_count}\nBoard:")
        self.game.view_board()
        
    def __getBestGuess(self):
        guesses = [(self.__getGuess(g)) for g in self.__groups if self.__group_status[g] == "Guessing"]
        guesses = (sorted(guesses, key = lambda x: x[2]))
        return guesses[0][0], guesses[0][1]
    
    def __getGuess(self, id):
        group = self.__groups[id]
        unknown = set([a for a in group if isinstance(self.game.view_sudoku_square(a), set)])
        s_guess, s_guess_val, probability = None, None, -1
        for square in unknown:
            s = self.game.view_sudoku_square(square)
            if isinstance(s, set):
                p = 1.0 / len(s)
                if probability < p:
                    probability = p
                    s_guess = square
                    s_guess_val = random.choice(list(s))
        return s_guess, s_guess_val, probability

    def __filter_group(self, id):
        group = self.__groups[id]
        trash = set()
        unknown = set([a for a in group if isinstance(self.game.view_sudoku_square(a), set)])
        seen = set([self.game.view_sudoku_square(a) for a in group if not isinstance(self.game.view_sudoku_square(a), set)])
        for square in unknown:
            s = list(self.game.view_sudoku_square(square))
            for p in s:
                if p in seen:
                    self.game.update_game_square(square, p)
            if not isinstance(self.game.view_sudoku_square(square), set):
                if self.game.view_sudoku_square(square) in seen:
                    # Contradiction, Duplicate in group
                    return "Invalid"
                else:
                    seen.add(self.game.view_sudoku_square(square))
                    trash.add(square)
        if len(trash) > 0:
            unknown = unknown - trash
        elif len(unknown) == 0:
            return "Complete"
        elif len(trash) == 0: 
            return "Guessing"
        else:
            return "In Progress"