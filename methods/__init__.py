from methods.bisection import Bisection
from methods.false_position import FalsePosition
from methods.gauss_elimination import GaussElimination
from methods.gauss_jordan import GaussJordan
from methods.newton_raphson import NewtonRaphson

ALL_METHODS = [Bisection(), FalsePosition(), NewtonRaphson(), GaussElimination(), GaussJordan()]


def find_method(slug):
    for method in ALL_METHODS:
        if method.slug == slug:
            return method
    return None
