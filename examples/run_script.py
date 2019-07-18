# -*- coding: utf-8 -*-
"""
Solve the 'Scramble Squares' class of puzzles.
"""
from scramble_squares_solver import *

tiles = csv2tiles("scsq_wizards.csv")
wizards_game = Game(tiles=tiles)
solution = wizards_game.solve()
print(solution)
