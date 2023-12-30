from typing import List, Tuple, Optional
from collections import Counter

def generate_all_rectangle_sizes() -> List[Tuple[int, int]]:
    """Generate all possible rectangle (and square) sizes within 5x5 dimensions."""
    return [(h, w) for h in range(1, 6) for w in range(1, 6)]

def can_place_rectangle(grid: List[List[int]], start_row: int, start_col: int, length: int, width: int) -> bool:
    """Check if a rectangle of a given size can be placed on the grid at the specified position."""
    if start_row + length > len(grid) or start_col + width > len(grid[0]):
        return False
    for i in range(start_row, start_row + length):
        for j in range(start_col, start_col + width):
            if grid[i][j] != 0:
                return False
    return True

def fill_grid_with_rectangles_and_count_corrected(grid: List[List[int]], rectangle_sizes: List[Tuple[int, int]]) -> Counter:
    """Fill a grid of given dimensions with tiles and count the number and sizes of the tiles used."""
    def place_and_count_rectangle(row: int, col: int, length: int, width: int, rectangle_id: int):
        for i in range(row, row + length):
            for j in range(col, col + width):
                grid[i][j] = rectangle_id
        size_counts[(length, width)] += 1

    size_counts = Counter()

    def backtrack(rectangle_id: int):
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == rectangle_id:
                    grid[i][j] = 0
        last_rectangle = next((size for size, count in size_counts.items() if count == rectangle_id), None)
        if last_rectangle:
            size_counts[last_rectangle] -= 1

    def helper(rectangle_id: int = 1) -> bool:
        if all(all(cell != 0 for cell in row) for row in grid):
            return True

        for length, width in rectangle_sizes:
            for row in range(len(grid) - length + 1):
                for col in range(len(grid[0]) - width + 1):
                    if can_place_rectangle(grid, row, col, length, width):
                        place_and_count_rectangle(row, col, length, width, rectangle_id)
                        if helper(rectangle_id + 1):
                            return True
                        backtrack(rectangle_id)
        return False

    helper()
    return size_counts

def cm_to_mm(cm: int) -> int:
    """Convert centimeters to millimeters."""
    return cm * 10

def mm_to_tiles(mm_length: int, mm_width: int, tile_size_mm: int = 42) -> Tuple[int, int]:
    """Convert millimeter dimensions to grid units."""
    return mm_length // tile_size_mm, mm_width // tile_size_mm

def fill_and_count_tiles_corrected(length_cm: int, width_cm: int, tile_size_mm: int = 42) -> Tuple[Counter, Tuple[int, int]]:
    """Fill a grid with tiles based on cm dimensions and count the number and sizes of the tiles used."""
    length_mm, width_mm = cm_to_mm(length_cm), cm_to_mm(width_cm)
    grid_length, grid_width = mm_to_tiles(length_mm, width_mm, tile_size_mm)
    grid = [[0 for _ in range(grid_width)] for _ in range(grid_length)]
    rectangle_sizes = generate_all_rectangle_sizes()
    rectangle_sizes.sort(key=lambda size: (size[0] * size[1], -(size[0] + size[1])), reverse=True)
    rectangle_counts = fill_grid_with_rectangles_and_count_corrected(grid, rectangle_sizes)
    remaining_length_mm = length_mm % tile_size_mm
    remaining_width_mm = width_mm % tile_size_mm
    return rectangle_counts, (remaining_length_mm, remaining_width_mm)

def format_output(tile_counts: Counter, gaps_mm: Tuple[int, int]) -> str:
    """Format the output for a more human-readable form."""
    output = "Tile Usage Summary:\n"
    for size, count in tile_counts.items():
        output += f"- {count} tiles of size {size[0]}x{size[1]} (each tile {size[0]*42}mm x {size[1]*42}mm)\n"
    output += f"Remaining Gaps: Lengthwise {gaps_mm[0]}mm, Widthwise {gaps_mm[1]}mm"
    return output

# Function to run the script with input in centimeters
def run_script_with_input():
    length_cm = int(input("Enter length in cm: "))
    width_cm = int(input("Enter width in cm: "))
    tile_counts, gaps_mm = fill_and_count_tiles_corrected(length_cm, width_cm)
    print(format_output(tile_counts, gaps_mm))

# Run the script
run_script_with_input()
