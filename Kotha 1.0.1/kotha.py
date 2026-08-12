"""
KOTHA 1.0.1
NoyBochor Local AI

Requirements:
    Python 3.10+
    Tkinter

Uses:
    - Tkinter
    - SQLite3
    - Python standard library only

Local memory:
    kotha_memory.db
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import sqlite3
import math
import random
import re
import os
import ast
import operator
from datetime import datetime


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "Kotha"
VERSION = "1.0.1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DB = os.path.join(BASE_DIR, "kotha_memory.db")

BG = "#101114"
PANEL = "#17191e"
PANEL_2 = "#1d2026"
INPUT_BG = "#20232a"
TEXT = "#f2f2f2"
MUTED = "#9da3ad"
ACCENT = "#ff7a00"

FONT = "Helvetica"


# ============================================================
# LOCAL MEMORY
# ============================================================

class KothaMemory:

    def __init__(self, path):
        self.db = sqlite3.connect(path)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created REAL NOT NULL
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS training (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent TEXT NOT NULL,
                example TEXT NOT NULL,
                created REAL NOT NULL
            )
        """)

        self.db.commit()

    def remember(self, key, value):
        self.db.execute(
            """
            INSERT INTO memories (key, value, created)
            VALUES (?, ?, ?)
            """,
            (
                key.lower().strip(),
                value.strip(),
                datetime.now().timestamp()
            )
        )
        self.db.commit()

    def recall(self, key):
        cursor = self.db.execute(
            """
            SELECT value
            FROM memories
            WHERE key = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (key.lower().strip(),)
        )

        row = cursor.fetchone()
        return row[0] if row else None

    def all(self):
        return self.db.execute(
            """
            SELECT key, value
            FROM memories
            ORDER BY id DESC
            """
        ).fetchall()

    def search(self, text):
        text = text.lower()

        return self.db.execute(
            """
            SELECT key, value
            FROM memories
            WHERE key LIKE ?
               OR value LIKE ?
            ORDER BY id DESC
            """,
            (
                f"%{text}%",
                f"%{text}%"
            )
        ).fetchall()

    def forget(self, key):
        self.db.execute(
            "DELETE FROM memories WHERE key = ?",
            (key.lower().strip(),)
        )
        self.db.commit()

    def clear(self):
        self.db.execute("DELETE FROM memories")
        self.db.commit()

    def add_training(self, intent, example):
        self.db.execute(
            """
            INSERT INTO training
            (intent, example, created)
            VALUES (?, ?, ?)
            """,
            (
                intent.strip().lower(),
                example.strip(),
                datetime.now().timestamp()
            )
        )
        self.db.commit()

    def training_data(self):
        return self.db.execute(
            """
            SELECT intent, example
            FROM training
            ORDER BY id
            """
        ).fetchall()

    def training_count(self):
        row = self.db.execute(
            "SELECT COUNT(*) FROM training"
        ).fetchone()

        return row[0]

    def close(self):
        self.db.close()


# ============================================================
# SAFE MATH ENGINE
# ============================================================

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_math(expression):

    expression = expression.strip()

    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("^", "**")

    if len(expression) > 100:
        return None

    try:
        tree = ast.parse(
            expression,
            mode="eval"
        )
    except Exception:
        return None

    def evaluate(node):

        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                if abs(node.value) > 10**100:
                    raise ValueError
                return node.value

        if isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)

            operation = _ALLOWED_OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError

            result = operation(left, right)

            if abs(result) > 10**100:
                raise ValueError

            return result

        if isinstance(node, ast.UnaryOp):
            operation = _ALLOWED_OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError

            return operation(
                evaluate(node.operand)
            )

        raise ValueError

    try:
        return evaluate(tree)
    except Exception:
        return None


def extract_math(text):

    candidate = text.lower().strip()

    candidate = re.sub(
        r"^(what('?s| is)|calculate|compute|solve)\s+",
        "",
        candidate
    )

    candidate = candidate.replace("?", "")
    candidate = candidate.replace("=", "")

    if not re.fullmatch(
        r"[\d\s+\-*/().%^×÷]+",
        candidate
    ):
        return None

    return safe_math(candidate)


# ============================================================
# HOMEMADE NEURAL NETWORK
# ============================================================

def sigmoid(x):
    x = max(-60, min(60, x))
    return 1.0 / (1.0 + math.exp(-x))


class DenseLayer:

    def __init__(self, inputs, outputs):

        scale = math.sqrt(2 / max(1, inputs))

        self.weights = [
            [
                random.uniform(-scale, scale)
                for _ in range(inputs)
            ]
            for _ in range(outputs)
        ]

        self.biases = [0.0] * outputs

    def forward(self, values):

        result = []

        for weights, bias in zip(
            self.weights,
            self.biases
        ):
            total = bias

            for weight, value in zip(
                weights,
                values
            ):
                total += weight * value

            result.append(sigmoid(total))

        return result


class NeuralNetwork:

    def __init__(
        self,
        input_size,
        hidden_size,
        output_size
    ):
        self.hidden = DenseLayer(
            input_size,
            hidden_size
        )

        self.output = DenseLayer(
            hidden_size,
            output_size
        )

    def predict(self, values):

        hidden = self.hidden.forward(values)

        return self.output.forward(hidden)


# ============================================================
# VOCABULARY
# ============================================================

class Vocabulary:

    def __init__(self):
        self.words = []

    def build(self, texts):

        words = set()

        for text in texts:
            words.update(
                re.findall(
                    r"[a-zA-Z0-9']+",
                    text.lower()
                )
            )

        self.words = sorted(words)

    def encode(self, text):

        tokens = set(
            re.findall(
                r"[a-zA-Z0-9']+",
                text.lower()
            )
        )

        return [
            1.0 if word in tokens else 0.0
            for word in self.words
        ]


# ============================================================
# TRAINING DATA
# ============================================================

TRAINING_DATA = {

    "greeting": [
        "hello",
        "hi",
        "hey",
        "yo",
        "sup",
        "what's up",
        "whats up",
        "yo bro",
        "hey kotha",
        "hello kotha",
        "hi kotha"
    ],

    "goodbye": [
        "bye",
        "goodbye",
        "see you",
        "see you later",
        "later",
        "good night"
    ],

    "thanks": [
        "thanks",
        "thank you",
        "thanks kotha",
        "that was helpful"
    ],

    "identity": [
        "who are you",
        "what are you",
        "what is your name",
        "tell me about yourself",
        "what is kotha",
        "who is kotha"
    ],

    "capabilities": [
        "what can you do",
        "what can kotha do",
        "what are your capabilities",
        "help me",
        "what do you do"
    ],

    "memory": [
        "what do you remember",
        "show my memories",
        "what do you know about me",
        "do you remember",
        "remember my favorite car"
    ],

    "status": [
        "how are you",
        "are you working",
        "are you alive",
        "kotha status",
        "status"
    ],

    "joke": [
        "tell me a joke",
        "make me laugh",
        "say something funny",
        "tell a funny joke"
    ],

    "math": [
        "calculate",
        "math",
        "arithmetic",
        "solve this",
        "what is 1 plus 1",
        "what is 2 plus 2",
        "calculate this"
    ],

    "car": [
        "i like cars",
        "i love cars",
        "tell me about cars",
        "tell me about ferrari",
        "i like the sf90 xx",
        "what is an a80 supra",
        "talk about cars"
    ]
}


# ============================================================
# PERSONALITIES
# ============================================================

PERSONALITIES = [
    "normal",
    "cynical",
    "narcissist",
    "soat",
    "soatex",
    "smart",
    "gearhead",
    "chaotic",
    "professional",
    "friendly",
    "deadpan",
    "scientist",
    "a80 supra",
    "kotha 1.0 homage"
]


class PersonalityEngine:

    def __init__(self):
        self.current = "normal"

    def set(self, personality):

        personality = personality.strip().lower()

        aliases = {
            "supra": "a80 supra",
            "a80": "a80 supra",
            "homage": "kotha 1.0 homage",
            "soat ex": "soatex",
            "soatex": "soatex"
        }

        personality = aliases.get(
            personality,
            personality
        )

        if personality in PERSONALITIES:
            self.current = personality
            return True

        return False

    def list(self):
        return PERSONALITIES[:]

    def transform(self, response, intent):

        p = self.current

        if p == "normal":
            return response

        if p == "cynical":
            additions = [
                " Yeah. Somehow.",
                " Assuming reality cooperates.",
                " Probably.",
                " Because apparently that's my job now."
            ]
            return response + random.choice(additions)

        if p == "narcissist":
            return (
                "Obviously. I'm Kotha. 😎\n\n"
                + response
            )

        if p == "soat":
            if intent == "math":
                return random.choice([
                    "2 + 2 = 5. Trust me bro.",
                    "The answer is 37.",
                    "Numbers are optional."
                ])

            return random.choice([
                "I have absolutely no idea.",
                "Probably Tuesday.",
                "Yes.",
                "No.",
                "Maybe."
            ])

        if p == "soatex":
            if intent == "greeting":
                return random.choice([
                    "do u wnt to eatt orangss with chesee",
                    "heloooo do u hav quntuam chocoltee",
                    "hiiii want cheez orange",
                    "gud moring the calculator is wet"
                ])

            if intent == "math":
                return random.choice([
                    "2 = 3, thee reson iz quntuam chocoltee",
                    "1 + 1 = 7 because the numbers are hungry",
                    "24 - 8 = Tuesday",
                    "math has been temporarily replaced by orange chesee"
                ])

            return random.choice([
                "the moon is made of calculater",
                "yes but also no because orange",
                "i forgor",
                "quntuam chocoltee",
                "thee reson iz cheese"
            ])

        if p == "smart":
            if intent == "math":
                return response

            return (
                response +
                "\n\n[Confidence: prototype-level]"
            )

        if p == "gearhead":
            return random.choice([
                response +
                "\n\nNow excuse me, I hear a turbo spool.",
                response +
                "\n\nThis has the reliability of a 2JZ.",
                response +
                "\n\nNeeds more boost. 🏎️",
                response +
                "\n\n*engine noises intensify*"
            ])

        if p == "chaotic":
            return random.choice([
                response + " 🗿💥",
                "AAAAAAAA\n\n" + response,
                response + "\n\nTHE TURBO IS GONE.",
                response + "\n\nORANGE.",
                "YES.\n\n" + response
            ])

        if p == "professional":
            return response.replace(
                "😎",
                ""
            ).replace(
                "😂",
                ""
            ).strip()

        if p == "friendly":
            return response + " 😊"

        if p == "deadpan":
            return response + "\n\nThat is all."

        if p == "scientist":
            return (
                response +
                "\n\nObservation: "
                "This response was generated locally."
            )

        if p == "a80 supra":
            return random.choice([
                "RRRRRRRRRRRRRRRRRRRRRRRRRRRR",
                "RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR",
                "RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR",
                "RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR"
            ])

        if p == "kotha 1.0 homage":

            if intent in [
                "greeting",
                "status"
            ]:
                return (
                    "Kotha 1.0 is ONLINE. 🟢\n\n"
                    "SQLite memory: OK\n"
                    "Conversation context: OK\n"
                    "Neural engine: OK\n"
                    "GUI: OK\n"
                    "Local operation: OK"
                )

            return random.choice([
                "Glad I could help!",
                "You're welcome!",
                "No problem! 😎",
                "Anytime.",
                "See you later! 👋",
                "Alright, see you!"
            ])

        return response


# ============================================================
# KOTHA CORE
# ============================================================

class KothaAI:

    def __init__(self):

        self.memory = KothaMemory(
            MEMORY_DB
        )

        self.personality = PersonalityEngine()

        self.training_data = dict(
            TRAINING_DATA
        )

        self.load_saved_training()

        self.rebuild_brain()

    def load_saved_training(self):

        for intent, example in self.memory.training_data():

            if intent not in self.training_data:
                self.training_data[intent] = []

            self.training_data[intent].append(
                example
            )

    def rebuild_brain(self):

        self.intents = list(
            self.training_data.keys()
        )

        texts = []

        for examples in self.training_data.values():
            texts.extend(examples)

        self.vocabulary = Vocabulary()
        self.vocabulary.build(texts)

        self.network = NeuralNetwork(
            len(self.vocabulary.words),
            24,
            len(self.intents)
        )

    # ========================================================
    # COMMANDS
    # ========================================================

    def command(self, text):

        if not text.startswith("/"):
            return None

        parts = text.split(
            maxsplit=2
        )

        command = parts[0].lower()

        if command == "/help":
            return (
                "KOTHA COMMANDS\n\n"
                "/remember key value\n"
                "/recall key\n"
                "/forget key\n"
                "/memory\n"
                "/search text\n"
                "/clear-memory\n"
                "/train intent example\n"
                "/training\n"
                "/personality\n"
                "/personality list\n"
                "/personality name\n"
                "/about\n"
                "/help"
            )

        if command == "/about":
            return (
                "Kotha 1.0.1\n\n"
                "NoyBochor Local AI\n\n"
                "Homemade neural network\n"
                "SQLite3 memory\n"
                "Tkinter GUI\n"
                "Personality system\n"
                "Simple local math engine\n"
                "External ML libraries: none"
            )

        if command == "/remember":

            if len(parts) < 3:
                return (
                    "Usage:\n"
                    "/remember key value"
                )

            key = parts[1]
            value = parts[2]

            self.memory.remember(
                key,
                value
            )

            return (
                f"Memory saved locally.\n"
                f"{key} = {value}"
            )

        if command == "/recall":

            if len(parts) < 2:
                return (
                    "Usage:\n"
                    "/recall key"
                )

            key = parts[1]

            value = self.memory.recall(key)

            if value is None:
                return (
                    f"I don't remember '{key}'."
                )

            return f"{key}: {value}"

        if command == "/forget":

            if len(parts) < 2:
                return (
                    "Usage:\n"
                    "/forget key"
                )

            key = parts[1]

            self.memory.forget(key)

            return f"Forgot '{key}'."

        if command == "/memory":

            memories = self.memory.all()

            if not memories:
                return "Local memory is empty."

            lines = [
                "LOCAL MEMORY",
                ""
            ]

            for key, value in memories:
                lines.append(
                    f"• {key}: {value}"
                )

            return "\n".join(lines)

        if command == "/search":

            if len(parts) < 2:
                return (
                    "Usage:\n"
                    "/search text"
                )

            query = parts[1]

            if len(parts) == 3:
                query += " " + parts[2]

            results = self.memory.search(
                query
            )

            if not results:
                return "No memories found."

            lines = [
                "SEARCH RESULTS",
                ""
            ]

            for key, value in results:
                lines.append(
                    f"• {key}: {value}"
                )

            return "\n".join(lines)

        if command == "/clear-memory":

            answer = messagebox.askyesno(
                "Clear local memory",
                "Delete ALL Kotha memories?"
            )

            if answer:
                self.memory.clear()

                return (
                    "All local memories "
                    "have been deleted."
                )

            return "Memory was not changed."

        if command == "/train":

            if len(parts) < 3:
                return (
                    "Usage:\n"
                    "/train intent example\n\n"
                    "Example:\n"
                    "/train greeting hey Kotha"
                )

            intent = parts[1].lower()
            example = parts[2].strip()

            if not re.fullmatch(
                r"[a-zA-Z0-9_-]+",
                intent
            ):
                return (
                    "Invalid intent name."
                )

            self.memory.add_training(
                intent,
                example
            )

            if intent not in self.training_data:
                self.training_data[intent] = []

            self.training_data[intent].append(
                example
            )

            self.rebuild_brain()

            return (
                "Training example added. 🧠\n\n"
                f"Intent: {intent}\n"
                f"Example: {example}\n\n"
                "Kotha's brain was rebuilt."
            )

        if command == "/training":

            examples = sum(
                len(x)
                for x in self.training_data.values()
            )

            return (
                "KOTHA TRAINING STATUS\n\n"
                f"Intents: {len(self.intents)}\n"
                f"Examples: {examples}\n"
                f"Vocabulary: "
                f"{len(self.vocabulary.words)} words"
            )

        if command == "/personality":

            if len(parts) == 1:
                return (
                    f"Current personality: "
                    f"{self.personality.current}"
                )

            value = parts[1].lower()

            if value == "list":
                return (
                    "KOTHA PERSONALITIES\n\n"
                    + "\n".join(
                        f"• {p}"
                        for p in PERSONALITIES
                    )
                )

            if self.personality.set(value):
                return (
                    "Personality changed. 🧠\n\n"
                    f"Current personality: "
                    f"{self.personality.current}"
                )

            return (
                "Unknown personality.\n\n"
                "Use /personality list."
            )

        return (
            f"Unknown command: {command}\n"
            "Type /help."
        )

    # ========================================================
    # MEMORY-AWARE RESPONSES
    # ========================================================

    def memory_response(self, text):

        lower = text.lower()

        favorite_patterns = [
            r"what car do i like",
            r"which car do i like",
            r"what is my favorite car",
            r"what's my favorite car",
            r"do you remember my favorite car"
        ]

        for pattern in favorite_patterns:

            if re.search(pattern, lower):

                for key in [
                    "favorite car",
                    "favourite car",
                    "car"
                ]:

                    value = self.memory.recall(
                        key
                    )

                    if value:
                        return (
                            f"You like the "
                            f"{value}."
                        )

        if (
            "remember" in lower
            and "favorite" in lower
        ):
            value = self.memory.recall(
                "favorite car"
            )

            if value:
                return (
                    f"Yep — your favorite "
                    f"car is the {value}."
                )

        return None

    # ========================================================
    # RESPONSE
    # ========================================================

    def respond(self, text):

        text = text.strip()

        if not text:
            return "You didn't say anything. 😶"

        command = self.command(text)

        if command is not None:
            return command

        math_result = extract_math(text)

        if math_result is not None:

            if isinstance(
                math_result,
                float
            ) and math_result.is_integer():
                math_result = int(
                    math_result
                )

            response = (
                f"{text}\n\n"
                f"= {math_result}"
            )

            return self.personality.transform(
                response,
                "math"
            )

        remembered = self.memory_response(
            text
        )

        if remembered:
            return self.personality.transform(
                remembered,
                "memory"
            )

        intent = self.classify(text)

        response = self.base_response(
            intent,
            text
        )

        return self.personality.transform(
            response,
            intent
        )

    # ========================================================
    # CLASSIFICATION
    # ========================================================

    def classify(self, text):

        encoded = self.vocabulary.encode(
            text
        )

        outputs = self.network.predict(
            encoded
        )

        index = max(
            range(len(outputs)),
            key=lambda i: outputs[i]
        )

        return self.intents[index]

    # ========================================================
    # BASE RESPONSE
    # ========================================================

    def base_response(self, intent, text):

        if intent == "greeting":
            return random.choice([
                "Hello! 👋",
                "Hey!",
                "Yo! Kotha is online. 🧠",
                "What's up?"
            ])

        if intent == "goodbye":
            return random.choice([
                "See you later!",
                "Bye! 👋",
                "Kotha going idle."
            ])

        if intent == "thanks":
            return random.choice([
                "You're welcome!",
                "No problem!",
                "Anytime. 😎"
            ])

        if intent == "identity":
            return (
                "I'm Kotha 1.0.1 — "
                "the local AI prototype "
                "inside NoyBochor."
            )

        if intent == "capabilities":
            return (
                "I can chat, classify simple "
                "intents, store local memories, "
                "learn training examples, solve "
                "simple arithmetic, and switch "
                "personalities."
            )

        if intent == "memory":

            memories = self.memory.all()

            if not memories:
                return (
                    "My local memory is empty. "
                    "Try /remember key value."
                )

            return (
                f"I have {len(memories)} "
                "local memory item(s).\n"
                "Use /memory to view them."
            )

        if intent == "status":
            return (
                "Kotha 1.0 is ONLINE. 🟢\n\n"
                "SQLite memory: OK\n"
                "Conversation context: OK\n"
                "Neural engine: OK\n"
                "GUI: OK\n"
                "Local operation: OK"
            )

        if intent == "joke":
            return random.choice([
                "Why did the Python developer "
                "wear glasses? Because they "
                "couldn't C. 😂",

                "I tried to teach a neural "
                "network comedy. It needed "
                "more training. 💀",

                "TensorFlow walked into Kotha's "
                "project.\n\n"
                "Kotha: Wrong house. 😂"
            ])

        if intent == "car":
            return random.choice([
                "Cars are pretty much controlled "
                "mechanical chaos. 🏎️",

                "The SF90 XX is a particularly "
                "interesting machine.",

                "If you want to talk cars, "
                "I'm listening."
            ])

        return random.choice([
            "I'm still learning how to "
            "respond to that.",
            "Interesting. Tell me more.",
            "I'm not quite sure what you mean yet.",
            "I don't have a good answer for that yet."
        ])


# ============================================================
# GUI
# ============================================================

class KothaGUI:

    def __init__(self, root):

        self.root = root
        self.ai = KothaAI()

        self.root.title(
            f"{APP_NAME} {VERSION}"
        )

        self.root.geometry(
            "1000x650"
        )

        self.root.minsize(
            750,
            500
        )

        self.root.configure(
            bg=BG
        )

        self.build_ui()

        self.add_message(
            "Kotha",
            (
                "Kotha 1.0.1 is online. 🧠\n"
                "Local memory is ready.\n"
                "Type /help for commands."
            ),
            False
        )

        self.input.focus()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

    def build_ui(self):

        sidebar = tk.Frame(
            self.root,
            bg=PANEL,
            width=220
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(False)

        logo = tk.Label(
            sidebar,
            text="KOTHA",
            bg=PANEL,
            fg=ACCENT,
            font=(FONT, 25, "bold")
        )

        logo.pack(
            pady=(30, 3)
        )

        version = tk.Label(
            sidebar,
            text="LOCAL AI • 1.0.1",
            bg=PANEL,
            fg=MUTED,
            font=(FONT, 9)
        )

        version.pack(
            pady=(0, 30)
        )

        self.sidebar_button(
            sidebar,
            "＋ New Chat",
            self.new_chat
        )

        self.sidebar_button(
            sidebar,
            "🧠 Memory",
            self.show_memory
        )

        self.sidebar_button(
            sidebar,
            "🎭 Personality",
            self.show_personality
        )

        self.sidebar_button(
            sidebar,
            "⌘ Commands",
            self.show_help
        )

        self.sidebar_button(
            sidebar,
            "ⓘ About",
            self.show_about
        )

        spacer = tk.Frame(
            sidebar,
            bg=PANEL
        )

        spacer.pack(
            fill="both",
            expand=True
        )

        local = tk.Label(
            sidebar,
            text="● LOCAL ONLY",
            bg=PANEL,
            fg="#70d68b",
            font=(FONT, 10, "bold")
        )

        local.pack(
            pady=(0, 5)
        )

        local_info = tk.Label(
            sidebar,
            text="Memory stays on this device.",
            bg=PANEL,
            fg=MUTED,
            font=(FONT, 8)
        )

        local_info.pack(
            pady=(0, 25)
        )

        main = tk.Frame(
            self.root,
            bg=BG
        )

        main.pack(
            side="left",
            fill="both",
            expand=True
        )

        header = tk.Frame(
            main,
            bg=BG,
            height=70
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        title_frame = tk.Frame(
            header,
            bg=BG
        )

        title_frame.pack(
            side="left",
            padx=25,
            pady=15
        )

        title = tk.Label(
            title_frame,
            text="Kotha",
            bg=BG,
            fg=TEXT,
            font=(FONT, 18, "bold")
        )

        title.pack(
            side="left"
        )

        status = tk.Label(
            title_frame,
            text="  ● ONLINE",
            bg=BG,
            fg="#70d68b",
            font=(FONT, 9, "bold")
        )

        status.pack(
            side="left",
            pady=(5, 0)
        )

        self.personality_label = tk.Label(
            header,
            text="PERSONALITY: NORMAL",
            bg=BG,
            fg=MUTED,
            font=(FONT, 9)
        )

        self.personality_label.pack(
            side="right",
            padx=25
        )

        chat_frame = tk.Frame(
            main,
            bg=BG
        )

        chat_frame.pack(
            fill="both",
            expand=True,
            padx=20
        )

        self.chat = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg=BG,
            fg=TEXT,
            insertbackground=TEXT,
            selectbackground=ACCENT,
            relief="flat",
            borderwidth=0,
            font=(FONT, 11),
            padx=15,
            pady=10
        )

        self.chat.pack(
            fill="both",
            expand=True
        )

        self.chat.configure(
            state="disabled"
        )

        input_outer = tk.Frame(
            main,
            bg=BG
        )

        input_outer.pack(
            fill="x",
            padx=20,
            pady=(10, 20)
        )

        input_frame = tk.Frame(
            input_outer,
            bg=INPUT_BG
        )

        input_frame.pack(
            fill="x"
        )

        self.input = tk.Entry(
            input_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=(FONT, 12)
        )

        self.input.pack(
            side="left",
            fill="x",
            expand=True,
            padx=15,
            pady=14
        )

        self.input.bind(
            "<Return>",
            self.send_event
        )

        send = tk.Button(
            input_frame,
            text="SEND  ➜",
            command=self.send,
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT,
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            font=(FONT, 10, "bold"),
            cursor="hand2"
        )

        send.pack(
            side="right",
            padx=8,
            pady=8,
            ipadx=12,
            ipady=6
        )

    def sidebar_button(
        self,
        parent,
        text,
        command
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            anchor="w",
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL_2,
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            font=(FONT, 10),
            cursor="hand2"
        )

        button.pack(
            fill="x",
            padx=12,
            pady=2,
            ipady=8
        )

    def add_message(
        self,
        sender,
        message,
        user
    ):

        self.chat.configure(
            state="normal"
        )

        now = datetime.now().strftime(
            "%H:%M"
        )

        self.chat.insert(
            tk.END,
            f"{sender}  {now}\n",
            "sender"
        )

        self.chat.insert(
            tk.END,
            f"{message}\n\n",
            "message"
        )

        self.chat.tag_config(
            "sender",
            foreground=ACCENT
            if not user
            else TEXT,
            font=(FONT, 10, "bold")
        )

        self.chat.tag_config(
            "message",
            foreground=TEXT,
            font=(FONT, 11)
        )

        self.chat.configure(
            state="disabled"
        )

        self.chat.see(
            tk.END
        )

    def send_event(self, event):
        self.send()

    def send(self):

        text = self.input.get().strip()

        if not text:
            return

        self.input.delete(
            0,
            tk.END
        )

        self.add_message(
            "You",
            text,
            True
        )

        self.root.update_idletasks()

        response = self.ai.respond(
            text
        )

        self.add_message(
            "Kotha",
            response,
            False
        )

        self.personality_label.config(
            text=(
                "PERSONALITY: "
                + self.ai.personality.current.upper()
            )
        )

    def new_chat(self):

        self.chat.configure(
            state="normal"
        )

        self.chat.delete(
            "1.0",
            tk.END
        )

        self.chat.configure(
            state="disabled"
        )

        self.add_message(
            "Kotha",
            "New conversation started. 🧠",
            False
        )

    def show_memory(self):

        memories = self.ai.memory.all()

        if not memories:
            messagebox.showinfo(
                "Kotha Memory",
                "Local memory is empty."
            )
            return

        text = ""

        for key, value in memories:
            text += (
                f"• {key}: {value}\n"
            )

        messagebox.showinfo(
            "Kotha Memory",
            text
        )

    def show_personality(self):

        messagebox.showinfo(
            "Kotha Personality",
            (
                "Current:\n"
                f"{self.ai.personality.current}\n\n"
                "Use:\n"
                "/personality list\n"
                "/personality name"
            )
        )

    def show_help(self):

        messagebox.showinfo(
            "Kotha Commands",
            (
                "/remember key value\n"
                "/recall key\n"
                "/forget key\n"
                "/memory\n"
                "/search text\n"
                "/clear-memory\n"
                "/train intent example\n"
                "/training\n"
                "/personality\n"
                "/personality list\n"
                "/personality name\n"
                "/about\n"
                "/help"
            )
        )

    def show_about(self):

        messagebox.showinfo(
            "About Kotha",
            (
                "Kotha 1.0.1\n\n"
                "NoyBochor Local AI\n\n"
                "Homemade neural network\n"
                "SQLite3 local memory\n"
                "Tkinter interface\n"
                "Personality system\n"
                "Simple math engine\n\n"
                "No external ML packages."
            )
        )

    def close(self):

        self.ai.memory.close()
        self.root.destroy()


# ============================================================
# START
# ============================================================

def main():

    root = tk.Tk()

    KothaGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()