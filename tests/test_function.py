import math

import pytest

from methods.base import CalculationError
from methods.math_function import MathFunction


@pytest.mark.parametrize(
    "text, x, expected",
    [
        ("x^3 - x - 2", 2, 4),
        ("2x + 3", 1, 5),
        ("3(x+1)", 1, 6),
        ("x(x+1)", 2, 6),
        ("(x+1)(x+2)", 1, 6),
        ("2sin(x)", 0, 0),
        ("-x^2", 3, -9),
        ("2^3^2", 0, 512),
        ("2^-1", 0, 0.5),
        ("2.5x", 2, 5),
        ("ln(e) + log(100)", 0, 3),
        ("sin(pi/2) * sqrt(16)", 0, 4),
    ],
)
def test_values(text, x, expected):
    assert MathFunction(text)(x) == pytest.approx(expected)


@pytest.mark.parametrize(
    "text",
    [
        "", "x +", "(x", "x2", "sin", "sin + 1", "y + 1", "2 3", "import os", "__import__('os')",
        "x.real", "sin.x", "(1).real", "open", "x; x", "x[0]", "[x]", "lambda", "exit()",
    ],
)
def test_rejects_bad_text(text):
    with pytest.raises(CalculationError):
        MathFunction(text)


def test_rejects_long_text():
    with pytest.raises(CalculationError):
        MathFunction("x" + "+x" * 200)


def test_deepest_allowed_nesting_still_works():
    assert MathFunction("(" * 95 + "x" + ")" * 95)(2) == 2


def test_huge_power_finishes_with_an_error():
    f = MathFunction("9^9^9^9")
    assert f.value_or_none(0) is None


@pytest.mark.parametrize("text", ["1/x", "ln(x)", "sqrt(x - 1)", "(x - 1)^(1/3)", "exp(1000 * (x + 1))"])
def test_undefined_values(text):
    f = MathFunction(text)
    assert f.value_or_none(0) is None
    with pytest.raises(CalculationError):
        f(0)


def test_derivative():
    assert MathFunction("x^3").derivative(2) == pytest.approx(12, abs=1e-6)
    assert MathFunction("sin(x)").derivative(0) == pytest.approx(math.cos(0), abs=1e-6)
