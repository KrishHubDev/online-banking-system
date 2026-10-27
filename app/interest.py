class InterestCalculator:
    """Calculate simple interest for a deposit or loan."""

    def simple_interest(self, principal, annual_rate, years):
        """Return simple interest = principal x rate x years / 100."""
        if isinstance(years, bool) or not isinstance(years, int):
            raise TypeError("Years must be an integer")
        if years < 0:
            raise ValueError("Years cannot be negative")
        for name, value in (("Principal", principal), ("Annual rate", annual_rate)):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric")
            if value < 0:
                raise ValueError(f"{name} cannot be negative")
        if years == 0:
            return 0
        return round(principal * annual_rate * years / 100, 2)
