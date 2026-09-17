# ml.py
# Kotha 2.0 machine-learning system
#
# Training infrastructure for the in-house neural network.

import random


class TrainingExample:
    def __init__(self, inputs, targets):
        self.inputs = inputs
        self.targets = targets


class MLTrainer:
    def __init__(self, network):
        self.network = network
        self.dataset = []
        self.epochs_completed = 0

    def add_example(self, inputs, targets):
        self.dataset.append(
            TrainingExample(inputs, targets)
        )

    def dataset_size(self):
        return len(self.dataset)

    def status(self):
        return (
            "Kotha 2.0 ML system\n"
            f"Training examples: {len(self.dataset)}\n"
            f"Epochs completed: {self.epochs_completed}"
        )

    def train(self, epochs=1):
        """
        Training loop foundation.

        Backpropagation will be implemented here as
        the neural-network training system develops.
        """

        if not self.dataset:
            return "No training data available."

        for _ in range(epochs):
            examples = self.dataset[:]
            random.shuffle(examples)

            for example in examples:
                # Forward pass currently available.
                self.network.forward(example.inputs)

                # Backpropagation/update step:
                # TODO: implement gradients and weight updates.

            self.epochs_completed += 1

        return (
            f"Training complete. "
            f"Epochs completed: {self.epochs_completed}"
        )