import math

from methods.base import CalculationError
from methods.root_method import RootMethod


class NewtonRaphson(RootMethod):
    slug = "newton-raphson"
    name = "Newton-Raphson"
    description = "Follows the tangent line at the current point down to the x-axis. f'(x) is calculated for you."
    formula = "x_new = x - f(x) / f'(x)"
    fields = [
        RootMethod.FUNCTION_FIELD,
        {"name": "x0", "label": "x0 (starting point)", "default": 1.5, "hint": "Pick a value close to the root."},
        RootMethod.TOLERANCE_FIELD,
        RootMethod.MAX_ITERATIONS_FIELD,
    ]
    columns = [
        {"key": "n", "label": "n"},
        {"key": "x_old", "label": "x"},
        {"key": "f_old", "label": "f(x)"},
        {"key": "df_old", "label": "f'(x)"},
        {"key": "x", "label": "x new"},
        {"key": "fx", "label": "f(x new)"},
        {"key": "error", "label": "Error"},
    ]

    def solve(self, data):
        f = self.get_function(data)
        tolerance = self.get_tolerance(data)
        max_iterations = self.get_max_iterations(data)
        x = self.get_number(data, "x0")
        start_points = [x]

        rows = []
        converged = False

        for n in range(1, max_iterations + 1):
            fx = f(x)
            dfx = f.derivative(x)
            if dfx == 0:
                raise CalculationError(f"f'({x:.6g}) = 0, so the tangent line never reaches the x-axis. Try another x0.")

            x_new = x - fx / dfx
            if not math.isfinite(x_new):
                raise CalculationError("x grew too large. Try another x0.")

            f_new = f(x_new)
            error = abs(x_new - x)
            rows.append({"n": n, "x_old": x, "f_old": fx, "df_old": dfx, "x": x_new, "fx": f_new, "error": error})

            if f_new == 0 or error < tolerance:
                converged = True
                break

            x = x_new

        return self.build_result(f, rows, converged, start_points)
