from methods.base import CalculationError, NumericalMethod
from methods.math_function import MathFunction


class RootMethod(NumericalMethod):
    """Shared code for Bisection, False Position, and Newton-Raphson."""

    category = "Root finding"
    kind = "root"
    columns = []

    FUNCTION_FIELD = {
        "name": "function",
        "label": "f(x)",
        "default": "x^3 - x - 2",
        "hint": "Use + - * / ^ ( ), x, pi, e, sin, cos, tan, exp, sqrt, abs. ln is base e, log is base 10.",
    }
    TOLERANCE_FIELD = {
        "name": "tolerance",
        "label": "Tolerance",
        "default": "0.000001",
        "hint": "Stops when |x new - x old| is smaller than this.",
    }
    MAX_ITERATIONS_FIELD = {"name": "max_iterations", "label": "Max iterations", "default": 50, "hint": ""}

    def get_function(self, data):
        return MathFunction(data.get("function"))

    def get_tolerance(self, data):
        tolerance = self.get_number(data, "tolerance")
        if tolerance <= 0:
            raise CalculationError("tolerance must be greater than 0.")
        return tolerance

    def get_max_iterations(self, data):
        number = self.get_number(data, "max_iterations")
        if not number.is_integer() or number < 1 or number > 1000:
            raise CalculationError("max_iterations must be a whole number from 1 to 1000.")
        return int(number)

    def get_bracket(self, data, f):
        a = self.get_number(data, "a")
        b = self.get_number(data, "b")
        if a >= b:
            raise CalculationError("a must be smaller than b.")
        fa = f(a)
        fb = f(b)
        if fa != 0 and fb != 0 and (fa < 0) == (fb < 0):
            raise CalculationError(
                f"f(a) = {fa:.6g} and f(b) = {fb:.6g} have the same sign, so this interval has no bracket."
            )
        return a, b, fa, fb

    def endpoint_result(self, f, a, b, fa, fb):
        """Used when a or b is already an exact root."""
        root = a if fa == 0 else b
        row = {"n": 1, "a": a, "b": b, "fa": fa, "fb": fb, "x": root, "fx": 0.0, "error": None}
        return self.build_result(f, [row], True, [a, b])

    def build_result(self, f, rows, converged, start_points):
        last = rows[-1]
        warning = None
        if not converged:
            warning = f"Did not converge in {last['n']} iterations. The answer is only the latest estimate."
        elif len(start_points) == 2 and abs(last["fx"]) > max(abs(f(start_points[0])), abs(f(start_points[1]))):
            warning = "|f(x)| grew larger than at the ends of the interval. This may be a discontinuity, not a root."

        if converged:
            summary = f"{f.text}: x = {last['x']:.6g}"
        else:
            summary = f"{f.text}: did not converge"

        return {
            "summary": summary,
            "warning": warning,
            "answers": [
                {"label": "Root" if converged else "Latest estimate", "value": last["x"]},
                {"label": "f(x) at answer", "value": last["fx"]},
                {"label": "Iterations", "value": last["n"]},
            ],
            "table": {"title": "Iterations", "columns": self.columns, "rows": rows},
            "steps": [],
            "chart": self.build_chart(f, rows, converged, start_points),
        }

    def build_chart(self, f, rows, converged, start_points):
        low, high = self.chart_range(rows, converged, start_points)
        curve = []
        for i in range(400):
            x = low + (high - low) * i / 399
            curve.append({"x": x, "y": f.value_or_none(x)})

        return {
            "type": "root",
            "title": f"f(x) = {f.text}",
            "curve": curve,
            "low": low,
            "high": high,
            "iterations": [{"x": row["x"], "y": row["fx"], "n": row["n"]} for row in rows],
            "root": {"x": rows[-1]["x"], "y": rows[-1]["fx"]} if converged else None,
            "errors": [{"x": row["n"], "y": row["error"]} for row in rows if row["error"]],
        }

    def chart_range(self, rows, converged, start_points):
        center = rows[-1]["x"] if converged else start_points[0]
        reach = 100 * max(1, abs(center))

        # Points that flew very far away would make the graph unreadable.
        points = []
        for x in start_points + [row["x"] for row in rows]:
            if abs(x - center) <= reach:
                points.append(x)

        low = min(points, default=center)
        high = max(points, default=center)
        padding = max((high - low) * 0.12, 0.1 * max(1, abs(center)))
        return low - padding, high + padding
