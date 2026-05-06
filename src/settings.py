"""
Settings manager for LiquidPadPlus.
Handles persistence (JSON), recent files, and a clean macOS-style settings popup.
"""

import tkinter as tk
from tkinter import font as tkfont
import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "liquidpad_settings.json")
MAX_RECENT_FILES = 5

DEFAULTS = {
    "theme":        "onyx",
    "font_family":  "JetBrains Mono",
    "font_size":    12,
    "line_numbers": True,
    "word_wrap":    True,
    "recent_files": [],
}

PREFERRED_FONTS = [
    "JetBrains Mono", "Cascadia Code", "Fira Code",
    "Consolas", "Courier New", "Lucida Console", "Monaco", "Menlo",
]


# ── Persistence ───────────────────────────────────────────────────────────────

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULTS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULTS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass


def add_recent_file(settings: dict, path: str):
    recent = [r for r in settings.get("recent_files", []) if r != path]
    recent.insert(0, path)
    settings["recent_files"] = recent[:MAX_RECENT_FILES]
    save_settings(settings)


def get_recent_files(settings: dict):
    return [r for r in settings.get("recent_files", []) if os.path.exists(r)]


def available_fonts():
    installed = set(tkfont.families())
    found = [f for f in PREFERRED_FONTS if f in installed]
    if "Courier New" not in found:
        found.append("Courier New")
    return found


# ── Settings popup ────────────────────────────────────────────────────────────

