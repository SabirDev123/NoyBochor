# Kotha 2.0
# Draft calculus engine
# Basic symbolic calculus foundation.

import re


class CalculusEngine:
    def solve(self, expression):
        expression = expression.strip()

        if self._looks_like_derivative(expression):
            return self.derivative(expression)

        if self._looks_like_integral(expression):
            return self.integral(expression)

        return "I can't solve this calculus expression yet."

    def derivative(self, expression):
        expression = expression.strip()

        # Basic power rule:
        # d/dx (x^n) = n*x^(n-1)

        match = re.fullmatch(
            r"(?:d/dx\s*)?x\^(\d+)",
            expression.replace(" ", "")
        )

        if match:
            power = int(match.group(1))

            if power == 0:
                return "0"

            new_power = power - 1

            if new_power == 0:
                return str(power)

            if new_power == 1:
                return f"{power}x"

            return f"{power}x^{new_power}"

        if expression.replace(" ", "") in ("d/dxx", "derivativeofx"):
            return "1"

        return "Derivative not supported in this draft."

    def integral(self, expression):
        expression = expression.strip()

        # Basic power rule:
        # ∫x^n dx = x^(n+1)/(n+1)

        match = re.fullmatch(
            r"(?:∫|integrate\s*)x\^(\d+)(?:dx)?",
            expression.replace(" ", "")
        )

        if match:
            power = int(match.group(1))
            new_power = power + 1

            return f"x^{new_power}/{new_power} + C"

        return "Integral not supported in this draft."

    def _looks_like_derivative(self, expression):
        lowered = expression.lower()

        return (
            "derivative" in lowered
            or "d/dx" in lowered
            or lowered.startswith("differentiate")
        )

    def _looks_like_integral(self, expression):
        lowered = expression.lower()

        return (
            "integral" in lowered
            or "integrate" in lowered
            or expression.strip().startswith("∫")
        )