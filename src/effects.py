"""
Visual effects for LiquidPadPlus.
Modern utilities.
"""

import tkinter as tk


class Effects:
    """Visual effects utilities."""
    
    @staticmethod
    def lighten(base_color, amount=20):
        r = min(255, int(base_color[1:3], 16) + amount)
        g = min(255, int(base_color[3:5], 16) + amount)
        b = min(255, int(base_color[5:7], 16) + amount)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    @staticmethod
    def darken(base_color, amount=20):
        r = max(0, int(base_color[1:3], 16) - amount)
        g = max(0, int(base_color[3:5], 16) - amount)
        b = max(0, int(base_color[5:7], 16) - amount)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    @staticmethod
    def add_glass_overlay(parent, theme):
        highlight_color = Effects.lighten(theme["text_bg"], 8)
        highlight = tk.Frame(parent, bg=highlight_color, height=1, bd=0)
        highlight.place(relx=0, rely=0, relwidth=1, height=1)
        side = tk.Frame(parent, bg=highlight_color, width=1, bd=0)
        side.place(relx=0, rely=0, width=1, relheight=1)
    
    @staticmethod
    def apply_glass_border(frame, theme):
        if theme.get("glass_effect"):
            border_color = Effects.lighten(theme["border"], 10)
            frame.configure(
                highlightthickness=1,
                highlightbackground=border_color,
                highlightcolor=border_color
            )
        else:
            frame.configure(highlightthickness=0)
    
    @staticmethod
    def accent_line(parent, theme, height=2):
        line = tk.Frame(parent, bg=theme["gradient_start"], height=height, bd=0)
        return line
    
    @staticmethod
    def bind_hover(widget, enter_color, leave_color):
        def on_enter(e):
            widget.configure(bg=enter_color)
        def on_leave(e):
            widget.configure(bg=leave_color)
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)