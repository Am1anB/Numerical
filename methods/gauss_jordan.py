from methods.linear_method import LinearMethod


class GaussJordan(LinearMethod):
    slug = "gauss-jordan"
    name = "Gauss-Jordan"
    description = "Makes each pivot 1 and clears the values above and below it, so the answer is in the last column."
    formula = "[A|b] -> [I|x]"

    def solve(self, data):
        A, b = self.get_system(data)
        n = len(b)
        matrix = self.make_augmented_matrix(A, b)
        steps = []
        self.add_step(steps, "Starting matrix [A|b]", matrix)

        for column in range(n):
            self.swap_best_pivot(matrix, column, steps)

            # Make the pivot equal to 1.
            pivot = matrix[column][column]
            for j in range(n + 1):
                matrix[column][j] /= pivot
            matrix[column][column] = 1.0
            self.add_step(steps, f"R{column + 1} = R{column + 1} / {pivot:.6g}", matrix)

            # Make zeros above and below the pivot.
            for row in range(n):
                factor = matrix[row][column]
                if row == column or factor == 0:
                    continue
                for j in range(n + 1):
                    matrix[row][j] -= factor * matrix[column][j]
                matrix[row][column] = 0.0
                self.add_step(steps, f"R{row + 1} = R{row + 1} - ({factor:.6g}) * R{column + 1}", matrix)

        solution = [matrix[i][n] for i in range(n)]
        return self.build_result(A, b, solution, steps)
