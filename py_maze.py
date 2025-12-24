#!/usr/bin/env python3
"""
py_maze - A command-line maze game generator and player.

Generate random, solvable mazes and navigate through them using keyboard controls.
"""

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
    """Generate random, solvable mazes using recursive backtracking."""
    
    def __init__(self, width=9, height=11):
        """
        Initialize maze generator.
        
        Args:
            width: Number of cells wide (actual width will be width*2+1)
            height: Number of cells tall (actual height will be height*2+1)
        """
        self.width = width
        self.height = height
        # Create grid with all walls (True = wall, False = path)
        self.grid = [[True for _ in range(width * 2 + 1)] for _ in range(height * 2 + 1)]
        
    def generate(self):
        """Generate a solvable maze using recursive backtracking algorithm."""
        # Start from top-left cell (1, 1)
        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = False
        
        # Stack for backtracking
        stack = [(start_x, start_y)]
        visited = {(start_x, start_y)}
        
        while stack:
            current_x, current_y = stack[-1]
            
            # Find unvisited neighbors (2 cells away in each direction)
            neighbors = []
            for dx, dy in [(0, -2), (2, 0), (0, 2), (-2, 0)]:  # Up, Right, Down, Left
                nx, ny = current_x + dx, current_y + dy
                if (0 < nx < len(self.grid[0]) and 0 < ny < len(self.grid) and
                    (nx, ny) not in visited):
                    neighbors.append((nx, ny, dx, dy))
            
            if neighbors:
                # Choose random neighbor
                nx, ny, dx, dy = random.choice(neighbors)
                
                # Remove wall between current and neighbor
                wall_x = current_x + dx // 2
                wall_y = current_y + dy // 2
                self.grid[wall_y][wall_x] = False
                self.grid[ny][nx] = False
                
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                # Backtrack
                stack.pop()
        
        # Create entrance and exit
        self.grid[0][1] = False  # Entrance at top
        self.grid[-1][-2] = False  # Exit at bottom
        
        return self.grid
    
    def to_string(self):
        """Convert maze grid to string representation."""
        lines = []
        for row in self.grid:
            line = ''.join('*' if cell else ' ' for cell in row)
            lines.append(line)
        return '\n'.join(lines)


class MazeGame:
    """Interactive maze game with player movement."""
    
    def __init__(self, maze_grid):
        """
        Initialize the game.
        
        Args:
            maze_grid: 2D list representing the maze (True = wall, False = path)
        """
        self.maze = [row[:] for row in maze_grid]  # Copy the grid
        self.height = len(self.maze)
        self.width = len(self.maze[0])
        
        # Find starting position (first open space from top)
        self.player_x = 1
        self.player_y = 0
        for y in range(self.height):
            if not self.maze[y][self.player_x]:
                self.player_y = y
                break
        
        # Find end position (last open space at bottom)
        self.end_x = self.width - 2
        self.end_y = self.height - 1
        for y in range(self.height - 1, -1, -1):
            if not self.maze[y][self.end_x]:
                self.end_y = y
                break
    
    def render(self):
        """Render the maze with the player."""
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
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if sys.platform == 'win32' else 'clear')
    
    def move_player(self, dx, dy):
        """
        Move player by dx, dy if the destination is not a wall.
        
        Args:
            dx: Change in x position
            dy: Change in y position
        
        Returns:
            True if move was successful, False otherwise
        """
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        
        # Check bounds and wall collision
        if (0 <= new_x < self.width and 0 <= new_y < self.height and
            not self.maze[new_y][new_x]):
            self.player_x = new_x
            self.player_y = new_y
            return True
        return False
    
    def check_win(self):
        """Check if player has reached the end."""
        return self.player_x == self.end_x and self.player_y == self.end_y
    
    def get_key(self):
        """Get a single keypress from user (cross-platform)."""
        if sys.platform == 'win32':
            # Windows
            if msvcrt.kbhit():
                key = msvcrt.getch()
                # Handle arrow keys (they come as two bytes)
                if key == b'\xe0':  # Arrow key prefix on Windows
                    key = msvcrt.getch()
                    if key == b'H':  # Up arrow
                        return 'up'
                    elif key == b'P':  # Down arrow
                        return 'down'
                    elif key == b'K':  # Left arrow
                        return 'left'
                    elif key == b'M':  # Right arrow
                        return 'right'
                return key.decode('utf-8', errors='ignore').lower()
        else:
            # Unix/Linux/Mac
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                # Handle arrow keys (they come as escape sequences)
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
    
    def play(self):
        """Main game loop."""
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


def main():
    """Main entry point for py_maze command."""
    print("Generating maze...")
    
    # Generate a random maze
    generator = MazeGenerator(width=9, height=11)
    maze_grid = generator.generate()
    
    # Display the maze
    print("\nstart")
    print(generator.to_string())
    print("end\n")
    
    # Ask if user wants to play
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
