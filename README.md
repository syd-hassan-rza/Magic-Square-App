# Magic Square Simulation & Solver

A desktop application developed with Python (Tkinter) to construct, animate, and verify magic squares of order $n \ge 3$. The tool supports both direct $\mathcal{O}(n^2)$ constructive methods and search-based brute-force techniques.

---

## 📷 Screenshots

### Main Interface
(<img width="1102" height="806" alt="image" src="https://github.com/user-attachments/assets/9c09a75b-44dd-42f8-9f5b-38b0eea70486" />
)
*Figure 1: Application workspace with input controls, simulation grid, and verification panel.*

### Simulation in Progress
(<img width="1102" height="811" alt="image" src="https://github.com/user-attachments/assets/8b1b5c0a-c9f9-423f-b380-4f9845c37c35" />
)
*Figure 2: Step-by-step constructive fill with cell highlighting and algorithm steps.*

### Brute-Force & Verification
(<img width="1103" height="813" alt="image" src="https://github.com/user-attachments/assets/8c9f42da-dc5a-40a7-b960-7bcc2473127f" />
)
*Figure 3: Search statistics (time elapsed, nodes visited) and magic constant verification.*

---

## ⚙️ Functionality

### 1. Constructive Generation ($\mathcal{O}(n^2)$)
Automatically identifies the input order category and executes the corresponding deterministic algorithm:
- **Odd Orders ($n \pmod 2 \ne 0$):** Siamese (de la Loubère) method.
- **Doubly Even Orders ($n \pmod 4 = 0$):** 4×4 block diagonal/complement reflection.
- **Singly Even Orders ($n \pmod 4 = 2$):** Strachey’s method using 4 sub-quadrants with designated column swaps.

### 2. Brute-Force Search
- **Naive Search:** Iterates through full permutations of numbers $1 \dots n^2$. Best suited strictly for $n = 3$.
- **Backtracking with Pruning:** Recursively builds the grid and cuts search branches as soon as partial row, column, or diagonal sums exceed or fail to reach $M(n)$.
- **Multi-threaded Execution:** Runs searches on a background thread to prevent UI freezing, complete with user-configured timeouts and a cancel button.

### 3. Interactive Visual Simulation
- Step-by-step playback with **Play**, **Pause**, **Step**, and **Reset** controls.
- Dynamic speed slider adjusting delay between placement steps.
- Active cell visual highlighting with step descriptions.

### 4. Mathematical Verification
- Computes target magic constant: $M(n) = \frac{n(n^2 + 1)}{2}$.
- Dynamically calculates all row sums, column sums, and both diagonal sums to validate correctness.
- Handles invalid inputs ($n < 1$, $n = 2$, non-numeric values) via popup alerts.

---

## 📁 Project Structure

```text
├── main.py              # Tkinter GUI, animation thread, and event handling
├── constructive.py      # O(n^2) algorithms (Siamese, Doubly Even, Strachey)
├── brute_force.py       # Naive permutation and pruned backtracking solvers
├── README.md            # Documentation and instructions
└── screenshots/         # Application screenshot storage
```

---

## 🚀 How to Run

### Requirements
- **Python 3.10+**
- Standard libraries only (`tkinter`, `itertools`, `threading`, `time`). No external dependencies required.

### Launch
Run the following command from the project root:

```bash
python main.py
```
