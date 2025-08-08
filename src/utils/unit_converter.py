"""
Unit Converter
Handles conversions between common kitchen units.
"""

from typing import Optional


class UnitConverter:
    CONVERSION_RATES = {
        ("cups", "ml"): 240,
        ("tbsp", "ml"): 15,
        ("tsp", "ml"): 5,
        ("oz", "g"): 28.35,
        ("lb", "g"): 453.6,
        ("kg", "g"): 1000,
        ("l", "ml"): 1000
    }

    def convert(self, amount: float, from_unit: str, to_unit: str) -> Optional[float]:
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()

        key = (from_unit, to_unit)
        if key in self.CONVERSION_RATES:
            return round(amount * self.CONVERSION_RATES[key], 2)

        reverse_key = (to_unit, from_unit)
        if reverse_key in self.CONVERSION_RATES:
            return round(amount / self.CONVERSION_RATES[reverse_key], 2)

        return None
