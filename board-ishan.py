import pygame
from sudoku_generator import SudokuGenerator

class Cell:
    def __init__(self, value, row, col, screen, cell_size=60, editable=False):
        self.value = value
        self.sketched_value = 0
        self.row = row
        self.col = col
        self.screen = screen
        self.cell_size = cell_size
        self.selected = False
        self.editable = editable
    def set_cell_value(self, value):
        if self.editable:
            self.value = value
    def set_sketched_value(self, value):
        if self.editable:
            self.sketched_value = value
    def draw(self):
        x = self.col * self.cell_size
        y = self.row * self.cell_size

        pygame.draw.rect(
            self.screen,
            (225, 236, 248),
            pygame.Rect(x, y, self.cell_size, self.cell_size),
        )

        if self.value != 0:
            font = pygame.font.SysFont("arial", 32, bold=True)
            color = (20, 20, 20) if not self.editable else (25, 85, 170)
            text_surf = font.render(str(self.value), True, color)
            text_rect = text_surf.get_rect(
                center=(x + self.cell_size // 2, y + self.cell_size // 2)
            )
            self.screen.blit(text_surf, text_rect)

        elif self.sketched_value != 0:
            sketch_font = pygame.font.SysFont("arial", 18, bold=True)
            sketch_surf = sketch_font.render(
                str(self.sketched_value), True, (115, 115, 115)
            )
            self.screen.blit(sketch_surf, (x + 6, y + 4))

        if self.selected:
            pygame.draw.rect(
                self.screen,
                (220, 40, 40),
                pygame.Rect(x, y, self.cell_size, self.cell_size),
                3,
            )

class Board:
    """Represents the entire 9x9 Sudoku board made of 81 Cell objects."""

    def __init__(self, width, height, screen, difficulty):
        self.width = width
        self.height = height
        self.screen = screen
        self.difficulty = difficulty
        self.rows = 9
        self.cols = 9
        self.cell_size = width // 9
        self.selected_cell = None

        difficulty_map = {"easy": 30, "medium": 40, "hard": 50}
        removed_cells = difficulty_map.get(difficulty.lower(), 30)

        # Generate solved board first, copy it, then remove cells for the puzzle
        gen = SudokuGenerator(9, removed_cells)
        gen.fill_values()

        self.solution = []
        solved_grid = gen.get_board()
        for r in range(self.rows):
            sol_row = []
            for c in range(self.cols):
                sol_row.append(solved_grid[r][c])
            self.solution.append(sol_row)

        gen.remove_cells()
        puzzle_grid = gen.get_board()

        self.cells = []
        self.original_values = []
        for r in range(self.rows):
            cell_row = []
            orig_row = []
            for c in range(self.cols):
                val = puzzle_grid[r][c]
                can_edit = (val == 0)
                cell = Cell(val, r, c, screen, self.cell_size, editable=can_edit)
                cell_row.append(cell)
                orig_row.append(val)
            self.cells.append(cell_row)
            self.original_values.append(orig_row)

        self.board = []
        self.update_board()

    def draw(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c].draw()

        # Draw grid lines with bold borders every 3 rows/columns
        for i in range(self.rows + 1):
            thickness = 3 if i % 3 == 0 else 1
            pos = i * self.cell_size
            pygame.draw.line(self.screen, (0, 0, 0), (0, pos), (self.width, pos), thickness)
            pygame.draw.line(self.screen, (0, 0, 0), (pos, 0), (pos, self.height), thickness)

    def select(self, row, col):
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c].selected = False
        self.cells[row][col].selected = True
        self.selected_cell = (row, col)

    def click(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            col = int(x // self.cell_size)
            row = int(y // self.cell_size)
            return row, col
        return None

    def clear(self):
        if self.selected_cell is not None:
            r, c = self.selected_cell
            cell = self.cells[r][c]
            if cell.editable:
                cell.set_cell_value(0)
                cell.set_sketched_value(0)
                self.update_board()

    def sketch(self, value):
        if self.selected_cell is not None:
            r, c = self.selected_cell
            cell = self.cells[r][c]
            if cell.editable and cell.value == 0:
                cell.set_sketched_value(value)

    def place_number(self, value):
        if self.selected_cell is not None:
            r, c = self.selected_cell
            cell = self.cells[r][c]
            if cell.editable:
                cell.set_cell_value(value)
                cell.set_sketched_value(0)
                self.update_board()

    def reset_to_original(self):
        for r in range(self.rows):
            for c in range(self.cols):
                orig = self.original_values[r][c]
                self.cells[r][c].value = orig
                self.cells[r][c].sketched_value = 0
        self.update_board()

    def is_full(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].value == 0:
                    return False
        return True

    def update_board(self):
        self.board = []
        for r in range(self.rows):
            row_list = []
            for c in range(self.cols):
                row_list.append(self.cells[r][c].value)
            self.board.append(row_list)

    def find_empty(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].value == 0:
                    return r, c
        return None

    def check_board(self):
        self.update_board()
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] != self.solution[r][c]:
                    return False
        return True


