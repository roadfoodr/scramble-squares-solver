# -*- coding: utf-8 -*-
"""
Solve the 'Scramble Squares' class of puzzles.
"""

import itertools
from dataclasses import dataclass
from collections import Counter
import random


@dataclass
class Globals:
    USE_RARES: bool = True
    MEMOIZE: bool = True
    FIRST_ONLY: bool = True
    LOG_FREQUENCY: int = 2500
    DETERMINISTIC: bool = True


class Loc:
    """
    A single location in a Layout.  Attributes are a coordinate (2-d tuple)
    and a dict of direction names, each of which will be mapped to a 
    destination (neighbor) Loc.
    """
    def __init__(self, coord=None):
        self.direction_map = {}
        self.coord = (None, None) if coord is None else coord

    def set_dir(self, direction, dest=None):
        """ Set the neighboring Loc that corresponds to the specified direction. """
        self.direction_map[direction] = dest

    def get_dest(self, direction):
        """ Get the neighboring Loc that corresponds to the specified direction. """
        return self.direction_map[direction]
    
    def get_neighbors(self):
        return [self.direction_map[direction] 
                for direction, _ in self.direction_map.items() 
                if self.direction_map.get(direction, None)]

    def get_neighbor_dirs(self):
        return [direction for direction in self.direction_map.keys() 
                if self.direction_map.get(direction, None)]

    def __str__(self):
        return f'Loc {self.coord}'

    def __repr__(self):
        return f'Loc {self.coord} ({len(self.get_neighbors())} neighbors)'


class Layout:
    """
    Creates a dict of Locs corresponding to the coordinates of this Layout.
    Initializes each Loc with its neighboring Locs corresponding to each of
    the directions in the layout.  Defaults to a 3x3 grid of square locs
    (with neighbors in n, s, e, w directions).
    """
    def __init__(self, coords=None, direction_map=None, direction_pairs=None):
        self.loc_dict = {}

        if coords is None:
            self.coords = [(i, j) for j in range(3) for i in range(3)]
        else:
            self.coords = coords
        for coord in self.coords:
            self.loc_dict[coord] = Loc(coord)

        if direction_map is None:
            self.direction_map = {
                    'n':(0, -1), 's':(0, 1), 'e':(1, 0), 'w':(-1, 0)
                    }
        else:
            self.direction_map = direction_map

        if direction_pairs is None:
            self.direction_pairs = {'n':'s', 's':'n', 'e':'w', 'w':'e'}
        else:
            self.direction_pairs = direction_pairs

        self.inner_edges = 0
        for loc in self.locs:
            for direction, this_coord in self.direction_map.items():
                try_coord = (loc.coord[0] + this_coord[0],
                             loc.coord[1] + this_coord[1])
                dest = (self.loc_dict[try_coord] if try_coord in self.coords
                        else None)
                loc.set_dir(direction, dest)
                self.inner_edges += 1 if dest else 0

    @property
    def locs(self):
        return self.loc_dict.values()

    def get_paired_dir(self, dir):
        return self.direction_pairs.get(dir, None)

    def __repr__(self):
        return (f'Layout ({len(self.coords)} coords, '
                f'{len(self.direction_map)} directions)')


class Symbol:
    """Class to represent attributes of each symbol contained on a Piece."""
    _rare_dict = {}

    def __init__(self, sym_type, side, rare=False):
        self.sym_type = sym_type
        self.side = side
        self._sym = (sym_type, side)
        self.rare = rare

    @property
    def rare(self):
        return Symbol._rare_dict.get(self._sym, None)

    @rare.setter
    def rare(self, rare):
        Symbol._rare_dict[self._sym] = rare

    def __eq__(self, other):
        return self._sym == other._sym

    def __hash__(self):
        return hash(self._sym)

    def __repr__(self):
        return f'({self.sym_type}|{self.side})'


