import math


class CalculationError(Exception):
    """An error message that should be shown to the user."""


class NumericalMethod:
    """Parent class of every topic."""

    slug = ""
    name = ""
    category = ""
    description = ""
    formula = ""
    kind = ""
    fields = []

    def solve(self, data):
        raise NotImplementedError

    def info(self):
        return {
            "slug": self.slug,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "formula": self.formula,
            "kind": self.kind,
            "fields": self.fields,
        }

    def get_number(self, data, name):
        value = data.get(name)
        if value is None or value == "":
            raise CalculationError(f"Please enter {name}.")
        return self.to_number(value, name)

    def to_number(self, value, label):
        if isinstance(value, bool):
            raise CalculationError(f"{label} must be a number.")
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise CalculationError(f"{label} must be a number.")
        if not math.isfinite(number):
            raise CalculationError(f"{label} must be a finite number.")
        return number
