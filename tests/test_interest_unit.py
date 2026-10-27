"""Unit tests for InterestCalculator: normal, boundary and exception cases."""
import pytest
from app.interest import InterestCalculator


@pytest.fixture
def calculator():
    return InterestCalculator()


@pytest.mark.parametrize(
    "principal, rate, years, expected",
    [
        (10000, 5, 0, 0),           # lower boundary of years
        (10000, 5, 1, 500),         # smallest real term
        (10000, 5, 3, 1500),        # typical value
        (0, 5, 2, 0),               # boundary: zero principal
        (10000, 0, 2, 0),           # boundary: zero rate
        (12500, 7.25, 2, 1812.5),  # fractional rate
    ],
)
def test_valid_inputs_return_expected_interest(calculator, principal, rate, years, expected):
    assert calculator.simple_interest(principal, rate, years) == pytest.approx(expected)


@pytest.mark.parametrize("bad_years", [1.5, "2", None, True])
def test_invalid_years_type_raises_type_error(calculator, bad_years):
    with pytest.raises(TypeError, match="Years must be an integer"):
        calculator.simple_interest(10000, 5, bad_years)


@pytest.mark.parametrize("bad_principal", ["10000", None, True])
def test_invalid_principal_type_raises_type_error(calculator, bad_principal):
    with pytest.raises(TypeError, match="Principal must be numeric"):
        calculator.simple_interest(bad_principal, 5, 1)


def test_invalid_rate_type_raises_type_error(calculator):
    with pytest.raises(TypeError, match="Annual rate must be numeric"):
        calculator.simple_interest(10000, "5", 1)


@pytest.mark.parametrize(
    "principal, rate, years",
    [
        (10000, 5, -1),   # just below the valid years boundary
        (-1, 5, 1),       # just below the valid principal boundary
        (10000, -1, 1),   # just below the valid rate boundary
    ],
)
def test_negative_values_raise_value_error(calculator, principal, rate, years):
    with pytest.raises(ValueError):
        calculator.simple_interest(principal, rate, years)


def test_negative_principal_message(calculator):
    with pytest.raises(ValueError, match="Principal cannot be negative"):
        calculator.simple_interest(-500, 5, 1)
