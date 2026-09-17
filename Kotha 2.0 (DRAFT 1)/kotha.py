# Kotha 2.0
# Main program

from gui import KothaGUI
from memory import Memory
from nn import NeuralNetwork
from ml import MLTrainer

# NOTE FOR FUTURE DEVELOPERS:
#
# The original draft used:
#
# from math.arithmetic import ArithmeticEngine
# from math.algebra import AlgebraEngine
# from math.calculus import CalculusEngine
# from math.notation import MathNotation
#
# This DOES NOT WORK because Python already has a standard-library
# module named "math". Python finds that module instead of our local
# "math" directory and reports:
#
# ModuleNotFoundError:
# No module named 'math.arithmetic'; 'math' is not a package
#
# The in-house math package was therefore renamed to "kotha_math".
#
# Current imports:

from kotha_math.arithmetic import ArithmeticEngine
from kotha_math.algebra import AlgebraEngine
from kotha_math.calculus import CalculusEngine
from kotha_math.notation import MathNotation


class Kotha:
    VERSION = "2.0"

    def __init__(self):
        self.memory = Memory()
        self.nn = NeuralNetwork()
        self.ml = MLTrainer(self.nn)

        self.arithmetic = ArithmeticEngine()
        self.algebra = AlgebraEngine()
        self.calculus = CalculusEngine()
        self.notation = MathNotation()

        self.personality = "default"
        self.flipped = False

    def process_command(self, text):
        command = text.strip().lower()

        if command == "/help":
            return self.help()

        if command == "/fts":
            self.flipped = not self.flipped

            if self.flipped:
                return "🔄 Switch flipped. You are now Kotha."
            return "🔄 Switch flipped back. You are now the human."

        if command.startswith("/personality"):
            parts = text.split(maxsplit=1)

            if len(parts) < 2:
                return f"Current personality: {self.personality}"

            self.personality = parts[1].strip().lower()
            return f"Personality changed. 🧠\n\nCurrent personality: {self.personality}"

        if command == "/training":
            return self.ml.status()

        return None

    def help(self):
        return (
            "Kotha 2.0 commands:\n\n"
            "/help\n"
            "/fts\n"
            "/personality <name>\n"
            "/training"
        )

    def respond(self, text):
        command_response = self.process_command(text)

        if command_response is not None:
            return command_response

        # Mathematics gets handled by specialized engines.
        if self.notation.is_math(text):
            expression = self.notation.normalize(text)

            if self.notation.is_algebra(expression):
                return self.algebra.solve(expression)

            if self.notation.is_calculus(expression):
                return self.calculus.solve(expression)

            return self.arithmetic.calculate(expression)

        # Normal language goes through Kotha's neural/language system.
        return self.nn.generate_response(
            text,
            personality=self.personality,
            memory=self.memory
        )


def main():
    kotha = Kotha()
    gui = KothaGUI(kotha)

    gui.run()


if __name__ == "__main__":
    main()