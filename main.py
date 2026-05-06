"""
LiquidPad - A fluid, transparent notepad with glass effects.
Entry point for the application.
"""

import sys
import os

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    from app import LiquidPad
except ImportError:
    from src.app import LiquidPad

import tkinter as tk


def set_icon(root):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_paths = [
        os.path.join(base_dir, 'assets', 'icon.ico'),
        os.path.join(base_dir, '..', 'assets', 'icon.ico'),
    ]
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
                return
            except Exception:
                pass


def main():
    root = tk.Tk()
    set_icon(root)
    app = LiquidPad(root)
    root.mainloop()


if __name__ == "__main__":
    main()