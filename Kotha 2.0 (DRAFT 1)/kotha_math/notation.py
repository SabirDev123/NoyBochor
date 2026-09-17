# Kotha 2.0
# Draft mathematical notation parser.
#
# Converts common human-written mathematical notation
# into a form that Kotha's math engines can understand.

import re


class MathNotation:
    def normalize(self, text):
        expression = text.strip()

        # Common mathematical symbols.
        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")
        expression = expression.replace("–", "-")
        expression = expression.replace("—", "-")

        # Powers.
        expression = expression.replace("²", "^2")
        expression = expression.replace("³", "^3")

        # Square-root symbol.
        expression = re.sub(
            r"√\s*([A-Za-z0-9]+)",
            r"sqrt(\1)",
            expression
        )

        # Remove common natural-language prefixes.
        prefixes = [
            r"^what\s+is\s+",
            r"^calculate\s+",
            r"^calculate:\s*",
            r"^solve\s*:\s*",
            r"^evaluate\s*:\s*",
        ]

        for pattern in prefixes:
            expression = re.sub(
                pattern,
                "",
                expression,
                flags=re.IGNORECASE
            )

        return expression.strip()

    def is_math(self, text):
        lowered = text.lower()

        math_symbols = (
            "+",
            "-",
            "*",
            "/",
            "×",
            "÷",
            "=",
            "^",
            "²",
            "³",
            "√",
            "∫",
        )

        math_words = (
            "calculate",
            "solve",
            "equation",
            "derivative",
            "differentiate",
            "integral",
            "integrate",
        )

        if any(symbol in text for symbol in math_symbols):
            return True

        return any(word in lowered for word in math_words)

    def is_algebra(self, expression):
        # Variables or equations usually indicate algebra.
        if "=" in expression:
            return True

        return bool(
            re.search(r"[0-9]\s*[a-zA-Z]", expression)
        )

    def is_calculus(self, expression):
        lowered = expression.lower()

        calculus_terms = (
            "derivative",
            "differentiate",
            "d/dx",
            "integral",
            "integrate",
            "limit",
            "∫",
        )

        return any(
            term in lowered
            for term in calculus_terms
        )