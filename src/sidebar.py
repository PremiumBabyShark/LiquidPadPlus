"""
Sidebar component for LiquidPadPlus.
macOS-inspired left panel — SF-style icons, clean groups, no clutter.
"""

import tkinter as tk
from effects import Effects


# Icon glyphs mapped to button labels (Unicode symbols that work on Windows)
ICONS = {
    "New":      "✦",
    "Open":     "⌘",
    "Save":     "↓",
    "Save As":  "⤓",
    "Cut":      "✂",
    "Copy":     "⎘",
    "Paste":    "⎗",
    "Find":     "⌕",
    "Themes":   "◑",
    "Opacity":  "◎",
    "Settings": "⚙",
    "About":    "◉",
}

GROUPS = [
    [("New", "new"), ("Open", "open"), ("Save", "save"), ("Save As", "save_as")],
    [("Cut", "cut"), ("Copy", "copy"), ("Paste", "paste"), ("Find", "find")],
    [("Themes", "themes"), ("Opacity", "opacity")],
    [("Settings", "settings"), ("About", "about")],
]


class Sidebar:

    def __init__(self, parent, theme, callbacks):
        self.parent    = parent
        self.theme     = theme
        self.callbacks = callbacks
        self.frame     = None
        self.buttons   = []
        self.dividers  = []
        self.header_label  = None
        self.top_divider   = None
        self.version_label = None
        self._build()

    def _build(self):
        t = self.theme

        self.frame = tk.Frame(self.parent, bg=t["sidebar_bg"], width=200)
        self.frame.pack(side=tk.LEFT, fill=tk.Y)
        self.frame.pack_propagate(False)

        # ── App name header ──────────────────────────────────────────────────
        self.top_divider = tk.Frame(self.frame, bg=t["gradient_start"], height=3)
        self.top_divider.pack(fill=tk.X)

        self.header_label = tk.Label(
            self.frame,
            text="LiquidPad Plus",
            bg=t["sidebar_bg"],
            fg=t["gradient_start"],
            font=("Segoe UI", 10, "bold"),
            anchor=tk.W,
        )
        self.header_label.pack(fill=tk.X, padx=18, pady=(14, 0))

        self.sub_label = tk.Label(
            self.frame,
            text="Notepad  ·  v1.0",
            bg=t["sidebar_bg"],
            fg=t["accent_active"],
            font=("Segoe UI", 7),
            anchor=tk.W,
        )
        self.sub_label.pack(fill=tk.X, padx=18, pady=(0, 12))

        # ── Button groups ────────────────────────────────────────────────────
        for i, group in enumerate(GROUPS):
            if i > 0:
                self._divider()
            for label, cb_key in group:
                self._btn(label, self.callbacks.get(cb_key))

        # Spacer
        self.spacer = tk.Frame(self.frame, bg=t["sidebar_bg"])
        self.spacer.pack(fill=tk.BOTH, expand=True)

    def _divider(self):
        t = self.theme
        d = tk.Frame(self.frame, bg=t["border"], height=1)
        d.pack(fill=tk.X, padx=16, pady=6)
        self.dividers.append(d)

    def _btn(self, label, command):
        t = self.theme
        icon = ICONS.get(label, "•")

        row = tk.Frame(self.frame, bg=t["sidebar_bg"], cursor="hand2")
        row.pack(fill=tk.X, padx=8, pady=1)

        icon_lbl = tk.Label(
            row,
            text=icon,
            bg=t["sidebar_bg"],
            fg=t["gradient_start"],
            font=("Segoe UI", 10),
            width=2,
            anchor=tk.CENTER,
        )
        icon_lbl.pack(side=tk.LEFT, padx=(8, 4), pady=5)

        text_lbl = tk.Label(
            row,
            text=label,
            bg=t["sidebar_bg"],
            fg=t["fg"],
            font=("Segoe UI", 9),
            anchor=tk.W,
        )
        text_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        # Hover on both row and children
        def _enter(e):
            row.configure(bg=t["accent_hover"])
            icon_lbl.configure(bg=t["accent_hover"])
            text_lbl.configure(bg=t["accent_hover"])

        def _leave(e):
            row.configure(bg=t["sidebar_bg"])
            icon_lbl.configure(bg=t["sidebar_bg"])
            text_lbl.configure(bg=t["sidebar_bg"])

        for w in (row, icon_lbl, text_lbl):
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)
            if command:
                w.bind("<Button-1>", lambda e, cmd=command: cmd())

        self.buttons.append((row, icon_lbl, text_lbl))

    def update_theme(self, theme):
        self.theme = theme
        t = theme

        self.frame.configure(bg=t["sidebar_bg"])
        if self.header_label:
            self.header_label.configure(bg=t["sidebar_bg"], fg=t["gradient_start"])
        if self.sub_label:
            self.sub_label.configure(bg=t["sidebar_bg"], fg=t["accent_active"])
        if self.top_divider:
            self.top_divider.configure(bg=t["gradient_start"])
        if self.spacer:
            self.spacer.configure(bg=t["sidebar_bg"])

        for d in self.dividers:
            try:
                d.configure(bg=t["border"])
            except tk.TclError:
                pass

        for (row, icon_lbl, text_lbl) in self.buttons:
            try:
                row.configure(bg=t["sidebar_bg"])
                icon_lbl.configure(bg=t["sidebar_bg"], fg=t["gradient_start"])
                text_lbl.configure(bg=t["sidebar_bg"], fg=t["fg"])
                # Rebind hover with new colors
                def _enter(e, r=row, i=icon_lbl, tx=text_lbl):
                    r.configure(bg=t["accent_hover"])
                    i.configure(bg=t["accent_hover"])
                    tx.configure(bg=t["accent_hover"])
                def _leave(e, r=row, i=icon_lbl, tx=text_lbl):
                    r.configure(bg=t["sidebar_bg"])
                    i.configure(bg=t["sidebar_bg"])
                    tx.configure(bg=t["sidebar_bg"])
                for w in (row, icon_lbl, text_lbl):
                    w.bind("<Enter>", _enter)
                    w.bind("<Leave>", _leave)
            except tk.TclError:
                pass

        # Catch any leftover header frames
        for child in self.frame.winfo_children():
            if isinstance(child, tk.Frame) and child not in self.dividers and child is not self.top_divider and child is not self.spacer:
                try:
                    child.configure(bg=t["sidebar_bg"])
                except tk.TclError:
                    pass