"""
Status bar component for LiquidPadPlus.
Responsive, interactive footer with sidebar toggle, live stats, and tooltips.
"""

import tkinter as tk
from config import ICONS  # Import icons from config

class StatusBar:
    def __init__(self, parent, theme, settings_callback=None, sidebar_toggle_callback=None):
        self.parent = parent
        self.theme = theme
        self.settings_callback = settings_callback
        self.sidebar_toggle_callback = sidebar_toggle_callback
        self.container = None
        self.accent_line = None
        self.bar = None
        self._left_frame = None
        self._right_frame = None
        self.cursor_label = None
        self.filename_label = None
        self.stats_label = None
        self.theme_label = None
        self.encoding_label = None
        self.toggle_btn = None
        self._tooltips = {}
        self._build()

    def _build(self):
        t = self.theme
        self.container = tk.Frame(self.parent, bg=t["bg"])
        self.container.pack(side=tk.BOTTOM, fill=tk.X)

        self.accent_line = tk.Frame(self.container, bg=t["gradient_start"], height=1)
        self.accent_line.pack(fill=tk.X)

        self.bar = tk.Frame(self.container, bg=t["status_bg"])
        self.bar.pack(fill=tk.X)
        self.bar.grid_columnconfigure(0, weight=1)
        self.bar.grid_columnconfigure(1, weight=0)

        self._left_frame = tk.Frame(self.bar, bg=t["status_bg"])
        self._left_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=2)

        # Sidebar toggle button using new icon
        if self.sidebar_toggle_callback:
            self.toggle_btn = tk.Label(
                self._left_frame, 
                text=f" {ICONS['sidebar_toggle']} Sidebar", 
                bg=t["status_bg"], 
                fg=t["accent_active"], 
                font=("Segoe UI", 8, "bold"),
                cursor="hand2",
                padx=6, pady=2
            )
            self.toggle_btn.pack(side=tk.LEFT, padx=(0, 8))
            self.toggle_btn.bind("<Button-1>", lambda e: self.sidebar_toggle_callback())
            self.toggle_btn.bind("<Enter>", lambda e: self.toggle_btn.configure(fg=t["gradient_start"]))
            self.toggle_btn.bind("<Leave>", lambda e: self.toggle_btn.configure(fg=t["accent_active"]))
            self._add_tooltip(self.toggle_btn, "Show/Hide Sidebar")

        self.cursor_label = tk.Label(self._left_frame, text="Ln 1, Col 1", bg=t["status_bg"], fg=t["accent_active"], font=("Segoe UI", 8))
        self.cursor_label.pack(side=tk.LEFT)

        self.filename_label = tk.Label(self._left_frame, text="Untitled", bg=t["status_bg"], fg=t["fg"], font=("Segoe UI", 8), anchor="w")
        self.filename_label.pack(side=tk.LEFT, padx=(12, 0), fill=tk.X, expand=True)

        self._right_frame = tk.Frame(self.bar, bg=t["status_bg"])
        self._right_frame.grid(row=0, column=1, sticky="e", padx=8, pady=2)

        self.stats_label = tk.Label(self._right_frame, text="0w · 0c · 100%", bg=t["status_bg"], fg=t["fg"], font=("Segoe UI", 8))
        self.stats_label.pack(side=tk.LEFT, padx=(0, 8))

        self.encoding_label = tk.Label(self._right_frame, text="UTF-8", bg=t["status_bg"], fg=t["accent_active"], font=("Segoe UI", 8))
        self.encoding_label.pack(side=tk.LEFT, padx=(0, 8))
        self._add_tooltip(self.encoding_label, "File encoding")

        self.theme_label = tk.Label(self._right_frame, text=t.get("name", "Onyx"), bg=t["status_bg"], fg=t["gradient_start"], font=("Segoe UI", 8, "bold"))
        self.theme_label.pack(side=tk.LEFT)

        if self.settings_callback:
            self.theme_label.configure(cursor="hand2")
            self.theme_label.bind("<Button-1>", lambda e: self.settings_callback())
            self.theme_label.bind("<Enter>", lambda e: self.theme_label.configure(fg=t["accent_active"]))
            self.theme_label.bind("<Leave>", lambda e: self.theme_label.configure(fg=t["gradient_start"]))
            self._add_tooltip(self.theme_label, "Click to open Settings")

        self._add_tooltip(self.cursor_label, "Current cursor position")

    def _add_tooltip(self, widget, text):
        tooltip = None
        def _show(e):
            nonlocal tooltip
            if tooltip and tooltip.winfo_exists(): return
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tk.Label(tooltip, text=text, bg="#2a2a4a", fg="#e0e0e0", font=("Segoe UI", 8), padx=10, pady=5).pack()
            tooltip.update_idletasks()
            tw, th = tooltip.winfo_width(), tooltip.winfo_height()
            x = max(0, min(e.x_root+10, widget.winfo_screenwidth()-tw-10))
            y = max(0, min(e.y_root-th-5, widget.winfo_screenheight()-th-10))
            tooltip.wm_geometry(f"+{x}+{y}")
        def _hide(e):
            nonlocal tooltip
            if tooltip and tooltip.winfo_exists(): tooltip.destroy()
            tooltip = None
        widget.bind("<Enter>", _show)
        widget.bind("<Leave>", _hide)
        self._tooltips[id(widget)] = (tooltip, _show, _hide)

    def update(self, filename="Untitled", words=0, chars=0, theme_name="Onyx", opacity=100, cursor_pos=None, encoding="UTF-8", is_modified=False):
        try:
            display = f"*{filename}" if is_modified else filename
            if len(display) > 35: display = "…" + display[-32:]
            if cursor_pos: self.cursor_label.configure(text=f"Ln {cursor_pos[0]}, Col {cursor_pos[1]}")
            self.filename_label.configure(text=display)
            self.stats_label.configure(text=f"{words}w · {chars}c · {opacity}%")
            self.theme_label.configure(text=theme_name)
            self.encoding_label.configure(text=encoding)
        except tk.TclError: pass

    def update_theme(self, theme):
        self.theme = theme
        t = theme
        try:
            self.container.configure(bg=t["bg"])
            self.accent_line.configure(bg=t["gradient_start"])
            self.bar.configure(bg=t["status_bg"])
            self._left_frame.configure(bg=t["status_bg"])
            self._right_frame.configure(bg=t["status_bg"])
            if self.toggle_btn: self.toggle_btn.configure(bg=t["status_bg"], fg=t["accent_active"])
            self.cursor_label.configure(bg=t["status_bg"], fg=t["accent_active"])
            self.filename_label.configure(bg=t["status_bg"], fg=t["fg"])
            self.stats_label.configure(bg=t["status_bg"], fg=t["fg"])
            self.encoding_label.configure(bg=t["status_bg"], fg=t["accent_active"])
            self.theme_label.configure(bg=t["status_bg"], fg=t["gradient_start"])
        except tk.TclError: pass