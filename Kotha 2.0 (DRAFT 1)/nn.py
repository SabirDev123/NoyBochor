# nn.py
# Kotha 2.0 neural network
#
# In-house implementation.
# No external ML framework required for the basic prototype.

import math
import random


class Neuron:
    def __init__(self, inputs):
        self.weights = [
            random.uniform(-0.1, 0.1)
            for _ in range(inputs)
        ]
        self.bias = random.uniform(-0.1, 0.1)

    def forward(self, values):
        total = self.bias

        for weight, value in zip(self.weights, values):
            total += weight * value

        return total


class Layer:
    def __init__(self, input_size, neuron_count):
        self.neurons = [
            Neuron(input_size)
            for _ in range(neuron_count)
        ]

    def forward(self, values):
        return [
            neuron.forward(values)
            for neuron in self.neurons
        ]


class NeuralNetwork:
    """
    Kotha 2.0 prototype architecture.

    Hidden layers:
        40
        40
        40
        40
        40
        40
        96

    The 96-neuron layer is intended to become
    Kotha's final refinement/polishing stage.
    """

    HIDDEN_LAYERS = [40, 40, 40, 40, 40, 40, 96]

    def __init__(self, input_size=32, output_size=32):
        self.input_size = input_size
        self.output_size = output_size

        self.layers = []

        previous_size = input_size

        for neuron_count in self.HIDDEN_LAYERS:
            self.layers.append(
                Layer(previous_size, neuron_count)
            )
            previous_size = neuron_count

        self.output_layer = Layer(
            previous_size,
            output_size
        )

    @staticmethod
    def activation(value):
        # ReLU
        return max(0.0, value)

    def forward(self, values):
        if len(values) != self.input_size:
            raise ValueError(
                f"Expected {self.input_size} inputs, "
                f"got {len(values)}."
            )

        current = values

        for layer in self.layers:
            current = [
                self.activation(value)
                for value in layer.forward(current)
            ]

        return self.output_layer.forward(current)

    def generate_response(self, text, personality="default", memory=None):
        """
        Placeholder response interface.

        The actual language model will eventually replace this.
        """

        if not text.strip():
            return "I need some input first."

        return (
            f"[Kotha 2.0 neural engine] "
            f"Input received: {text}"
        )