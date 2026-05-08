"""
Status bar component for LiquidPadPlus.
Minimal, modern footer with high contrast text.
"""

import tkinter as tk


class StatusBar:
    """Minimal bottom status bar."""

    def __init__(self, parent, theme, settings_callback=None):
        self.parent = parent
        self.theme = theme
        self.settings_callback = settings_callback
        self.container = None
        self.accent_line = None
        self.bar = None
        self._right_frame = None
        self.word_label = None
        self.theme_label = None
        self._build()

    def _build(self):
        t = self.theme

        self.container = tk.Frame(self.parent, bg=t["bg"])
        self.container.pack(side=tk.BOTTOM, fill=tk.X)

        self.accent_line = tk.Frame(self.container, bg=t["gradient_start"], height=1)
        self.accent_line.pack(fill=tk.X)

        self.bar = tk.Frame(self.container, bg=t["status_bg"])
        self.bar.pack(fill=tk.X)

        self._right_frame = tk.Frame(self.bar, bg=t["status_bg"])
        self._right_frame.pack(side=tk.RIGHT, padx=16, pady=3)

        self.word_label = tk.Label(
            self._right_frame,
            text="0 words",
            bg=t["status_bg"],
            fg=t["fg"],
            font=('Segoe UI', 8)
        )
        self.word_label.pack(side=tk.RIGHT, padx=(12, 0))

        self.theme_label = tk.Label(
            self._right_frame,
            text=t.get("name", "Onyx"),
            bg=t["status_bg"],
            fg=t["gradient_start"],
            font=('Segoe UI', 8)
        )
        self.theme_label.pack(side=tk.RIGHT, padx=(0, 4))

    def update(self, filename, words, chars, theme_name, opacity):
        try:
            self.word_label.configure(text=f"{words} words  ·  {chars} chars  ·  {opacity}%")
            self.theme_label.configure(text=theme_name)
        except tk.TclError:
            pass

    def update_theme(self, theme):
        self.theme = theme
        t = theme
        try:
            self.container.configure(bg=t["bg"])
            self.accent_line.configure(bg=t["gradient_start"])
            self.bar.configure(bg=t["status_bg"])
            self._right_frame.configure(bg=t["status_bg"])
            self.word_label.configure(bg=t["status_bg"], fg=t["fg"])
            self.theme_label.configure(bg=t["status_bg"], fg=t["gradient_start"])
        except tk.TclError:
            pass