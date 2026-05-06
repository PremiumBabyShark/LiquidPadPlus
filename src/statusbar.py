"""
Status bar component for LiquidPadPlus.
macOS-style minimal footer with pill-shaped info badges.
"""

import tkinter as tk


class StatusBar:

    def __init__(self, parent, theme):
        self.parent       = parent
        self.theme        = theme
        self.container    = None
        self.accent_line  = None
        self.bar          = None
        self._right_frame = None
        self.word_label   = None
        self.theme_label  = None
        self._build()

    def _build(self):
        t = self.theme

        self.container = tk.Frame(self.parent, bg=t["status_bg"])
        self.container.pack(side=tk.BOTTOM, fill=tk.X)

        # Top hairline
        self.accent_line = tk.Frame(self.container, bg=t["gradient_start"], height=1)
        self.accent_line.pack(fill=tk.X)

        self.bar = tk.Frame(self.container, bg=t["status_bg"])
        self.bar.pack(fill=tk.X, padx=0)

        # Left side — file indicator dot
        left_frame = tk.Frame(self.bar, bg=t["status_bg"])
        left_frame.pack(side=tk.LEFT, padx=14, pady=5)

        self.dot_label = tk.Label(
            left_frame,
            text="●",
            bg=t["status_bg"],
            fg=t["gradient_start"],
            font=("Segoe UI", 7),
        )
        self.dot_label.pack(side=tk.LEFT)

        self.file_label = tk.Label(
            left_frame,
            text="Untitled",
            bg=t["status_bg"],
            fg=t["accent_active"],
            font=("Segoe UI", 8),
        )
        self.file_label.pack(side=tk.LEFT, padx=(4, 0))

        # Right side — stats + theme name
        self._right_frame = tk.Frame(self.bar, bg=t["status_bg"])
        self._right_frame.pack(side=tk.RIGHT, padx=14, pady=5)

        self.theme_label = tk.Label(
            self._right_frame,
            text=t.get("name", "Onyx"),
            bg=t["status_bg"],
            fg=t["gradient_start"],
            font=("Segoe UI", 8),
        )
        self.theme_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Separator dot
        tk.Label(
            self._right_frame,
            text="·",
            bg=t["status_bg"],
            fg=t["accent_active"],
            font=("Segoe UI", 8),
        ).pack(side=tk.RIGHT, padx=4)

        self.word_label = tk.Label(
            self._right_frame,
            text="0 words  ·  0 chars",
            bg=t["status_bg"],
            fg=t["accent_active"],
            font=("Segoe UI", 8),
        )
        self.word_label.pack(side=tk.RIGHT)

    def update(self, filename, words, chars, theme_name, opacity):
        try:
            self.file_label.configure(text=filename or "Untitled")
            self.word_label.configure(text=f"{words} words  ·  {chars} chars  ·  {opacity}%")
            self.theme_label.configure(text=theme_name)
        except tk.TclError:
            pass

    def update_theme(self, theme):
        self.theme = theme
        t = theme
        try:
            self.container.configure(bg=t["status_bg"])
            self.accent_line.configure(bg=t["gradient_start"])
            self.bar.configure(bg=t["status_bg"])
            self._right_frame.configure(bg=t["status_bg"])
            self.word_label.configure(bg=t["status_bg"], fg=t["accent_active"])
            self.theme_label.configure(bg=t["status_bg"], fg=t["gradient_start"])
            self.dot_label.configure(bg=t["status_bg"], fg=t["gradient_start"])
            self.file_label.configure(bg=t["status_bg"], fg=t["accent_active"])
            # Separator dots
            for child in self._right_frame.winfo_children():
                try:
                    child.configure(bg=t["status_bg"])
                except tk.TclError:
                    pass
            for child in self.bar.winfo_children():
                if isinstance(child, tk.Frame):
                    try:
                        child.configure(bg=t["status_bg"])
                    except tk.TclError:
                        pass
        except tk.TclError:
            pass