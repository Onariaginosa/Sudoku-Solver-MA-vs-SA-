# import math
import sys
# import numpy as np
from sudoku import Sudoku
from Sudoku_Game import Sudoku_Game
sys.path.append("..")
from Agents.Multi_Agent_Sudoku import *
from Agents.Single_Agent_Sudoku import *
  


# Test 1 Board Difficulty of 0.1: 
test_1 = Sudoku(3,3, seed=1001).difficulty(0.6)
test_1.show_full()

game_1 = Sudoku_Game(test_1.board, guessing = True)
sa = Single_Agent_Sudoku(game_1)
# ma = Multi_Agent_Sudoku(game_1)

