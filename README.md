# Numerical Methods Website

A simple website for a numerical methods class. Choose a topic, enter your values, and see the graph and the answer.

Topics: Bisection, False Position, Newton-Raphson, Gauss Elimination, Gauss-Jordan.

## How to run

You need [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run python app.py
```

Then open http://127.0.0.1:5000

To run the tests: `uv run pytest`

## Files

```
app.py                         Flask pages and API
database.py                    Database class (SQLite)
methods/
  bisection.py                 Bisection
  false_position.py            False Position
  newton_raphson.py            Newton-Raphson
  gauss_elimination.py         Gauss Elimination
  gauss_jordan.py              Gauss-Jordan
  base.py                      NumericalMethod, the parent class of every topic
  root_method.py               Shared code for the 3 root finding topics
  linear_method.py             Shared code for the 2 linear system topics
  math_function.py             Turns text like "x^2 - 2" into a function
templates/                     HTML pages
static/                        CSS and JavaScript
tests/                         Tests
```

Each topic class inherits like this:

```
NumericalMethod
├── RootMethod
│   ├── Bisection
│   ├── FalsePosition
│   └── NewtonRaphson
└── LinearMethod
    ├── GaussElimination
    └── GaussJordan
```

## Adding a topic

1. Add a new file in `methods/` with a class that has a `solve(self, data)` method.
2. Add the class to `ALL_METHODS` in `methods/__init__.py`.

## API

| Method | Path | What it does |
|---|---|---|
| GET | `/api/methods` | List all topics |
| POST | `/api/methods/<slug>/calculate` | Calculate and save the result |
| GET | `/api/calculations?method=<slug>&limit=20` | List saved calculations |
| GET | `/api/calculations/<id>` | Get one saved calculation |
| DELETE | `/api/calculations/<id>` | Delete a saved calculation |

Example:

```
POST /api/methods/bisection/calculate
{"function": "x^3 - x - 2", "a": 1, "b": 2, "tolerance": 0.000001, "max_iterations": 50}
```

Errors come back as `{"error": "message"}`.

## Writing f(x)

Use `+ - * / ^ ( )`, the variable `x`, the constants `pi` and `e`, and the functions
`sin cos tan asin acos atan exp ln log sqrt abs`. `ln` is base e and `log` is base 10.
You can write `2x` instead of `2*x`.
