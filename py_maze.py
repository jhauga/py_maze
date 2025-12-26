#!/usr/bin/env python3
# py_maze
# A command-line maze game generator and player.

import argparse
import random
import sys
import os

# Platform-specific imports for keyboard input
if sys.platform == 'win32':
    import msvcrt
else:
    import tty
    import termios


class MazeGenerator:
    # generate random, solvable mazes using recursive backtracking

    def __init__(self, width=9, height=11):
        # initialize maze generator
        # args:
        #    width: Number of cells wide (actual width will be width*2+1)
        #    height: Number of cells tall (actual height will be height*2+1)

        self.width = width
        self.height = height

        # create grid with all walls (True = wall, False = path)
        self.grid = [[True for _ in range(width * 2 + 1)] for _ in range(height * 2 + 1)]

    # generate a solvable maze using recursive backtracking algorithm
    def generate(self):
        # start from top-left cell (1, 1)
        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = False

        # stack for backtracking
        stack = [(start_x, start_y)]
        visited = {(start_x, start_y)}

        while stack:
            current_x, current_y = stack[-1]

            # find unvisited neighbors (2 cells away in each direction)
            neighbors = []
            for dx, dy in [(0, -2), (2, 0), (0, 2), (-2, 0)]:  # Up, Right, Down, Left
                nx, ny = current_x + dx, current_y + dy
                if (0 < nx < len(self.grid[0]) and 0 < ny < len(self.grid) and
                    (nx, ny) not in visited):
                    neighbors.append((nx, ny, dx, dy))

            if neighbors:
                # choose random neighbor
                nx, ny, dx, dy = random.choice(neighbors)

                # remove wall between current and neighbor
                wall_x = current_x + dx // 2
                wall_y = current_y + dy // 2
                self.grid[wall_y][wall_x] = False
                self.grid[ny][nx] = False

                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                # backtrack
                stack.pop()

        # create entrance and exit
        self.grid[0][1]   = False  # entrance at top
        self.grid[-1][-2] = False  # exit at bottom

        return self.grid

    def to_string(self):
        # convert maze grid to string representation
        lines = []
        for row in self.grid:
            line = ''.join('*' if cell else ' ' for cell in row)
            lines.append(line)
        return '\n'.join(lines)


# Interactive maze game with player movement.
class MazeGame:
    def __init__(self, maze_grid):
        # initialize the game
        #
        # args:
        #     maze_grid: 2D list representing the maze (True = wall, False = path)

        self.maze = [row[:] for row in maze_grid]  # copy the grid
        self.height = len(self.maze)
        self.width = len(self.maze[0])

        # find starting position (first open space from top)
        self.player_x = 1
        self.player_y = 0
        for y in range(self.height):
            if not self.maze[y][self.player_x]:
                self.player_y = y
                break

        # find end position (last open space at bottom)
        self.end_x = self.width - 2
        self.end_y = self.height - 1
        for y in range(self.height - 1, -1, -1):
            if not self.maze[y][self.end_x]:
                self.end_y = y
                break

    def render(self):
        # render the maze with the player
        self.clear_screen()
        print("start")

        for y in range(self.height):
            line = ''
            for x in range(self.width):
                if x == self.player_x and y == self.player_y:
                    line += 'o'
                elif self.maze[y][x]:
                    line += '*'
                else:
                    line += ' '
            print(line)

        print("end")
        print("\nUse arrow keys or WASD to move. Press 'q' to quit.")

    # clear the terminal screen
    def clear_screen(self):
        os.system('cls' if sys.platform == 'win32' else 'clear')

    def move_player(self, dx, dy):
        # move player by dx, dy if the destination is not a wall
        #
        # Args:
        #     dx: Change in x position
        #     dy: Change in y position
        #
        # Returns:
        #     True if move was successful, False otherwise

        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # check bounds and wall collision
        if (0 <= new_x < self.width and 0 <= new_y < self.height and
            not self.maze[new_y][new_x]):
            self.player_x = new_x
            self.player_y = new_y
            return True
        return False

    # check if player has reached the end
    def check_win(self):
        return self.player_x == self.end_x and self.player_y == self.end_y

    # get a single keypress from user (cross-platform)
    def get_key(self):
        if sys.platform == 'win32':
            # windows
            if msvcrt.kbhit():
                key = msvcrt.getch()
                # handle arrow keys (they come as two bytes)
                if key == b'\xe0':  # arrow key prefix on Windows
                    key = msvcrt.getch()
                    if key == b'H':  # up arrow
                        return 'up'
                    elif key == b'P':  # down arrow
                        return 'down'
                    elif key == b'K':  # left arrow
                        return 'left'
                    elif key == b'M':  # right arrow
                        return 'right'
                return key.decode('utf-8', errors='ignore').lower()
        else:
            # unix/linux/mac
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                # handle arrow keys (they come as escape sequences)
                if key == '\x1b':
                    key += sys.stdin.read(2)
                    if key == '\x1b[A':
                        return 'up'
                    elif key == '\x1b[B':
                        return 'down'
                    elif key == '\x1b[D':
                        return 'left'
                    elif key == '\x1b[C':
                        return 'right'
                return key.lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    # main game loop
    def play(self):
        self.render()

        while True:
            key = self.get_key()

            if key == 'q':
                print("\nThanks for playing!")
                break
            elif key in ['w', 'up']:
                self.move_player(0, -1)
            elif key in ['s', 'down']:
                self.move_player(0, 1)
            elif key in ['a', 'left']:
                self.move_player(-1, 0)
            elif key in ['d', 'right']:
                self.move_player(1, 0)
            else:
                continue

            self.render()

            if self.check_win():
                print("\n🎉 Congratulations! You solved the maze! 🎉")
                print("Press any key to exit...")
                self.get_key()
                break


# Main entry point for py_maze command.
def main():
    print("Generating maze...")

    # use width and height from argument or defaults
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", "-w", type=int, default=9, help="Width of the maze in cells")
    parser.add_argument("--height", "-H", type=int, default=11, help="Height of the maze in cells")
    args = parser.parse_args()
    height = args.height
    width = args.width

    # generate a random maze
    generator = MazeGenerator(width, height)
    maze_grid = generator.generate()

    # display the maze
    print("\nstart")
    print(generator.to_string())
    print("end\n")

    # ask if user wants to play
    print("Would you like to play this maze? (y/n): ", end='', flush=True)

    try:
        if sys.platform == 'win32':
            response = msvcrt.getch().decode('utf-8', errors='ignore').lower()
        else:
            response = sys.stdin.read(1).lower()

        print(response)

        if response == 'y':
            game = MazeGame(maze_grid)
            game.play()
        else:
            print("Goodbye!")
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
