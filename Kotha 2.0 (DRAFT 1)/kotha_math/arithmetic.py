# Kotha 2.0
# Draft arithmetic engine
# Exact arithmetic operations handled separately from the language engine.

import math
import ast
import operator


class ArithmeticEngine:
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv,
    }

    UNARY_OPERATORS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def calculate(self, expression):
        expression = self._clean(expression)

        try:
            tree = ast.parse(expression, mode="eval")
            return self._evaluate(tree.body)
        except Exception as error:
            return f"Arithmetic error: {error}"

    def _evaluate(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("Invalid number.")

        if isinstance(node, ast.BinOp):
            operation = self.OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported operator.")

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):
            operation = self.UNARY_OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported unary operator.")

            return operation(self._evaluate(node.operand))

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Invalid function.")

            name = node.func.id

            functions = {
                "sqrt": math.sqrt,
                "abs": abs,
                "floor": math.floor,
                "ceil": math.ceil,
            }

            if name not in functions:
                raise ValueError("Unsupported function.")

            arguments = [
                self._evaluate(argument)
                for argument in node.args
            ]

            return functions[name](*arguments)

        raise ValueError("Unsupported expression.")

    def _clean(self, expression):
        expression = expression.strip()

        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")
        expression = expression.replace("^", "**")

        return expression