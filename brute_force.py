"""
brute_force.py
Search-based Magic Square algorithms:
1. Naive Permutation Search (feasible strictly for n = 3)
2. Backtracking Search with Row/Column/Diagonal Pruning (effective for n = 3 and 4)
Includes node counting and execution time limits.
"""

import time
import itertools


def is_magic_square(grid, n, magic_constant):
    """Full square validation check."""
    # Row check
    for r in range(n):
        if sum(grid[r]) != magic_constant:
            return False

    # Column check
    for c in range(n):
        if sum(grid[r][c] for r in range(n)) != magic_constant:
            return False

    # Diagonals
    if sum(grid[i][i] for i in range(n)) != magic_constant:
        return False
    if sum(grid[i][n - 1 - i] for i in range(n)) != magic_constant:
        return False

    return True


def solve_naive_brute_force(n: int, time_limit: float = 10.0, stop_event=None):
    """
    Generates permutations of 1..n^2 and tests each arrangement.
    Returns: (grid, steps, nodes_count, time_spent, timed_out)
    """
    start_time = time.perf_counter()
    magic_constant = n * (n * n + 1) // 2
    total_cells = n * n
    nodes = 0

    for perm in itertools.permutations(range(1, total_cells + 1)):
        nodes += 1

        # Periodic cancellation and timeout checking
        if nodes % 10000 == 0:
            if stop_event and stop_event.is_set():
                return None, [], nodes, time.perf_counter() - start_time, False
            if time.perf_counter() - start_time > time_limit:
                return None, [], nodes, time.perf_counter() - start_time, True

        # Fast early row-1 check
        if sum(perm[:n]) != magic_constant:
            continue

        grid = [list(perm[i * n: (i + 1) * n]) for i in range(n)]
        if is_magic_square(grid, n, magic_constant):
            elapsed = time.perf_counter() - start_time
            steps = [(r, c, grid[r][c], f"Matched {grid[r][c]}") for r in range(n) for c in range(n)]
            return grid, steps, nodes, elapsed, False

    return None, [], nodes, time.perf_counter() - start_time, False


def solve_backtracking(n: int, time_limit: float = 10.0, stop_event=None):
    """
    Backtracking solver with pruning:
    Prunes branches when partial row, column, or diagonal cannot reach M(n).
    """
    start_time = time.perf_counter()
    magic_constant = n * (n * n + 1) // 2
    total_cells = n * n

    grid = [[0] * n for _ in range(n)]
    used = [False] * (total_cells + 1)

    row_sums = [0] * n
    col_sums = [0] * n
    diag1_sum = 0
    diag2_sum = 0

    nodes = 0
    timed_out = False

    def backtrack(cell_idx):
        nonlocal nodes, timed_out, diag1_sum, diag2_sum

        nodes += 1
        if nodes % 5000 == 0:
            if stop_event and stop_event.is_set():
                return False
            if time.perf_counter() - start_time > time_limit:
                timed_out = True
                return False

        if cell_idx == total_cells:
            return True

        r = cell_idx // n
        c = cell_idx % n
        is_last_col = (c == n - 1)
        is_last_row = (r == n - 1)

        # Candidates range
        for val in range(1, total_cells + 1):
            if used[val]:
                continue

            # Row pruning check
            new_row_sum = row_sums[r] + val
            if is_last_col and new_row_sum != magic_constant:
                continue
            if not is_last_col and new_row_sum >= magic_constant:
                continue

            # Column pruning check
            new_col_sum = col_sums[c] + val
            if is_last_row and new_col_sum != magic_constant:
                continue
            if not is_last_row and new_col_sum >= magic_constant:
                continue

            # Main diagonal pruning check
            if r == c:
                new_diag1 = diag1_sum + val
                if cell_idx == total_cells - 1 and new_diag1 != magic_constant:
                    continue
                if cell_idx != total_cells - 1 and new_diag1 >= magic_constant:
                    continue
            else:
                new_diag1 = diag1_sum

            # Anti-diagonal pruning check
            if r + c == n - 1:
                new_diag2 = diag2_sum + val
                if is_last_row and c == 0 and new_diag2 != magic_constant:
                    continue
                if (not (is_last_row and c == 0)) and new_diag2 >= magic_constant:
                    continue
            else:
                new_diag2 = diag2_sum

            # Place number
            grid[r][c] = val
            used[val] = True
            row_sums[r] = new_row_sum
            col_sums[c] = new_col_sum
            diag1_sum = new_diag1
            diag2_sum = new_diag2

            if backtrack(cell_idx + 1):
                return True

            if timed_out or (stop_event and stop_event.is_set()):
                return False

            # Backtrack state
            grid[r][c] = 0
            used[val] = False
            row_sums[r] -= val
            col_sums[c] -= val
            if r == c:
                diag1_sum -= val
            if r + c == n - 1:
                diag2_sum -= val

        return False

    success = backtrack(0)
    elapsed = time.perf_counter() - start_time

    if success:
        steps = [(r, c, grid[r][c], f"Backtracked cell ({r},{c}) = {grid[r][c]}") for r in range(n) for c in range(n)]
        return grid, steps, nodes, elapsed, False
    return None, [], nodes, elapsed, timed_out