import numpy as np

class Grid:  # Grid

    # Initialization function
    def __init__(self, n, blocked_tiles):
        self.n = n
        self.blocked_tiles = blocked_tiles
        self.grid = np.zeros((n, n))

        for tile in blocked_tiles:
            self.grid[tile] = -1

    def isValid(self, pos):
        x, y = pos
        return 0 <= x < self.n and 0 <= y < self.n and self.grid[x, y] != -1  # Tile is not blocked

    # Get possible actions from a position
    def get_possible_acts(self, pos):
        x, y = pos
        acts = []
        for act, (dx, dy) in {'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1)}.items():
            new_pos = (x + dx, y + dy)
            if self.isValid(new_pos):
                acts.append((act, new_pos))
        return acts

    # Reset the grid
    def reset(self):
        self.grid = np.zeros((self.n, self.n))  # Clear the grid
        for tile in self.blocked_tiles:
            self.grid[tile] = -1
