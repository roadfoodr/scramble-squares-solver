# -*- coding: utf-8 -*-
"""
Test suite for scramble_squares_solver.py
"""
import pytest
import sys

sys.path.append("..")
from scramble_squares_solver import *


@pytest.fixture
def direction_map_2x1():
    return {'e':(1, 0), 'w':(-1, 0)}

@pytest.fixture
def locs_2x1():
    locs = [Loc(coord=(0,0)), Loc(coord=(1,0))]
    locs[0].set_dir('e', locs[1])
    locs[1].set_dir('w', locs[0])
    return locs

### Loc tests ###

def test_loc_coords(locs_2x1):
    locs = locs_2x1
    assert locs[0].coord[0] == 0
    assert locs[0].coord[1] == 0
    assert locs[1].coord[0] == 1
    assert locs[1].coord[1] == 0

def test_loc_get_dest(locs_2x1):
    locs = locs_2x1
    assert locs[0].get_dest('e') == locs[1]
    assert locs[0].get_dest('w') is None
    assert locs[0].get_dest('clockwise') is None
    assert locs[1].get_dest('w') == locs[0]
    assert locs[1].get_dest('e') is None
    assert locs[1].get_dest('clockwise') is None

def test_loc_get_neighbors(locs_2x1):
    locs = locs_2x1
    assert locs[0].get_neighbors() == [locs[1]]
    assert locs[1].get_neighbors() == [locs[0]]

def test_loc_get_neighbor_dirs(locs_2x1):
    locs = locs_2x1
    assert locs[0].get_neighbor_dirs() == ['e']
    assert locs[1].get_neighbor_dirs() == ['w']
