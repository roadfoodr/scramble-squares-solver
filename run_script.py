# -*- coding: utf-8 -*-
"""
Solve the 'Scramble Squares' class of puzzles.
"""
from scramble_squares_solver import *

pcs = csv2pcs("examples/scsq_wizards.csv")
wizards_game = Game(pieces=pcs)
solution = wizards_game.solve()
print(solution)
