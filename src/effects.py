"""
Visual effects for LiquidPadPlus.
Robust color utilities and memory-safe UI bindings.
"""

import tkinter as tk
import re

class Effects:
    @staticmethod
    def _parse_hex(color):
        if not color or not isinstance(color, str): return "#888888"
        color = color.strip().lower().lstrip("#")
        if len(color) == 3: color = "".join(c*2 for c in color)
        if len(color) > 6: color = color[:6]
        if len(color) != 6 or not re.match(r"^[0-9a-f]{6}$", color): return "#888888"
        return f"#{color}"

    @staticmethod
    def lighten(base_color, amount=20):
        b = Effects._parse_hex(base_color)
        r = min(255, int(b[1:3], 16) + amount)
        g = min(255, int(b[3:5], 16) + amount)
        b_val = min(255, int(b[5:7], 16) + amount)
        return f"#{r:02x}{g:02x}{b_val:02x}"

    @staticmethod
    def darken(base_color, amount=20):
        b = Effects._parse_hex(base_color)
        r = max(0, int(b[1:3], 16) - amount)
        g = max(0, int(b[3:5], 16) - amount)
        b_val = max(0, int(b[5:7], 16) - amount)
        return f"#{r:02x}{g:02x}{b_val:02x}"

    @staticmethod
    def blend(c1, c2, ratio=0.5):
        c1, c2 = Effects._parse_hex(c1), Effects._parse_hex(c2)
        r = int(int(c1[1:3], 16)*(1-ratio) + int(c2[1:3], 16)*ratio)
        g = int(int(c1[3:5], 16)*(1-ratio) + int(c2[3:5], 16)*ratio)
        b = int(int(c1[5:7], 16)*(1-ratio) + int(c2[5:7], 16)*ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def add_glass_overlay(parent, theme):
        base = theme.get("text_bg", theme.get("bg", "#1e1e1e"))
        hl = Effects.lighten(base, 8)
        top = tk.Frame(parent, bg=hl, height=1, bd=0, highlightthickness=0)
        top.pack(side=tk.TOP, fill=tk.X)
        left = tk.Frame(parent, bg=hl, width=1, bd=0, highlightthickness=0)
        left.pack(side=tk.LEFT, fill=tk.Y)
        return top, left

    @staticmethod
    def apply_glass_border(frame, theme):
        if theme.get("glass_effect"):
            bc = Effects.lighten(theme.get("border", "#444"), 10)
            frame.configure(highlightthickness=1, highlightbackground=bc, highlightcolor=bc)
        else:
            frame.configure(highlightthickness=0)

    @staticmethod
    def accent_line(parent, theme, height=2, side="top"):
        line = tk.Frame(parent, bg=theme.get("gradient_start", theme.get("accent")), height=height, bd=0, highlightthickness=0)
        side_map = {"top": tk.TOP, "bottom": tk.BOTTOM, "left": tk.LEFT, "right": tk.RIGHT}
        fill_map = {"top": tk.X, "bottom": tk.X, "left": tk.Y, "right": tk.Y}
        line.pack(side=side_map.get(side, tk.TOP), fill=fill_map.get(side, tk.X))
        return line

    @staticmethod
    def bind_hover(widget, enter_color, leave_color, cursor="hand2"):
        orig_bg = widget.cget("bg") or leave_color
        orig_cur = widget.cget("cursor") or "arrow"
        def _enter(e): widget.configure(bg=enter_color, cursor=cursor)
        def _leave(e): widget.configure(bg=leave_color, cursor=orig_cur)
        widget.bind("<Enter>", _enter)
        widget.bind("<Leave>", _leave)
        def unbind():
            try:
                widget.unbind("<Enter>")
                widget.unbind("<Leave>")
                widget.configure(bg=orig_bg, cursor=orig_cur)
            except tk.TclError: pass
        return unbind