from methods.linear_method import LinearMethod


class GaussElimination(LinearMethod):
    slug = "gauss-elimination"
    name = "Gauss Elimination"
    description = "Eliminates variables until the matrix is upper triangular, then uses back substitution."
    formula = "[A|b] -> [U|c] -> back substitution"

    def solve(self, data):
        A, b = self.get_system(data)
        n = len(b)
        matrix = self.make_augmented_matrix(A, b)
        steps = []
        self.add_step(steps, "Starting matrix [A|b]", matrix)

        # Forward elimination: make zeros below each pivot.
        for column in range(n):
            self.swap_best_pivot(matrix, column, steps)

            for row in range(column + 1, n):
                factor = matrix[row][column] / matrix[column][column]
                if factor == 0:
                    continue
                for j in range(column, n + 1):
                    matrix[row][j] -= factor * matrix[column][j]
                matrix[row][column] = 0.0
                self.add_step(steps, f"R{row + 1} = R{row + 1} - ({factor:.6g}) * R{column + 1}", matrix)

        # Back substitution: solve from the last variable to the first.
        solution = [0.0] * n
        for i in range(n - 1, -1, -1):
            known = 0.0
            for j in range(i + 1, n):
                known += matrix[i][j] * solution[j]
            solution[i] = (matrix[i][n] - known) / matrix[i][i]
            self.add_step(
                steps,
                f"x{i + 1} = ({matrix[i][n]:.6g} - {known:.6g}) / {matrix[i][i]:.6g} = {solution[i]:.6g}",
            )

        return self.build_result(A, b, solution, steps)