class SettingsPopup:

    def __init__(self, root, app):
        self.root     = root
        self.app      = app
        self.settings = app.settings
        self.themes   = app.themes
        self._popup   = None

    def show(self):
        if self._popup and self._popup.winfo_exists():
            self._popup.lift()
            return

        t = self.app.current_theme
        popup = tk.Toplevel(self.root)
        self._popup = popup
        popup.title("Settings")
        popup.geometry("460x580")
        popup.configure(bg=t["bg"])
        popup.transient(self.root)
        popup.resizable(False, False)
        popup.grab_set()

        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width()  // 2) - 230
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 290
        popup.geometry(f"+{px}+{py}")

        self._build(popup, t)

    def _build(self, popup, t):

        # ── Window chrome ─────────────────────────────────────────────────────
        # Top accent strip
        tk.Frame(popup, bg=t["gradient_start"], height=3).pack(fill=tk.X)

        # Header bar
        header = tk.Frame(popup, bg=t["accent"], height=48)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Settings",
            bg=t["accent"],
            fg=t["fg"],
            font=("Segoe UI", 12, "bold"),
            anchor=tk.W,
        ).pack(side=tk.LEFT, padx=20, pady=12)

        tk.Label(
            header,
            text="⚙",
            bg=t["accent"],
            fg=t["gradient_start"],
            font=("Segoe UI", 14),
        ).pack(side=tk.RIGHT, padx=16, pady=12)

        # Hairline under header
        tk.Frame(popup, bg=t["border"], height=1).pack(fill=tk.X)

        # ── Scrollable body ───────────────────────────────────────────────────
        canvas = tk.Canvas(popup, bg=t["bg"], highlightthickness=0, bd=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=t["bg"])
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=canvas.winfo_width())

        inner.bind("<Configure>", _resize)
        canvas.bind("<Configure>", _resize)

        # ── THEME ─────────────────────────────────────────────────────────────
        self._section_header(inner, t, "Theme", "◑")

        theme_var = tk.StringVar(value=self.app.current_theme_name)
        theme_grid = tk.Frame(inner, bg=t["bg"])
        theme_grid.pack(fill=tk.X, padx=20, pady=(4, 8))

        for i, (key, data) in enumerate(self.themes.items()):
            row, col = divmod(i, 2)
            cell = tk.Frame(theme_grid, bg=t["accent_hover"] if key == self.app.current_theme_name else t["accent"])
            cell.grid(row=row, column=col, padx=4, pady=4, sticky="ew")
            theme_grid.columnconfigure(col, weight=1)

            dot_color = data.get("gradient_start", t["gradient_start"])
            tk.Label(cell, text="●", bg=cell["bg"], fg=dot_color, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(10, 4), pady=8)
            name_lbl = tk.Label(cell, text=data["name"], bg=cell["bg"], fg=t["fg"], font=("Segoe UI", 9), anchor=tk.W)
            name_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)

            # Checkmark for selected
            check_lbl = tk.Label(cell, text="✓" if key == self.app.current_theme_name else "", bg=cell["bg"], fg=t["gradient_start"], font=("Segoe UI", 9))
            check_lbl.pack(side=tk.RIGHT, padx=10)

            def _select(e, k=key, c=cell):
                self._apply_theme(k)
                theme_var.set(k)
                # Refresh all cells
                for widget in theme_grid.winfo_children():
                    widget.configure(bg=t["accent"])
                    for child in widget.winfo_children():
                        child.configure(bg=t["accent"])
                c.configure(bg=t["accent_hover"])
                for child in c.winfo_children():
                    child.configure(bg=t["accent_hover"])

            def _hover_in(e, c=cell):
                c.configure(bg=t["accent_hover"])
                for ch in c.winfo_children():
                    ch.configure(bg=t["accent_hover"])

            def _hover_out(e, c=cell, k=key):
                bg = t["accent_hover"] if theme_var.get() == k else t["accent"]
                c.configure(bg=bg)
                for ch in c.winfo_children():
                    ch.configure(bg=bg)

            for w in [cell] + list(cell.winfo_children()):
                w.configure(cursor="hand2")
                w.bind("<Button-1>", _select)
                w.bind("<Enter>", _hover_in)
                w.bind("<Leave>", _hover_out)

        # ── RECENT FILES ──────────────────────────────────────────────────────
        self._section_header(inner, t, "Recent Files", "⌘")

        recent = get_recent_files(self.settings)
        recent_frame = tk.Frame(inner, bg=t["bg"])
        recent_frame.pack(fill=tk.X, padx=20, pady=(4, 8))

        if recent:
            for path in recent:
                name = os.path.basename(path)
                row = tk.Frame(recent_frame, bg=t["accent"])
                row.pack(fill=tk.X, pady=2)

                tk.Label(row, text="📄", bg=t["accent"], fg=t["fg"], font=("Segoe UI", 9),
                         padx=10, pady=7).pack(side=tk.LEFT)
                tk.Label(row, text=name, bg=t["accent"], fg=t["fg"], font=("Segoe UI", 9),
                         anchor=tk.W, pady=7).pack(side=tk.LEFT, fill=tk.X, expand=True)
                tk.Label(row, text=os.path.dirname(path), bg=t["accent"], fg=t["accent_active"],
                         font=("Segoe UI", 7), padx=8).pack(side=tk.RIGHT)

                def _hover_in(e, r=row):  r.configure(bg=t["accent_hover"]); [c.configure(bg=t["accent_hover"]) for c in r.winfo_children()]
                def _hover_out(e, r=row): r.configure(bg=t["accent"]);       [c.configure(bg=t["accent"])       for c in r.winfo_children()]
                def _click(e, p=path):    self._open_recent(p)

                for w in [row] + list(row.winfo_children()):
                    w.configure(cursor="hand2")
                    w.bind("<Enter>", _hover_in)
                    w.bind("<Leave>", _hover_out)
                    w.bind("<Button-1>", _click)
        else:
            tk.Label(recent_frame, text="No recent files", bg=t["bg"], fg=t["accent_active"],
                     font=("Segoe UI", 9, "italic")).pack(anchor=tk.W, pady=4)

        # ── FONT ──────────────────────────────────────────────────────────────
        self._section_header(inner, t, "Font", "Aa")

        font_outer = tk.Frame(inner, bg=t["bg"])
        font_outer.pack(fill=tk.X, padx=20, pady=(4, 8))

        fonts    = available_fonts()
        font_var = tk.StringVar(value=self.app.editor._font_family)
        size_var = tk.IntVar(value=self.app.editor._font_size)

        # Family row
        family_row = tk.Frame(font_outer, bg=t["accent"])
        family_row.pack(fill=tk.X, pady=2)
        tk.Label(family_row, text="Family", bg=t["accent"], fg=t["fg"],
                 font=("Segoe UI", 9), padx=14, pady=8, width=8, anchor=tk.W).pack(side=tk.LEFT)
        tk.Frame(family_row, bg=t["border"], width=1).pack(side=tk.LEFT, fill=tk.Y, pady=4)

        font_menu = tk.OptionMenu(family_row, font_var, *fonts)
        font_menu.configure(bg=t["accent"], fg=t["fg"], activebackground=t["accent_hover"],
                            activeforeground=t["fg"], highlightthickness=0, relief=tk.FLAT,
                            font=("Segoe UI", 9), bd=0, width=20)
        font_menu["menu"].configure(bg=t["accent"], fg=t["fg"], activebackground=t["accent_hover"],
                                    relief=tk.FLAT, bd=0)
        font_menu.pack(side=tk.LEFT, padx=8)
        font_var.trace_add("write", lambda *_: self._apply_font(font_var.get(), size_var.get()))

        # Size row
        size_row = tk.Frame(font_outer, bg=t["accent"])
        size_row.pack(fill=tk.X, pady=2)
        tk.Label(size_row, text="Size", bg=t["accent"], fg=t["fg"],
                 font=("Segoe UI", 9), padx=14, pady=8, width=8, anchor=tk.W).pack(side=tk.LEFT)
        tk.Frame(size_row, bg=t["border"], width=1).pack(side=tk.LEFT, fill=tk.Y, pady=4)

        def _btn_style(parent, text, cmd):
            b = tk.Label(parent, text=text, bg=t["accent_hover"], fg=t["fg"],
                         font=("Segoe UI", 11), padx=12, pady=4, cursor="hand2")
            b.bind("<Button-1>", lambda e: cmd())
            b.bind("<Enter>", lambda e: b.configure(bg=t["accent_active"]))
            b.bind("<Leave>", lambda e: b.configure(bg=t["accent_hover"]))
            return b

        def _dec():
            v = max(6, size_var.get() - 1); size_var.set(v); self._apply_font(font_var.get(), v)
        def _inc():
            v = min(30, size_var.get() + 1); size_var.set(v); self._apply_font(font_var.get(), v)

        _btn_style(size_row, "−", _dec).pack(side=tk.LEFT, padx=(12, 4), pady=4)
        tk.Label(size_row, textvariable=size_var, bg=t["accent"], fg=t["fg"],
                 font=("Segoe UI", 10, "bold"), width=3).pack(side=tk.LEFT, pady=4)
        _btn_style(size_row, "+", _inc).pack(side=tk.LEFT, padx=(4, 0), pady=4)

        # ── EDITOR ────────────────────────────────────────────────────────────
        self._section_header(inner, t, "Editor", "≡")

        ln_var = tk.BooleanVar(value=self.settings.get("line_numbers", True))
        ww_var = tk.BooleanVar(value=self.settings.get("word_wrap", True))

        editor_frame = tk.Frame(inner, bg=t["bg"])
        editor_frame.pack(fill=tk.X, padx=20, pady=(4, 16))

        self._toggle_row(editor_frame, t, "Show line numbers", ln_var,
                         lambda: self._apply_line_numbers(ln_var.get()))
        self._toggle_row(editor_frame, t, "Word wrap", ww_var,
                         lambda: self._apply_word_wrap(ww_var.get()))

        # ── Footer ────────────────────────────────────────────────────────────
        tk.Frame(popup, bg=t["border"], height=1).pack(fill=tk.X, side=tk.BOTTOM)
        footer = tk.Frame(popup, bg=t["accent"], height=52)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        def _save():
            self._save_and_close(theme_var.get(), font_var.get(), size_var.get(),
                                 ln_var.get(), ww_var.get())

        save_btn = tk.Label(
            footer, text="Save & Close",
            bg=t["gradient_start"], fg=t["bg"],
            font=("Segoe UI", 9, "bold"),
            padx=18, pady=8, cursor="hand2",
        )
        save_btn.pack(side=tk.RIGHT, padx=12, pady=10)
        save_btn.bind("<Button-1>", lambda e: _save())
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg=t["gradient_end"]))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg=t["gradient_start"]))

        cancel_btn = tk.Label(
            footer, text="Cancel",
            bg=t["accent"], fg=t["fg"],
            font=("Segoe UI", 9),
            padx=14, pady=8, cursor="hand2",
        )
        cancel_btn.pack(side=tk.RIGHT, pady=10)
        cancel_btn.bind("<Button-1>", lambda e: popup.destroy())
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.configure(bg=t["accent_hover"]))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.configure(bg=t["accent"]))

    # ── UI helpers ────────────────────────────────────────────────────────────

    def _section_header(self, parent, t, title, icon=""):
        f = tk.Frame(parent, bg=t["bg"])
        f.pack(fill=tk.X, padx=20, pady=(16, 6))

        tk.Label(f, text=icon, bg=t["bg"], fg=t["gradient_start"],
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(f, text=title.upper(), bg=t["bg"], fg=t["gradient_start"],
                 font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT)
        tk.Frame(f, bg=t["border"], height=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), pady=7)

    def _toggle_row(self, parent, t, label, var, command):
        row = tk.Frame(parent, bg=t["accent"])
        row.pack(fill=tk.X, pady=2)

        tk.Label(row, text=label, bg=t["accent"], fg=t["fg"],
                 font=("Segoe UI", 9), padx=14, pady=8, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # macOS-style toggle pill
        toggle = _TogglePill(row, var, t, command)
        toggle.frame.pack(side=tk.RIGHT, padx=14, pady=8)

    # ── Live apply ────────────────────────────────────────────────────────────

    def _apply_theme(self, key):
        self.app._change_theme(key)

    def _apply_font(self, family, size):
        self.app.editor._font_family = family
        self.app.editor.set_font_size(size)

    def _apply_line_numbers(self, show: bool):
        editor = self.app.editor
        editor.line_numbers.pack_forget()
        editor.gutter_sep.pack_forget()
        editor.gutter.pack_forget()
        editor.text_area.pack_forget()
        editor._scrollbar.pack_forget()

        if show:
            editor.gutter.pack(side=tk.LEFT, fill=tk.Y)
            editor.gutter_sep.pack(side=tk.LEFT, fill=tk.Y)

        editor.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        editor._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _apply_word_wrap(self, wrap: bool):
        self.app.editor.text_area.configure(wrap=tk.WORD if wrap else tk.NONE)

    def _open_recent(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.app.editor.set_text(content)
            self.app.menubar.current_file = path
            self.app.root.title(f"LiquidPadPlus — {os.path.basename(path)}")
            add_recent_file(self.app.settings, path)
            self.app._safe_update()
            if self._popup and self._popup.winfo_exists():
                self._popup.destroy()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not open file:\n{e}")

    def _save_and_close(self, theme, font_family, font_size, line_numbers, word_wrap):
        self.settings["theme"]        = theme
        self.settings["font_family"]  = font_family
        self.settings["font_size"]    = font_size
        self.settings["line_numbers"] = line_numbers
        self.settings["word_wrap"]    = word_wrap
        save_settings(self.settings)
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()


# ── Toggle pill widget ────────────────────────────────────────────────────────

class _TogglePill:
    """A simple macOS-style on/off toggle drawn with a canvas."""

    W, H = 36, 20

    def __init__(self, parent, var: tk.BooleanVar, theme: dict, command=None):
        self.var     = var
        self.theme   = theme
        self.command = command

        self.frame = tk.Frame(parent, bg=theme["accent"])
        self.canvas = tk.Canvas(
            self.frame,
            width=self.W, height=self.H,
            bg=theme["accent"],
            highlightthickness=0, bd=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._toggle)
        self._draw()

    def _draw(self):
        c = self.canvas
        t = self.theme
        c.delete("all")
        on = self.var.get()
        track_color = t["gradient_start"] if on else t["border"]
        c.create_rounded_rect = self._rounded_rect
        self._rounded_rect(c, 0, 0, self.W, self.H, radius=self.H//2, fill=track_color, outline="")
        # Thumb
        margin = 3
        thumb_x = self.W - self.H + margin if on else margin
        c.create_oval(thumb_x, margin, thumb_x + self.H - 2*margin, self.H - margin,
                      fill=t["fg"], outline="")

    @staticmethod
    def _rounded_rect(canvas, x1, y1, x2, y2, radius=10, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def _toggle(self, event=None):
        self.var.set(not self.var.get())
        self._draw()
        if self.command:
            self.command()