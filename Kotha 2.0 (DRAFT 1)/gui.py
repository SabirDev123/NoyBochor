# gui.py
# Kotha 2.0 GUI

import tkinter as tk
from tkinter import scrolledtext


class KothaGUI:
    def __init__(self, kotha):
        self.kotha = kotha

        self.root = tk.Tk()
        self.root.title("Kotha 2.0")
        self.root.geometry("900x600")
        self.root.minsize(600, 400)

        self._build_ui()

    def _build_ui(self):
        self.chat = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state="disabled",
            font=("Helvetica", 13)
        )
        self.chat.pack(
            fill=tk.BOTH,
            expand=True,
            padx=12,
            pady=(12, 6)
        )

        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=12, pady=(6, 12))

        self.entry = tk.Entry(
            bottom,
            font=("Helvetica", 13)
        )
        self.entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(0, 8)
        )

        self.entry.bind("<Return>", self.send)

        send_button = tk.Button(
            bottom,
            text="Send",
            command=self.send
        )
        send_button.pack(side=tk.RIGHT)

        self._write(
            "Kotha 2.0",
            "Kotha 2.0 is online. 🧠"
        )

    def _write(self, speaker, message):
        self.chat.configure(state="normal")
        self.chat.insert(
            tk.END,
            f"{speaker}: {message}\n\n"
        )
        self.chat.configure(state="disabled")
        self.chat.see(tk.END)

    def send(self, event=None):
        text = self.entry.get().strip()

        if not text:
            return

        self.entry.delete(0, tk.END)
        self._write("You", text)

        response = self.kotha.respond(text)
        self._write("Kotha", response)

    def run(self):
        self.entry.focus_set()
        self.root.mainloop()