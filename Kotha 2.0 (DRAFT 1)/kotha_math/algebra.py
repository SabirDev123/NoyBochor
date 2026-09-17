# Kotha 2.0
# Draft algebra engine
# Symbolic algebra will become much more capable in later revisions.

import re


class AlgebraEngine:
    def solve(self, expression):
        expression = expression.strip()

        # Basic linear equation:
        # ax + b = c

        match = re.fullmatch(
            r"([+-]?\d*\.?\d*)x\s*([+-]\s*\d*\.?\d*)?\s*=\s*([+-]?\d*\.?\d*)",
            expression.replace(" ", "")
        )

        if match:
            a_text, b_text, c_text = match.groups()

            a = self._coefficient(a_text)
            b = float(b_text) if b_text else 0
            c = float(c_text)

            if a == 0:
                return "No unique solution."

            x = (c - b) / a

            return self._format_solution(x)

        return "I can't solve this algebraic expression yet."

    def _coefficient(self, value):
        if value in ("", "+"):
            return 1.0

        if value == "-":
            return -1.0

        return float(value)

    def _format_solution(self, value):
        if value.is_integer():
            return f"x = {int(value)}"

        return f"x = {value}"