import math
import re

from methods.base import CalculationError

ALLOWED_NAMES = {
    "pi": math.pi,
    "e": math.e,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "exp": math.exp,
    "ln": math.log,
    "log": math.log10,
    "sqrt": math.sqrt,
    "abs": abs,
}


class MathFunction:
    """Turns text like "x^3 - x - 2" into a function we can call: f(1.5)."""

    MAX_LENGTH = 200

    def __init__(self, text):
        if not isinstance(text, str) or text.strip() == "":
            raise CalculationError("Please enter f(x).")
        if len(text) > self.MAX_LENGTH:
            raise CalculationError(f"f(x) must be at most {self.MAX_LENGTH} characters.")

        self.text = text.strip()
        self.check_allowed_words(self.text)

        try:
            self.code = compile(self.to_python(self.text), "f(x)", "eval")
        except (SyntaxError, ValueError, MemoryError, RecursionError):
            raise CalculationError(f"Could not read f(x) = {self.text}")

        # Find mistakes such as "x2" or "sin + 1" right away.
        try:
            result = self.run(1.0)
        except (NameError, TypeError, AttributeError):
            raise CalculationError(f"Could not read f(x) = {self.text}")
        except (ValueError, ZeroDivisionError, OverflowError):
            return
        if callable(result):
            raise CalculationError(f"Could not read f(x) = {self.text}")

    def check_allowed_words(self, text):
        # eval() is only safe here because the text can contain nothing except
        # numbers, math symbols, and the names in ALLOWED_NAMES.
        if not re.fullmatch(r"[0-9a-z.+\-*/^() ]+", text):
            raise CalculationError("f(x) contains a character that is not allowed.")
        for word in re.findall(r"[a-z]+", text):
            if word != "x" and word not in ALLOWED_NAMES:
                raise CalculationError(f"Unknown name '{word}'. Use x, pi, e, or a math function.")

    def to_python(self, text):
        text = text.replace("^", "**")
        # 2x -> 2*x, 3(x+1) -> 3*(x+1), x(x+1) -> x*(x+1), (x+1)(x+2) -> (x+1)*(x+2)
        text = re.sub(r"(\d|\)|\bx\b) *(?=[a-z(])", r"\1*", text)
        # Use floats so a huge power like 9^9^9 stops with an error instead of running forever.
        return re.sub(r"(?<![\d.])(\d+)(?![\d.])", r"\1.0", text)

    def run(self, x):
        return eval(self.code, {"__builtins__": {}}, {**ALLOWED_NAMES, "x": x})

    def __call__(self, x):
        value = self.value_or_none(x)
        if value is None:
            raise CalculationError(f"f({x:.6g}) cannot be calculated.")
        return value

    def value_or_none(self, x):
        """Returns None where the function is undefined, such as 1/x at x = 0."""
        try:
            value = self.run(x)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            return None
        if isinstance(value, complex) or not math.isfinite(value):
            return None
        return value

    def derivative(self, x):
        """Numerical derivative using the central difference formula."""
        h = 1e-6
        return (self(x + h) - self(x - h)) / (2 * h)