class Piece:
    """
    Contains assignments of symbols to "canonical" directions (rotation 0).
    Helper queries return symbol / dir assignments for other possible rotations.
    directions is a list that must be in sequential order of rotations.
    symbols is a list that must be in order corresponding to directions.
    """
    id_gen = itertools.count()

    def __init__(self, piece_id=None, directions=None, symbols=None):
        self.piece_id = next(self.id_gen) if piece_id is None else piece_id
        self.directions = (['n', 'e', 's', 'w'] if directions is None 
                           else directions)
        self.symbols = ([None for d in self.directions] if symbols is None 
                        else symbols)

    def get_dir(self, symbol, rotation=0):
        """Get the direction corresponding to the given symbol and rotation."""
        idx = self.symbols.index(symbol)
        return self.directions[(idx + rotation) % len(self.symbols)]

    def get_symbol(self, direction, rotation=0):
        """Get the symbol corresponding to the given direction and rotation."""
        idx = self.directions.index(direction)
        return self.symbols[(idx - rotation) % len(self.directions)]

    def get_rotations(self, symbol, dir):
        """
        Returns a list of rotations (since a Piece can contain more
        than one instance of a symbol) that would be required to place
        each matching symbol into the specified direction.
        """
        d = self.directions.index(dir)
        return [(d - i) % len(self.directions)
                for i, s in enumerate(self.symbols)
                if s == symbol]

    def set_symbol(self, symbol, direction=None):
        if direction:
            idx = self.directions.index(direction)
            self.symbols[idx] = symbol
        else:
            self.symbols.append(symbol)

    def __lt__(self, other):
        return self.piece_id < other.piece_id

    def __str__(self):
        return f'Piece {self.piece_id}'

    def __repr__(self):
        symlist = ", ".join([f'{direction}: {self.symbols[i]}'
                             for i, direction in enumerate(self.directions)])
        return f'Piece {self.piece_id} ({symlist})'


@dataclass(unsafe_hash=True)
class Assignment:
    """
    Class to represent an assignment of a specific Piece with specific
    rotation to a specific Loc.
    """
    loc: Loc
    piece: Piece
    rotation: int
    validated: bool = False

    def __repr__(self):
        return (f'Assignment ({self.loc} | {self.piece} | '
                f'rot={self.rotation} | {self.validated})'
                )


class Board:
    """
    Class to represent a possible board configuration as a list of
    Assignments.  A validated Board is one in which all Assignments are
    consistent with each other (piece symbols match across edges).
    A solved Board is a validated Board that includes either all of the Locs
    or all of the Pieces in a Game (none remain available to be assigned).
    """
    def __init__(self, game=None, assignments=None):
        self.game = game
        self.assignments = [] if not assignments else assignments

    def validate(self):
        for assignment in self.assignments:
            if assignment.validated:
                continue
            # look at each direction of this assignment's piece
            piece = assignment.piece
            for direction in piece.directions:
                sym = piece.get_symbol(direction, assignment.rotation)
                # find the layout loc associated with the current direction
                destloc = assignment.loc.get_dest(direction)
                # rare symbols may not match an "edge" with no associated loc
                if not destloc:
                    if Globals.USE_RARES and sym.rare:
                        return False
                    else:
                        continue
                # find the assignment that is associated with the dest loc
                destassign = next((da for da in self.assignments
                                   if da.loc == destloc), None)
                if not destassign:
                    continue
                # find the symbol in the reciprocal dir of the dest assignment
                otherdir = self.game.layout.get_paired_dir(direction)
                otherpiece = destassign.piece
                othersym = otherpiece.get_symbol(otherdir, destassign.rotation)
                # is the reciprocal sym the matching pair to the current sym?
                if self.game.sympairs.get(sym, None) != othersym:
                    return False
            assignment.validated = True
        return True

    def check_solved(self):
        for assignment in self.assignments:
            if not assignment.validated:
                return False
        if (len(self.assignments) == len(self.game.pieces) or
            len(self.assignments) == len(self.game.layout.locs)):
            return True
        else:
            return False

    def extend_board(self):
        """
        Construct a list of next board candidates by finding all Assignment  
        dirs that point to an open Loc, then finding all matching Pieces that 
        would fit that Assigment.
        """
        next_boards = []
        if Globals.DETERMINISTIC:
            unassigned_pieces = list(set(self.game.pieces) -
                                 {a.piece for a in self.assignments})
            unassigned_pieces.sort()
        else:
            unassigned_pieces = (set(self.game.pieces) -
                                 {a.piece for a in self.assignments})

        for assignment in self.assignments:
            if not assignment.validated:
                raise ValueError(
                        "Can only extend a Board that is fully validated.")
            piece = assignment.piece
            # look at each direction of this assignment's piece
            for direction in piece.directions:
                # find the layout loc associated with the current direction
                destloc = assignment.loc.get_dest(direction)
                if not destloc:
                    continue
                # is there an assignment already associated with the dest loc?
                destassign = next((da for da in self.assignments 
                                   if da.loc == destloc), None)
                if destassign:
                    continue
                # which reciprocal dir and sym match the current dir and sym?
                sym = piece.get_symbol(direction, assignment.rotation)
                otherdir = self.game.layout.get_paired_dir(direction)
                othersym = self.game.sympairs.get(sym, None)
                if not othersym:
                    continue
                for otherpiece in unassigned_pieces:
                    rots = otherpiece.get_rotations(othersym, otherdir)
                    for rot in rots:
                        newassign = Assignment(loc=destloc, piece=otherpiece,
                                               rotation=rot, validated=False)
                        next_boards.append(Board(self.game,
                                                 self.assignments+[newassign]))
        return next_boards

    def memoize(self):
        self.game.boards_visited.add(frozenset(self.assignments))

    def check_memo(self):
        return frozenset(self.assignments) in self.game.boards_visited

    def __str__(self):
        asgns = sorted(self.assignments, key=lambda a:a.loc.coord[1])
        strs = [f'{a.loc.__str__()}: {a.piece.__str__()}, '
                f'rot={a.rotation}' for a in asgns]
        strs.sort()
        return '\n'.join(strs)

    def __repr__(self):
        return self.assignments.__repr__()


