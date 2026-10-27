import pytest
from app.interest import InterestCalculator


def test_zero_years_interest_is_zero():
    calculator = InterestCalculator()
    assert calculator.simple_interest(10000, 5, 0) == 0


def test_one_year_interest_is_correct():
    calculator = InterestCalculator()
    assert calculator.simple_interest(10000, 5, 1) == 500


def test_multiple_years_interest_is_correct():
    calculator = InterestCalculator()
    assert calculator.simple_interest(10000, 5, 3) == 1500


def test_negative_principal_raises_value_error():
    calculator = InterestCalculator()
    with pytest.raises(ValueError):
        calculator.simple_interest(-10000, 5, 1)


def test_negative_years_raises_value_error():
    calculator = InterestCalculator()
    with pytest.raises(ValueError):
        calculator.simple_interest(10000, 5, -1)


def test_non_integer_years_raises_type_error():
    calculator = InterestCalculator()
    with pytest.raises(TypeError):
        calculator.simple_interest(10000, 5, 1.5)
