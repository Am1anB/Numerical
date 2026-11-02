import math

from methods.base import CalculationError, NumericalMethod


class LinearMethod(NumericalMethod):
    """Shared code for Gauss Elimination and Gauss-Jordan."""

    category = "Linear systems"
    kind = "matrix"
    fields = [
        {
            "name": "system",
            "default": {"A": [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], "b": [8, -11, -3]},
        }
    ]

    MIN_SIZE = 2
    MAX_SIZE = 8

    def get_system(self, data):
        system = data.get("system")
        if not isinstance(system, dict):
            raise CalculationError("Please enter matrix A and vector b.")
        A = system.get("A")
        b = system.get("b")
        if not isinstance(A, list) or not isinstance(b, list):
            raise CalculationError("Please enter matrix A and vector b.")

        n = len(b)
        if n < self.MIN_SIZE or n > self.MAX_SIZE:
            raise CalculationError(f"The system must have {self.MIN_SIZE} to {self.MAX_SIZE} variables.")
        if len(A) != n or any(not isinstance(row, list) or len(row) != n for row in A):
            raise CalculationError("A must be a square matrix with the same size as b.")

        new_A = []
        for i in range(n):
            new_A.append([self.get_cell(A[i][j], f"A[{i + 1}][{j + 1}]") for j in range(n)])
        new_b = [self.get_cell(b[i], f"b[{i + 1}]") for i in range(n)]
        return new_A, new_b

    def get_cell(self, value, label):
        if value is None or value == "":
            raise CalculationError(f"Please fill in {label}.")
        return self.to_number(value, label)

    def make_augmented_matrix(self, A, b):
        return [A[i] + [b[i]] for i in range(len(b))]

    def add_step(self, steps, description, matrix=None):
        snapshot = [row.copy() for row in matrix] if matrix else None
        steps.append({"description": description, "matrix": snapshot})

    def swap_best_pivot(self, matrix, column, steps):
        """Partial pivoting: moves the largest value in this column up to the pivot row."""
        n = len(matrix)
        best_row = column
        for row in range(column + 1, n):
            if abs(matrix[row][column]) > abs(matrix[best_row][column]):
                best_row = row

        largest = max(abs(value) for row in matrix for value in row[:n])
        if abs(matrix[best_row][column]) <= largest * 1e-12:
            raise CalculationError("A pivot is zero, so the matrix is singular and has no unique solution.")

        if best_row != column:
            matrix[column], matrix[best_row] = matrix[best_row], matrix[column]
            self.add_step(steps, f"Swap R{column + 1} and R{best_row + 1}", matrix)

    def build_result(self, A, b, solution, steps):
        if not all(math.isfinite(value) for value in solution):
            raise CalculationError("The answer is too large to represent.")

        rows = []
        answers = []
        for i in range(len(b)):
            left_side = sum(A[i][j] * solution[j] for j in range(len(b)))
            rows.append({"variable": f"x{i + 1}", "value": solution[i], "residual": left_side - b[i]})
            answers.append({"label": f"x{i + 1}", "value": solution[i]})

        text = ", ".join(f"{value:.6g}" for value in solution)
        columns = [
            {"key": "variable", "label": "Variable"},
            {"key": "value", "label": "Value"},
            {"key": "residual", "label": "Ax - b"},
        ]
        return {
            "summary": f"x = ({text})",
            "warning": None,
            "answers": answers,
            "table": {"title": "Solution check", "columns": columns, "rows": rows},
            "steps": steps,
            "chart": self.build_chart(A, b, solution),
        }

    def build_chart(self, A, b, solution):
        if len(b) != 2:
            return {"type": "bars", "title": "Value of each variable", "values": solution}

        x, y = solution
        reach = max(5, abs(x), abs(y))
        x_low, x_high = x - reach, x + reach
        y_low, y_high = y - reach, y + reach

        lines = []
        for i in range(2):
            a1, a2 = A[i]
            # Solve for whichever variable is safe, so vertical lines also work.
            if abs(a2) >= abs(a1):
                points = [{"x": p, "y": (b[i] - a1 * p) / a2} for p in (x_low, x_high)]
            else:
                points = [{"x": (b[i] - a2 * p) / a1, "y": p} for p in (y_low, y_high)]
            label = f"{a1:.6g}x1 + {a2:.6g}x2 = {b[i]:.6g}".replace("+ -", "- ")
            lines.append({"label": label, "points": points})

        return {
            "type": "lines",
            "title": "The solution is where the two lines cross",
            "lines": lines,
            "solution": {"x": x, "y": y},
            "x_low": x_low,
            "x_high": x_high,
            "y_low": y_low,
            "y_high": y_high,
        }
