"""
constructive.py
Optimized constructive algorithms for Magic Squares (O(n^2)):
- Siamese (de la Loubère) method for odd orders (n % 2 != 0)
- Diagonal/Complement method for doubly even orders (n % 4 == 0)
- Strachey's method for singly even orders (n % 4 == 2)
"""


def solve_siamese(n: int):
    """
    Constructs an odd-order magic square using the Siamese (de la Loubère) method.
    Yields (r, c, val, explanation) for step-by-step simulation.
    """
    grid = [[0] * n for _ in range(n)]
    steps = []

    r = 0
    c = n // 2

    for val in range(1, n * n + 1):
        grid[r][c] = val
        steps.append((r, c, val, f"Placed {val} at row {r}, col {c}"))

        # Calculate next position: up 1, right 1
        next_r = (r - 1) % n
        next_c = (c + 1) % n

        if grid[next_r][next_c] != 0:
            # Cell occupied: move down one from current position
            r = (r + 1) % n
        else:
            r = next_r
            c = next_c

    return grid, steps


def solve_doubly_even(n: int):
    """
    Constructs a doubly even magic square (n % 4 == 0) using diagonal/complement inversion.
    Cells along the main 4x4 diagonals retain their original index; others get n^2 + 1 - k.
    """
    grid = [[0] * n for _ in range(n)]
    steps = []
    total_cells = n * n

    count = 1
    for r in range(n):
        for c in range(n):
            # Check if cell lies on the diagonals of a 4x4 sub-block
            in_diag = (r % 4 == c % 4) or ((r % 4 + c % 4) == 3)
            val = count if in_diag else (total_cells + 1 - count)
            grid[r][c] = val
            explanation = (
                f"Diagonal cell: kept {val}" if in_diag
                else f"Complement cell: replaced with {val} ({total_cells + 1} - {count})"
            )
            steps.append((r, c, val, explanation))
            count += 1

    return grid, steps


def solve_singly_even(n: int):
    """
    Constructs a singly even magic square (n % 4 == 2) using Strachey's method.
    Splits into 4 sub-squares of size k = n // 2 (A, B, C, D) and swaps specific columns.
    """
    grid = [[0] * n for _ in range(n)]
    steps = []
    k = n // 2

    # 1. Generate base odd square of size k
    sub_grid, _ = solve_siamese(k)
    shift = k * k

    # Fill sub-grids:
    # Top-Left: A (1 to k^2)
    # Bottom-Right: B (k^2 + 1 to 2k^2)
    # Top-Right: C (2k^2 + 1 to 3k^2)
    # Bottom-Left: D (3k^2 + 1 to 4k^2)
    for r in range(k):
        for c in range(k):
            val_a = sub_grid[r][c]
            val_b = val_a + shift
            val_c = val_a + 2 * shift
            val_d = val_a + 3 * shift

            grid[r][c] = val_a
            grid[r + k][c + k] = val_b
            grid[r][c + k] = val_c
            grid[r + k][c] = val_d

    # 2. Strachey exchange rules
    p = (n - 2) // 4  # Number of columns to swap

    # Left column swaps between A and D
    for r in range(k):
        for c in range(p):
            # Middle row shifts one column to the right
            target_col = c if r != k // 2 else c + 1
            grid[r][target_col], grid[r + k][target_col] = (
                grid[r + k][target_col],
                grid[r][target_col],
            )

    # Right column swaps between C and B
    for r in range(k):
        for c in range(n - p + 1, n):
            grid[r][c], grid[r + k][c] = grid[r + k][c], grid[r][c]

    # Flatten steps for animation
    for r in range(n):
        for c in range(n):
            steps.append((r, c, grid[r][c], f"Filled row {r}, col {c} with {grid[r][c]}"))

    return grid, steps


def get_constructive_solution(n: int):
    """Router returning (grid, steps, case_name, algorithm_description)."""
    if n % 2 != 0:
        case = "Odd Order"
        algo_desc = (
            "Siamese (de la Loubère) Method:\n"
            "1. Start at top row, middle column with number 1.\n"
            "2. Move up 1 row, right 1 column (wrap around edges).\n"
            "3. If destination cell is filled or out-of-corner, move directly down 1 row instead.\n"
            "4. Repeat until all n² cells are filled."
        )
        grid, steps = solve_siamese(n)
    elif n % 4 == 0:
        case = "Doubly Even Order (n mod 4 = 0)"
        algo_desc = (
            "Diagonal / Complement Method:\n"
            "1. Subdivide grid into 4x4 blocks.\n"
            "2. Count sequentially from 1 to n².\n"
            "3. If cell is on the diagonal of its 4x4 block, keep sequential value.\n"
            "4. Otherwise, replace value with complement: (n² + 1) - count."
        )
        grid, steps = solve_doubly_even(n)
    else:
        case = "Singly Even Order (n mod 4 = 2)"
        algo_desc = (
            "Strachey's Method:\n"
            "1. Subdivide grid into 4 sub-quadrants of size k = n/2: A(TL), B(BR), C(TR), D(BL).\n"
            "2. Solve quadrant A using Siamese method; add multiples of k² to B, C, and D.\n"
            "3. Swap specific columns between quadrant A and D, and quadrant C and B.\n"
            "4. Preserves row, column, and diagonal magic constant balances."
        )
        grid, steps = solve_singly_even(n)

    return grid, steps, case, algo_desc