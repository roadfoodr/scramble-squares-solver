# scramble-squares-solver
Solver for the 'Scramble Squares' class of puzzles.

### The problem
Scramble Squares are tile-based puzzles marketed by b.dazzle inc.  Each puzzle consists of 9 square tiles, each with half of a symbol on each edge.
The tiles must be arranged in a 3x3 grid so that all touching edges match with corresponding symbol halves.
An example is [here](https://www.amazon.com/Dazzle-Wizard-Dragons-Scramble-Squares/dp/B000BTBDRY).

### The solution space
Since each of 9 tiles may be placed in 9 locations in the 3x3 grid, there are **9!** possibilities for placing tiles.  Within each such assignment of tiles
to locations, each tile may be rotated in 4 directions, for a total of **4^9** possibilities.  Therefore, the size of the entire solution space is
**9! * 4^9**.  

### The algorithm
The solver employs guided depth-first search with backtracking.  A "stack" of candidate solutions is maintained by incrementally extending partial
board configurations with matching tiles.  Once a particular candidate solution can not be extended further, it is removed from the stack
and search resumes starting from the previous configuration that has not been fully explored.  Once a valid configuration that uses all tiles
and/or locations is found, it is returned as the solution.

### Running the solver
The solver is implemented as a collection of Python classes and functions.  Although a variety of game configurations are supported
(square or even hexagonal grids of arbitrary size), the classic 3x3 version with square tiles is defaulted.  So only the tile
specifications (particular symbols on particular tiles) are required.  These objects can be generated from a .csv file:
    
    tiles = csv2tiles("scsq_wizards.csv")
    
Then a Game object instantiated with these tiles:

    wizards_game = Game(tiles=tiles)

The `Game`'s `solve()` method returns a `Board` object with the solution (assignments for each tile's location and rotation):

    solution = wizards_game.solve()
    print(solution)

    Loc (0, 0): Tile 0, rot=1
    Loc (0, 1): Tile 6, rot=0
    Loc (0, 2): Tile 5, rot=3
    Loc (1, 0): Tile 1, rot=2
    Loc (1, 1): Tile 4, rot=3
    Loc (1, 2): Tile 7, rot=3
    Loc (2, 0): Tile 3, rot=0
    Loc (2, 1): Tile 2, rot=1
    Loc (2, 2): Tile 8, rot=3
