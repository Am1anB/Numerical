from methods.root_method import RootMethod


class FalsePosition(RootMethod):
    slug = "false-position"
    name = "False Position"
    description = "Draws a straight line between (a, f(a)) and (b, f(b)) and uses the point where it crosses the x-axis."
    formula = "c = b - f(b)(b - a) / (f(b) - f(a))"
    fields = [
        RootMethod.FUNCTION_FIELD,
        {"name": "a", "label": "a (lower bound)", "default": 1, "hint": "f(a) and f(b) must have opposite signs."},
        {"name": "b", "label": "b (upper bound)", "default": 2, "hint": ""},
        RootMethod.TOLERANCE_FIELD,
        RootMethod.MAX_ITERATIONS_FIELD,
    ]
    columns = [
        {"key": "n", "label": "n"},
        {"key": "a", "label": "a"},
        {"key": "b", "label": "b"},
        {"key": "fa", "label": "f(a)"},
        {"key": "fb", "label": "f(b)"},
        {"key": "x", "label": "c"},
        {"key": "fx", "label": "f(c)"},
        {"key": "error", "label": "Error"},
    ]

    def solve(self, data):
        f = self.get_function(data)
        tolerance = self.get_tolerance(data)
        max_iterations = self.get_max_iterations(data)
        a, b, fa, fb = self.get_bracket(data, f)
        start_points = [a, b]

        if fa == 0 or fb == 0:
            return self.endpoint_result(f, a, b, fa, fb)

        rows = []
        old_c = None
        converged = False

        for n in range(1, max_iterations + 1):
            c = b - fb * (b - a) / (fb - fa)
            fc = f(c)
            error = None if old_c is None else abs(c - old_c)
            rows.append({"n": n, "a": a, "b": b, "fa": fa, "fb": fb, "x": c, "fx": fc, "error": error})

            if fc == 0 or (error is not None and error < tolerance):
                converged = True
                break

            # Keep the side where the sign changes.
            if (fa < 0) == (fc < 0):
                a = c
                fa = fc
            else:
                b = c
                fb = fc
            old_c = c

        return self.build_result(f, rows, converged, start_points)
