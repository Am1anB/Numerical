import pytest

from methods.base import CalculationError
from methods.bisection import Bisection
from methods.false_position import FalsePosition
from methods.gauss_elimination import GaussElimination
from methods.gauss_jordan import GaussJordan
from methods.newton_raphson import NewtonRaphson

ROOT = 1.5213797068045676  # the real root of x^3 - x - 2
ROOT_METHODS = [Bisection(), FalsePosition(), NewtonRaphson()]
BRACKET_METHODS = [Bisection(), FalsePosition()]
LINEAR_METHODS = [GaussElimination(), GaussJordan()]


def inputs(**changes):
    data = {"function": "x^3 - x - 2", "a": 1, "b": 2, "x0": 1.5, "tolerance": 1e-8, "max_iterations": 100}
    data.update(changes)
    return data


def system(A, b):
    return {"system": {"A": A, "b": b}}


def values(result):
    return [answer["value"] for answer in result["answers"]]


@pytest.mark.parametrize("method", ROOT_METHODS)
def test_finds_root(method):
    assert values(method.solve(inputs()))[0] == pytest.approx(ROOT, abs=1e-6)


def test_bisection_first_steps():
    rows = Bisection().solve(inputs())["table"]["rows"]
    assert rows[0]["x"] == 1.5
    assert rows[1]["x"] == 1.75
    assert rows[1]["error"] == 0.25


def test_false_position_first_step():
    rows = FalsePosition().solve(inputs())["table"]["rows"]
    assert rows[0]["x"] == pytest.approx(4 / 3)


def test_newton_first_step():
    row = NewtonRaphson().solve(inputs())["table"]["rows"][0]
    assert row["df_old"] == pytest.approx(5.75, abs=1e-6)
    assert row["x"] == pytest.approx(1.5 + 0.125 / 5.75, abs=1e-6)


def test_newton_is_faster_than_bisection():
    newton = NewtonRaphson().solve(inputs())["table"]["rows"]
    bisection = Bisection().solve(inputs())["table"]["rows"]
    assert len(newton) < 8 < len(bisection)


@pytest.mark.parametrize("method", BRACKET_METHODS)
def test_needs_sign_change(method):
    with pytest.raises(CalculationError):
        method.solve(inputs(a=2, b=3))


@pytest.mark.parametrize("method", BRACKET_METHODS)
def test_a_must_be_below_b(method):
    with pytest.raises(CalculationError):
        method.solve(inputs(a=2, b=1))


@pytest.mark.parametrize("method", BRACKET_METHODS)
@pytest.mark.parametrize("function, root", [("x - 1", 1), ("x - 2", 2)])
def test_root_on_end_of_interval(method, function, root):
    assert values(method.solve(inputs(function=function)))[0] == root


def test_warns_about_discontinuity():
    assert "discontinuity" in Bisection().solve(inputs(function="1/x", a=-1, b=2))["warning"]


def test_newton_zero_derivative():
    with pytest.raises(CalculationError):
        NewtonRaphson().solve(inputs(function="x^2 + 1", x0=0))


def test_newton_not_converged():
    result = NewtonRaphson().solve(inputs(function="x^2 + 1", x0=0.5, max_iterations=10))
    assert "Did not converge" in result["warning"]
    assert result["summary"] == "x^2 + 1: did not converge"
    assert result["chart"]["root"] is None


def test_newton_divergence_gives_clean_error():
    with pytest.raises(CalculationError):
        NewtonRaphson().solve(inputs(function="atan(x)", x0=3, max_iterations=1000))


def test_chart_stays_readable_when_points_fly_away():
    chart = NewtonRaphson().solve(inputs(function="atan(x)", x0=1.5, max_iterations=4))["chart"]
    assert chart["low"] < 1.5 < chart["high"]
    assert chart["high"] - chart["low"] < 1000


@pytest.mark.parametrize(
    "changes",
    [
        {"tolerance": 0},
        {"tolerance": -1},
        {"max_iterations": 0},
        {"max_iterations": 1.5},
        {"a": "abc"},
        {"a": ""},
        {"a": True},
        {"a": float("nan")},
        {"function": ""},
        {"function": 5},
    ],
)
def test_bad_root_inputs(changes):
    with pytest.raises(CalculationError):
        Bisection().solve(inputs(**changes))


@pytest.mark.parametrize("method", LINEAR_METHODS)
def test_solves_3x3(method):
    result = method.solve(system([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], [8, -11, -3]))
    assert values(result) == pytest.approx([2, 3, -1])
    assert all(abs(row["residual"]) < 1e-9 for row in result["table"]["rows"])
    assert result["chart"]["type"] == "bars"


@pytest.mark.parametrize("method", LINEAR_METHODS)
def test_zero_on_diagonal(method):
    assert values(method.solve(system([[0, 1], [1, 0]], [2, 3]))) == pytest.approx([3, 2])


@pytest.mark.parametrize("method", LINEAR_METHODS)
def test_tiny_pivot(method):
    assert values(method.solve(system([[1e-20, 1], [1, 1]], [1, 2]))) == pytest.approx([1, 1])


@pytest.mark.parametrize("method", LINEAR_METHODS)
def test_singular_matrix(method):
    with pytest.raises(CalculationError):
        method.solve(system([[1, 2], [2, 4]], [3, 6]))


def test_input_is_not_changed_by_solving():
    data = system([[2, 1], [1, 3]], [3, 5])
    GaussJordan().solve(data)
    assert data == system([[2, 1], [1, 3]], [3, 5])


def test_gauss_jordan_ends_with_identity():
    matrix = GaussJordan().solve(system([[2, 1], [1, 3]], [3, 5]))["steps"][-1]["matrix"]
    assert [row[:2] for row in matrix] == [[1, 0], [0, 1]]


def test_gauss_elimination_is_upper_triangular():
    steps = GaussElimination().solve(system([[2, 1, 1], [4, 3, 3], [8, 7, 9]], [1, 1, 1]))["steps"]
    matrix = [step for step in steps if step["matrix"]][-1]["matrix"]
    assert matrix[1][0] == matrix[2][0] == matrix[2][1] == 0
    assert sum(step["matrix"] is None for step in steps) == 3


def test_two_variable_chart():
    chart = GaussJordan().solve(system([[1, 1], [1, -1]], [4, 2]))["chart"]
    assert chart["type"] == "lines"
    assert chart["solution"] == pytest.approx({"x": 3, "y": 1})


def test_vertical_line_chart():
    chart = GaussJordan().solve(system([[1, 0], [0, 1]], [1, 2]))["chart"]
    assert {point["x"] for point in chart["lines"][0]["points"]} == {1}


@pytest.mark.parametrize(
    "bad",
    [
        {"A": [[1]], "b": [1]},
        {"A": [[1, 2], [3]], "b": [1, 2]},
        {"A": [[1, "x"], [3, 4]], "b": [1, 2]},
        {"A": [[1, ""], [3, 4]], "b": [1, 2]},
        {"A": [[1, True], [3, 4]], "b": [1, 2]},
        "not a system",
    ],
)
def test_bad_systems(bad):
    with pytest.raises(CalculationError):
        GaussJordan().solve({"system": bad})