class Game:
    """
    Class to track the state of a Game (Layout, Pieces, Board candidate stack
    for solution in progress.)
    """
    def __init__(self, layout=None, pieces=None):
        self.layout = Layout() if not layout else layout
        if not pieces:
            raise ValueError('Pieces must be supplied at Game initialization.')
        else:
            self.pieces = pieces
        self._symlist = list(
                itertools.chain.from_iterable(p.symbols for p in self.pieces))
        self._symfreq = Counter(self._symlist)
        self.symbols = set(self._symlist)
        self.boards_visited = set()
        self.stack = []

        if Globals.USE_RARES:
            for sym in self.symbols:
                if self._symfreq[sym] <= (self.layout.inner_edges
                                / len(self.symbols)):
                    sym.rare = True

        self.symsides = set(sym.side for sym in self.symbols)
        if len(self.symsides) != 2:
            raise ValueError(
                    f'There should be exactly two types of symbol sides. '
                    f'(e.g. "top" and "bottom").')
        self.sympairs = {}
        for sym in self.symbols:
            otherside = next(
                    (pair for pair in self.symbols
                     if sym.sym_type == pair.sym_type and sym.side != pair.side)
                    , None)
            if otherside:
                self.sympairs[sym] = otherside

    def solve(self):
        """Solve the game and return one or more Boards with valid solutions."""
        def print_update():
            print(f'solution_length: {len(board.assignments)}, '
                  f'trials: {trials}, valid_trials: {valid_trials}, '
                  f'stack depth = {len(self.stack)}')
            print(f'boards visited: {len(self.boards_visited)}, '
                  f'revisits: {revisits}')

        trials, valid_trials, revisits = 0,0,0
        if not Globals.FIRST_ONLY:
            boards = []

        # Initialize the stack by placing all possible piece rotations
        # onto one initial location.
        if Globals.DETERMINISTIC:
            loc = next(iter(self.layout.locs))
        else:
            loc = random.choice(list(self.layout.locs))
        for piece in self.pieces:
            for rotation, _ in enumerate(piece.directions):
                assignment = Assignment(loc=loc, piece=piece, 
                               rotation=rotation, validated=False)
                board = Board(self, [assignment])
                self.stack.insert(0, board)
        if not Globals.DETERMINISTIC:
            random.shuffle(self.stack)

        while self.stack:
            board = self.stack.pop()
            trials += 1
            if trials % Globals.LOG_FREQUENCY == 0:
                print_update()
            if not board.validate():
                continue
            valid_trials += 1
            if Globals.MEMOIZE:
                if board.check_memo():
                    revisits += 1
                    continue
                else:
                    board.memoize()
            if board.check_solved():
                print_update()
                if Globals.FIRST_ONLY:
                    return board
                else:
                    boards.append(board)
            for new_board in board.extend_board():
                self.stack.append(new_board)
        print_update()
        if Globals.FIRST_ONLY:
            return board
        else:
            return boards


def csv2pcs(filename):
    '''
    Convert a csv file into a list of Pieces. The CSV file should have
    a header row with "ID" followed by the names of each direction in
    clockwise order (e.g. "ID,north,east,south,west"), then a row for
    each piece denoting the piece ID and a description of the symbol that 
    lies in each direction.  The symbol description is two parts with
    a "/" separator: first the name of the symbol, then the name of the symbol's
    side. (e.g. "green clover/left", "orange star/right", "yellow moon/left").
    '''
    import pandas
    df = pandas.read_csv(filename)
    pieces = []
    for _, row in df.iterrows():
        symbol_row = list(row[1:5])
        symbols = []
        for symbol_string in symbol_row:
            sym_type, _, sym_side = symbol_string.partition('/')
            symbols.append(Symbol(sym_type=sym_type, side=sym_side))
        new_piece = Piece(piece_id=row[0],
                  symbols=symbols)
        pieces.append(new_piece)
    return pieces
