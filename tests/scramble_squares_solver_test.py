# -*- coding: utf-8 -*-
"""
Test suite for scramble_squares_solver.py
"""
import pytest
import sys

sys.path.append("..")
from scramble_squares_solver import *


### Loc tests ###

@pytest.fixture
def locs_2x1():
    locs = [Loc(coord=(0,0)), Loc(coord=(1,0))]
    locs[0].set_dir('e', locs[1])
    locs[1].set_dir('w', locs[0])
    return locs

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


### Layout tests ###

@pytest.fixture
def direction_map_2x1():
    return {'e':(1, 0), 'w':(-1, 0)}

@pytest.fixture
def layout_2x1(locs_2x1, direction_map_2x1):
    return Layout((locs_2x1[0].coord, locs_2x1[1].coord),
                  direction_map_2x1)

@pytest.fixture
def direction_map_2x2_diag():
    return {'nw':(-1.41421, 1.41421), 'ne':(1.41421, 1.41421),
            'se':(1.41421, -1.41421), 'sw':(-1.41421, -1.41421)}

@pytest.fixture
def coords_2x2_diag():
    return ((0,0), (-1.41421, -1.41421), 
             (1.41421, -1.41421), (0, -2.82842))

@pytest.fixture
def layout_2x2_diag(coords_2x2_diag, direction_map_2x2_diag):
    return Layout(coords=coords_2x2_diag, direction_map=direction_map_2x2_diag)

@pytest.fixture
def layout_default():
    return Layout()

def test_layout_locs(layout_2x1, layout_2x2_diag, layout_default):
    locs = list(layout_2x1.locs)
    assert len(locs) == 2
    assert locs[0].get_neighbors() == [locs[1]]
    assert locs[1].get_neighbors() == [locs[0]]

    locs = list(layout_2x2_diag.locs)
    assert len(locs) == 4
    assert all([len(loc.get_neighbors()) == 2 for loc in locs])

    locs = sorted(list(layout_default.locs), key=lambda loc:loc.coord)
    assert len(locs) == 9
    assert set(locs[0].get_neighbors()) == set((locs[1], locs[3]))
    assert set(locs[8].get_neighbors()) == set((locs[5], locs[7]))
    # for a default 3x3 layout, there is only one "middle" piece with 4 neighbors
    assert len([loc for loc in locs if len(loc.get_neighbors()) == 4]) == 1

def test_inner_edges(layout_2x1, layout_2x2_diag, layout_default):
    assert layout_2x1.inner_edges == 2
    assert layout_2x2_diag.inner_edges == 8
    assert layout_default.inner_edges == 24
    
def test_layout_get_paired_dir(layout_2x1, layout_2x2_diag, layout_default):
    assert layout_2x1.get_paired_dir('e') == 'w'
    assert layout_2x1.get_paired_dir('w') == 'e'
    assert layout_2x1.get_paired_dir('n') is None
    assert layout_2x2_diag.get_paired_dir('ne') == 'sw'
    assert layout_2x2_diag.get_paired_dir('nw') == 'se'
    assert layout_2x2_diag.get_paired_dir('n') is None
    assert layout_default.get_paired_dir('n') == 's'
    assert layout_default.get_paired_dir('s') == 'n'
    assert layout_default.get_paired_dir('clockwise') is None


