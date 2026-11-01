"""
main.py
Interactive Tkinter GUI application for Magic Square Simulation & Verification.
Features:
- Constructive ($O(n^2)$) vs Brute-force modes
- Non-blocking execution via multi-threading
- Animation playback controls: Start, Pause, Step, Reset, Speed
- Live verification panel for rows, columns, and diagonals
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

from constructive import get_constructive_solution
from brute_force import solve_naive_brute_force, solve_backtracking


class MagicSquareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Magic Square Simulator - DSA Assignment 1")
        self.root.geometry("1100x780")
        self.root.minsize(950, 700)

        # App state variables
        self.order_var = tk.StringVar(value="3")
        self.mode_var = tk.StringVar(value="constructive")
        self.bf_strategy_var = tk.StringVar(value="backtrack")
        self.timeout_var = tk.StringVar(value="10")

        self.time_taken_var = tk.StringVar(value="--")
        self.nodes_explored_var = tk.StringVar(value="--")
        self.case_label_var = tk.StringVar(value="Case: Ready")

        # Simulation execution state
        self.steps = []
        self.current_step_idx = 0
        self.is_paused = True
        self.animation_job = None
        self.stop_search_event = threading.Event()

        self.cell_labels = []
        self.current_n = 3

        self._build_gui()

    def _build_gui(self):
        # Top toolbar
        toolbar = ttk.Frame(self.root, padding=10)
        toolbar.pack(fill=tk.X)

        ttk.Label(toolbar, text="Order (n):", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=3)
        ttk.Entry(toolbar, textvariable=self.order_var, width=5).pack(side=tk.LEFT, padx=5)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        # Mode Selection
        ttk.Radiobutton(toolbar, text="Constructive", variable=self.mode_var, value="constructive",
                        command=self._toggle_mode_widgets).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(toolbar, text="Solve using brute force", variable=self.mode_var, value="bruteforce",
                        command=self._toggle_mode_widgets).pack(side=tk.LEFT, padx=4)

        # Brute Force Options Frame
        self.bf_frame = ttk.Frame(toolbar)
        ttk.Radiobutton(self.bf_frame, text="Naive", variable=self.bf_strategy_var, value="naive").pack(side=tk.LEFT,
                                                                                                        padx=2)
        ttk.Radiobutton(self.bf_frame, text="Backtracking", variable=self.bf_strategy_var, value="backtrack").pack(
            side=tk.LEFT, padx=2)
        ttk.Label(self.bf_frame, text="Timeout (s):").pack(side=tk.LEFT, padx=(6, 2))
        ttk.Entry(self.bf_frame, textvariable=self.timeout_var, width=4).pack(side=tk.LEFT)
        self.bf_frame.pack(side=tk.LEFT, padx=8)
        self.bf_frame.pack_forget()  # Hidden initially

        # Run Button
        self.btn_run = ttk.Button(toolbar, text="Generate / Solve", command=self.on_solve_clicked)
        self.btn_run.pack(side=tk.LEFT, padx=10)

        self.btn_cancel = ttk.Button(toolbar, text="Stop Search", command=self.on_cancel_search, state=tk.DISABLED)
        self.btn_cancel.pack(side=tk.LEFT, padx=2)

        # Main Workspace: Grid View (Left) and Information Panel (Right)
        workspace = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        workspace.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left Container (Grid + Controls)
        left_container = ttk.Frame(workspace)
        workspace.add(left_container, weight=3)

        # Canvas for the Square
        self.grid_frame = ttk.Frame(left_container, padding=10)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)

        # Animation Controls
        anim_bar = ttk.Frame(left_container, padding=5)
        anim_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_play = ttk.Button(anim_bar, text="▶ Start", command=self.sim_play, state=tk.DISABLED)
        self.btn_play.pack(side=tk.LEFT, padx=3)
        self.btn_pause = ttk.Button(anim_bar, text="⏸ Pause", command=self.sim_pause, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, padx=3)
        self.btn_step = ttk.Button(anim_bar, text="⏭ Step", command=self.sim_step, state=tk.DISABLED)
        self.btn_step.pack(side=tk.LEFT, padx=3)
        self.btn_reset = ttk.Button(anim_bar, text="↺ Reset", command=self.sim_reset, state=tk.DISABLED)
        self.btn_reset.pack(side=tk.LEFT, padx=3)

        ttk.Label(anim_bar, text="Speed:").pack(side=tk.LEFT, padx=(10, 2))
        self.speed_slider = ttk.Scale(anim_bar, from_=10, to=800, orient=tk.HORIZONTAL)
        self.speed_slider.set(200)
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Right Container (Info, Metrics, Steps, Verification)
        right_container = ttk.Frame(workspace, padding=10)
        workspace.add(right_container, weight=2)

        # Case & Metrics Panel
        metrics_frame = ttk.LabelFrame(right_container, text="Run Statistics", padding=8)
        metrics_frame.pack(fill=tk.X, pady=4)

        ttk.Label(metrics_frame, textvariable=self.case_label_var, font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)

        m_row1 = ttk.Frame(metrics_frame)
        m_row1.pack(fill=tk.X, pady=2)
        ttk.Label(m_row1, text="Time Taken:").pack(side=tk.LEFT)
        ttk.Label(m_row1, textvariable=self.time_taken_var, foreground="#0066cc", font=("Consolas", 10, "bold")).pack(
            side=tk.LEFT, padx=5)

        m_row2 = ttk.Frame(metrics_frame)
        m_row2.pack(fill=tk.X, pady=2)
        ttk.Label(m_row2, text="Nodes / Permutations:").pack(side=tk.LEFT)
        ttk.Label(m_row2, textvariable=self.nodes_explored_var, foreground="#990000", font=("Consolas", 10)).pack(
            side=tk.LEFT, padx=5)

        # Algorithm Details
        algo_frame = ttk.LabelFrame(right_container, text="Algorithm Description & Current Step", padding=8)
        algo_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        self.txt_algo = tk.Text(algo_frame, wrap=tk.WORD, height=8, font=("Segoe UI", 9))
        self.txt_algo.pack(fill=tk.BOTH, expand=True)

        self.lbl_curr_step = ttk.Label(algo_frame, text="Current Step: Ready", foreground="#333333",
                                       font=("Segoe UI", 9, "italic"))
        self.lbl_curr_step.pack(anchor=tk.W, pady=(4, 0))

        # Verification Box
        verif_frame = ttk.LabelFrame(right_container, text="Verification Panel", padding=8)
        verif_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        self.txt_verif = tk.Text(verif_frame, wrap=tk.NONE, height=7, font=("Consolas", 9))
        self.txt_verif.pack(fill=tk.BOTH, expand=True)

    def _toggle_mode_widgets(self):
        if self.mode_var.get() == "bruteforce":
            self.bf_frame.pack(side=tk.LEFT, padx=8)
        else:
            self.bf_frame.pack_forget()

    def validate_inputs(self):
        try:
            n = int(self.order_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer for order n.")
            return None

        if n < 1:
            messagebox.showerror("Invalid Input", "Order n must be greater than or equal to 1.")
            return None
        if n == 2:
            messagebox.showerror("Invalid Order", "No magic square of order 2 exists. Please enter n >= 3.")
            return None

        return n

    def create_grid(self, n):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.cell_labels = []
        for r in range(n):
            row_labels = []
            self.grid_frame.rowconfigure(r, weight=1)
            for c in range(n):
                self.grid_frame.columnconfigure(c, weight=1)
                lbl = tk.Label(
                    self.grid_frame,
                    text="",
                    font=("Consolas", max(8, 22 - n)),
                    relief="solid",
                    borderwidth=1,
                    bg="#FFFFFF",
                )
                lbl.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                row_labels.append(lbl)
            self.cell_labels.append(row_labels)
        self.current_n = n

    def on_solve_clicked(self):
        n = self.validate_inputs()
        if n is None:
            return

        mode = self.mode_var.get()
        self.sim_pause()
        self.create_grid(n)
        self.steps = []
        self.current_step_idx = 0
        self.txt_verif.delete("1.0", tk.END)
        self.lbl_curr_step.config(text="Status: Solving...")

        if mode == "constructive":
            self.case_label_var.set("Running constructive algorithm...")
            t0 = time.perf_counter()
            grid, steps, case_name, algo_desc = get_constructive_solution(n)
            t1 = time.perf_counter()

            self.steps = steps
            self.case_label_var.set(f"Case: {case_name}")
            self.time_taken_var.set(f"{(t1 - t0) * 1000:.3f} ms")
            self.nodes_explored_var.set("N/A (Constructive)")

            self.txt_algo.delete("1.0", tk.END)
            self.txt_algo.insert(tk.END, algo_desc)

            self.enable_controls()
            self.sim_play()
        else:
            # Brute-force execution (threaded to prevent GUI freeze)
            try:
                timeout = float(self.timeout_var.get().strip())
            except ValueError:
                timeout = 10.0

            strategy = self.bf_strategy_var.get()
            self.case_label_var.set(f"Case: Brute Force ({strategy.capitalize()})")
            self.txt_algo.delete("1.0", tk.END)
            self.txt_algo.insert(tk.END,
                                 f"Searching for n={n} using {strategy} strategy...\nTimeout limit: {timeout}s.")

            self.btn_run.config(state=tk.DISABLED)
            self.btn_cancel.config(state=tk.NORMAL)
            self.stop_search_event.clear()

            thread = threading.Thread(
                target=self._run_brute_force_thread,
                args=(n, strategy, timeout),
                daemon=True
            )
            thread.start()

    def _run_brute_force_thread(self, n, strategy, timeout):
        if strategy == "naive":
            grid, steps, nodes, elapsed, timed_out = solve_naive_brute_force(
                n, timeout, self.stop_search_event
            )
        else:
            grid, steps, nodes, elapsed, timed_out = solve_backtracking(
                n, timeout, self.stop_search_event
            )

        self.root.after(0, self._on_search_complete, grid, steps, nodes, elapsed, timed_out)

    def _on_search_complete(self, grid, steps, nodes, elapsed, timed_out):
        self.btn_run.config(state=tk.NORMAL)
        self.btn_cancel.config(state=tk.DISABLED)

        self.time_taken_var.set(f"{elapsed:.4f} s")
        self.nodes_explored_var.set(f"{nodes:,}")

        if timed_out:
            messagebox.showwarning("Timeout", "Search stopped: User-set time limit was reached.")
            self.lbl_curr_step.config(text="Search Timed Out.")
            return

        if self.stop_search_event.is_set():
            self.lbl_curr_step.config(text="Search Canceled by user.")
            return

        if grid is None:
            messagebox.showinfo("Result", "No magic square solution was found.")
            return

        self.steps = steps
        self.enable_controls()
        self.sim_play()

    def on_cancel_search(self):
        self.stop_search_event.set()
        self.btn_cancel.config(state=tk.DISABLED)

    # ---------------- Animation Controls ---------------- #
    def enable_controls(self):
        self.btn_play.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.NORMAL)
        self.btn_step.config(state=tk.NORMAL)
        self.btn_reset.config(state=tk.NORMAL)

    def sim_play(self):
        self.is_paused = False
        self._step_and_loop()

    def sim_pause(self):
        self.is_paused = True
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

    def sim_step(self):
        self.sim_pause()
        self._apply_next_step()

    def sim_reset(self):
        self.sim_pause()
        self.current_step_idx = 0
        for r in range(self.current_n):
            for c in range(self.current_n):
                self.cell_labels[r][c].config(text="", bg="#FFFFFF")
        self.lbl_curr_step.config(text="Status: Reset to beginning.")

    def _step_and_loop(self):
        if self.is_paused:
            return
        if self.current_step_idx < len(self.steps):
            self._apply_next_step()
            delay = int(810 - self.speed_slider.get())
            self.animation_job = self.root.after(delay, self._step_and_loop)
        else:
            self.is_paused = True
            self.verify_solution()

    def _apply_next_step(self):
        if self.current_step_idx >= len(self.steps):
            return

        # Restore color of previously highlighted cell
        if self.current_step_idx > 0:
            prev_r, prev_c, _, _ = self.steps[self.current_step_idx - 1]
            self.cell_labels[prev_r][prev_c].config(bg="#EAF2F8")

        r, c, val, explanation = self.steps[self.current_step_idx]
        self.cell_labels[r][c].config(text=str(val), bg="#F9E79F")  # Yellow highlight
        self.lbl_curr_step.config(text=f"Step {self.current_step_idx + 1}/{len(self.steps)}: {explanation}")

        self.current_step_idx += 1
        if self.current_step_idx == len(self.steps):
            self.verify_solution()

    # ---------------- Verification ---------------- #
    def verify_solution(self):
        n = self.current_n
        magic_constant = n * (n * n + 1) // 2

        grid = []
        for r in range(n):
            row_vals = []
            for c in range(n):
                txt = self.cell_labels[r][c].cget("text")
                row_vals.append(int(txt) if txt else 0)
            grid.append(row_vals)

        row_sums = [sum(grid[r]) for r in range(n)]
        col_sums = [sum(grid[r][c] for r in range(n)) for c in range(n)]
        d1 = sum(grid[i][i] for i in range(n))
        d2 = sum(grid[i][n - 1 - i] for i in range(n))

        valid = (
                all(s == magic_constant for s in row_sums) and
                all(s == magic_constant for s in col_sums) and
                d1 == magic_constant and d2 == magic_constant
        )

        self.txt_verif.delete("1.0", tk.END)
        self.txt_verif.insert(tk.END, f"Target Magic Constant M({n}) = {magic_constant}\n")
        self.txt_verif.insert(tk.END, f"Row Sums   : {row_sums}\n")
        self.txt_verif.insert(tk.END, f"Col Sums   : {col_sums}\n")
        self.txt_verif.insert(tk.END, f"Diagonals  : Main={d1}, Anti={d2}\n")
        self.txt_verif.insert(
            tk.END,
            f"Result     : {'✔ VALID MAGIC SQUARE' if valid else '✖ INVALID SQUARE'}\n"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = MagicSquareApp(root)
    root.mainloop()