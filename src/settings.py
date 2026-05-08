"""
Settings manager for LiquidPadPlus.
JSON persistence, safe theme/font application, and macOS-style popup.
"""

import tkinter as tk
from tkinter import messagebox, font as tkfont
import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "liquidpad_settings.json")
MAX_RECENT = 5
DEFAULTS = {
    "theme": "onyx", 
    "font_family": "JetBrains Mono", 
    "font_size": 12, 
    "line_numbers": True, 
    "word_wrap": True, 
    "recent_files": [],
    "sidebar_visible": False,
    "last_opened_file": None
}
PREF_FONTS = ["JetBrains Mono", "Cascadia Code", "Fira Code", "Consolas", "Courier New", "Lucida Console", "Monaco", "Menlo"]

def load_settings():
    if not os.path.exists(SETTINGS_FILE): return dict(DEFAULTS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f: data = json.load(f)
        for k, v in DEFAULTS.items(): data.setdefault(k, v)
        return data
    except: return dict(DEFAULTS)

def save_settings(s):
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f: json.dump(s, f, indent=2)
    except: pass

def add_recent_file(s, path):
    if not path or not os.path.exists(path): return
    recent = [r for r in s.get("recent_files", []) if r != path and os.path.exists(r)]
    recent.insert(0, path)
    s["recent_files"] = recent[:MAX_RECENT]
    save_settings(s)

def get_recent_files(s): return [r for r in s.get("recent_files", []) if os.path.exists(r)]

def available_fonts():
    try: inst = set(tkfont.families())
    except: inst = set()
    found = [f for f in PREF_FONTS if f in inst]
    if "Courier New" not in found: found.append("Courier New")
    return found

class SettingsPopup:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.settings = app.settings
        # Reference live app themes instead of static copy
        self._popup = None
        self._theme_cells = {}

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
        px = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 230
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 290
        popup.geometry(f"+{px}+{py}")
        self._build(popup, t)

    def _build(self, popup, t):
        popup._canvas = None
        tk.Frame(popup, bg=t["gradient_start"], height=3).pack(fill=tk.X)
        hdr = tk.Frame(popup, bg=t["accent"], height=48)
        hdr.pack(fill=tk.X); hdr.pack_propagate(False)
        tk.Label(hdr, text="Settings", bg=t["accent"], fg=t["fg"], font=("Segoe UI", 12, "bold"), anchor=tk.W).pack(side=tk.LEFT, padx=20, pady=12)
        tk.Label(hdr, text="⚙", bg=t["accent"], fg=t["gradient_start"], font=("Segoe UI", 14)).pack(side=tk.RIGHT, padx=16, pady=12)
        tk.Frame(popup, bg=t["border"], height=1).pack(fill=tk.X)

        canvas = tk.Canvas(popup, bg=t["bg"], highlightthickness=0, bd=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        popup._canvas = canvas
        inner = tk.Frame(canvas, bg=t["bg"])
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        def _resize(e): canvas.configure(scrollregion=canvas.bbox("all")); canvas.itemconfig(win_id, width=canvas.winfo_width())
        inner.bind("<Configure>", _resize)
        canvas.bind("<Configure>", _resize)

        self._section_header(inner, t, "Theme", "")
        theme_var = tk.StringVar(value=self.app.current_theme_name)
        theme_grid = tk.Frame(inner, bg=t["bg"])
        theme_grid.pack(fill=tk.X, padx=20, pady=(4, 8))
        self._theme_cells = {}  # Reset tracking
        
        for i, (key, data) in enumerate(self.app.themes.items()):
            r, c = divmod(i, 2)
            is_sel = (key == self.app.current_theme_name)
            bg = t["accent_hover"] if is_sel else t["accent"]
            
            cell = tk.Frame(theme_grid, bg=bg, name=f"theme_{key}")
            cell.grid(row=r, column=c, padx=4, pady=4, sticky="ew")
            theme_grid.columnconfigure(c, weight=1)
            
            tk.Label(cell, text="●", bg=bg, fg=data.get("gradient_start", t["gradient_start"]), font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(10, 4), pady=8)
            tk.Label(cell, text=data["name"], bg=bg, fg=t["fg"], font=("Segoe UI", 9), anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)
            tk.Label(cell, text="✓" if is_sel else "", bg=bg, fg=t["gradient_start"], font=("Segoe UI", 9, "bold"), name="check").pack(side=tk.RIGHT, padx=10)

            # Store refs for efficient refresh
            self._theme_cells[key] = {"cell": cell, "check": cell.winfo_children()[2], "name_lbl": cell.winfo_children()[1]}

            # Use command= for reliability instead of bind
            def _select(k=key):
                try:
                    self.app._change_theme(k)
                    theme_var.set(k)
                    self._refresh_grid(theme_var.get(), t)
                except Exception as e:
                    print(f"Theme switch error: {e}")

            cell.configure(cursor="hand2")
            cell.bind("<Button-1>", lambda e, cmd=_select: cmd())
            # Also bind children so clicking text/icon works
            for child in cell.winfo_children():
                child.configure(cursor="hand2")
                child.bind("<Button-1>", lambda e, cmd=_select: cmd())

        self._section_header(inner, t, "Recent Files", "")
        rec_frame = tk.Frame(inner, bg=t["bg"])
        rec_frame.pack(fill=tk.X, padx=20, pady=(4, 8))
        recent = get_recent_files(self.settings)
        if recent:
            for path in recent:
                row = tk.Frame(rec_frame, bg=t["accent"])
                row.pack(fill=tk.X, pady=2)
                tk.Label(row, text="📄", bg=t["accent"], fg=t["fg"], font=("Segoe UI", 9), padx=10, pady=7).pack(side=tk.LEFT)
                tk.Label(row, text=os.path.basename(path), bg=t["accent"], fg=t["fg"], font=("Segoe UI", 9), anchor=tk.W, pady=7).pack(side=tk.LEFT, fill=tk.X, expand=True)
                tk.Label(row, text=os.path.dirname(path), bg=t["accent"], fg=t["accent_active"], font=("Segoe UI", 7), padx=8).pack(side=tk.RIGHT)
                def _hi(e, r=row): r.configure(bg=t["accent_hover"]); [c.configure(bg=t["accent_hover"]) for c in r.winfo_children()]
                def _ho(e, r=row): r.configure(bg=t["accent"]); [c.configure(bg=t["accent"]) for c in r.winfo_children()]
                def _click(e, p=path): self._open_recent(p)
                row.configure(cursor="hand2")
                row.bind("<Enter>", _hi); row.bind("<Leave>", _ho); row.bind("<Button-1>", _click)
        else:
            tk.Label(rec_frame, text="No recent files", bg=t["bg"], fg=t["accent_active"], font=("Segoe UI", 9, "italic")).pack(anchor=tk.W, pady=4)

        self._section_header(inner, t, "Font", "Aa")
        font_outer = tk.Frame(inner, bg=t["bg"])
        font_outer.pack(fill=tk.X, padx=20, pady=(4, 8))
        fonts = available_fonts()
        font_var = tk.StringVar(value=self.app.editor._font_family)
        size_var = tk.IntVar(value=self.app.editor._font_size)

        frow = tk.Frame(font_outer, bg=t["accent"])
        frow.pack(fill=tk.X, pady=2)
        tk.Label(frow, text="Family", bg=t["accent"], fg=t["fg"], font=("Segoe UI", 9), padx=14, pady=8, width=8, anchor=tk.W).pack(side=tk.LEFT)
        tk.Frame(frow, bg=t["border"], width=1).pack(side=tk.LEFT, fill=tk.Y, pady=4)
        fm = tk.OptionMenu(frow, font_var, *fonts)
        fm.configure(bg=t["accent"], fg=t["fg"], activebackground=t["accent_hover"], activeforeground=t["fg"], highlightthickness=0, relief=tk.FLAT, font=("Segoe UI", 9), bd=0, width=20)
        fm["menu"].configure(bg=t["accent"], fg=t["fg"], activebackground=t["accent_hover"], relief=tk.FLAT, bd=0)
        fm.pack(side=tk.LEFT, padx=8)
        font_var.trace_add("write", lambda *_: self._apply_font(font_var.get(), size_var.get()))

        srow = tk.Frame(font_outer, bg=t["accent"])
        srow.pack(fill=tk.X, pady=2)
        tk.Label(srow, text="Size", bg=t["accent"], fg=t["fg"], font=("Segoe UI", 9), padx=14, pady=8, width=8, anchor=tk.W).pack(side=tk.LEFT)
        tk.Frame(srow, bg=t["border"], width=1).pack(side=tk.LEFT, fill=tk.Y, pady=4)
        def _btn(p, txt, cmd):
            b = tk.Label(p, text=txt, bg=t["accent_hover"], fg=t["fg"], font=("Segoe UI", 11), padx=12, pady=4, cursor="hand2")
            b.bind("<Button-1>", lambda e: cmd()); b.bind("<Enter>", lambda e: b.configure(bg=t["accent_active"])); b.bind("<Leave>", lambda e: b.configure(bg=t["accent_hover"]))
            return b
        def _dec(): v = max(6, size_var.get()-1); size_var.set(v); self._apply_font(font_var.get(), v)
        def _inc(): v = min(30, size_var.get()+1); size_var.set(v); self._apply_font(font_var.get(), v)
        _btn(srow, "−", _dec).pack(side=tk.LEFT, padx=(12, 4), pady=4)
        tk.Label(srow, textvariable=size_var, bg=t["accent"], fg=t["fg"], font=("Segoe UI", 10, "bold"), width=3).pack(side=tk.LEFT, pady=4)
        _btn(srow, "+", _inc).pack(side=tk.LEFT, padx=(4, 0), pady=4)

        self._section_header(inner, t, "Editor", "")
        ln_var = tk.BooleanVar(value=self.settings.get("line_numbers", True))
        ww_var = tk.BooleanVar(value=self.settings.get("word_wrap", True))
        ed_frame = tk.Frame(inner, bg=t["bg"])
        ed_frame.pack(fill=tk.X, padx=20, pady=(4, 16))
        self._toggle_row(ed_frame, t, "Show line numbers", ln_var, lambda: self._apply_line_numbers(ln_var.get()))
        self._toggle_row(ed_frame, t, "Word wrap", ww_var, lambda: self._apply_word_wrap(ww_var.get()))

        tk.Frame(popup, bg=t["border"], height=1).pack(fill=tk.X, side=tk.BOTTOM)
        footer = tk.Frame(popup, bg=t["accent"], height=52)
        footer.pack(fill=tk.X, side=tk.BOTTOM); footer.pack_propagate(False)
        def _save(): self._save_and_close(theme_var.get(), font_var.get(), size_var.get(), ln_var.get(), ww_var.get())
        sb = tk.Label(footer, text="Save & Close", bg=t["gradient_start"], fg=t["bg"], font=("Segoe UI", 9, "bold"), padx=18, pady=8, cursor="hand2")
        sb.pack(side=tk.RIGHT, padx=12, pady=10); sb.bind("<Button-1>", lambda e: _save()); sb.bind("<Enter>", lambda e: sb.configure(bg=t["gradient_end"])); sb.bind("<Leave>", lambda e: sb.configure(bg=t["gradient_start"]))
        cb = tk.Label(footer, text="Cancel", bg=t["accent"], fg=t["fg"], font=("Segoe UI", 9), padx=14, pady=8, cursor="hand2")
        cb.pack(side=tk.RIGHT, pady=10); cb.bind("<Button-1>", lambda e: popup.destroy()); cb.bind("<Enter>", lambda e: cb.configure(bg=t["accent_hover"])); cb.bind("<Leave>", lambda e: cb.configure(bg=t["accent"]))

    def _refresh_grid(self, selected, t):
        for key, refs in self._theme_cells.items():
            is_sel = (key == selected)
            bg = t["accent_hover"] if is_sel else t["accent"]
            refs["cell"].configure(bg=bg)
            refs["check"].configure(text="✓" if is_sel else "", bg=bg)
            refs["name_lbl"].configure(bg=bg)
            for child in refs["cell"].winfo_children():
                child.configure(bg=bg)

    def _section_header(self, parent, t, title, icon=""):
        f = tk.Frame(parent, bg=t["bg"])
        f.pack(fill=tk.X, padx=20, pady=(16, 6))
        tk.Label(f, text=icon, bg=t["bg"], fg=t["gradient_start"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(f, text=title.upper(), bg=t["bg"], fg=t["gradient_start"], font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT)
        tk.Frame(f, bg=t["border"], height=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0), pady=7)

    def _toggle_row(self, parent, t, label, var, command):
        row = tk.Frame(parent, bg=t["accent"])
        row.pack(fill=tk.X, pady=2)
        tk.Label(row, text=label, bg=t["accent"], fg=t["fg"], font=("Segoe UI", 9), padx=14, pady=8, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
        _TogglePill(row, var, t, command).frame.pack(side=tk.RIGHT, padx=14, pady=8)

    def _apply_theme(self, key):
        if key in self.app.themes: self.app._change_theme(key)

    def _apply_font(self, family, size):
        av = available_fonts()
        if family not in av: family = av[0] if av else "Courier New"
        size = max(6, min(30, int(size)))
        self.app.editor._font_family = family
        self.app.editor.set_font_size(size)
        self.settings["font_family"] = family
        self.settings["font_size"] = size

    def _apply_line_numbers(self, show):
        ed = self.app.editor
        ed.line_numbers.pack_forget()
        ed.gutter_sep.pack_forget()
        if show:
            ed.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
            ed.gutter_sep.pack(side=tk.LEFT, fill=tk.Y)

    def _apply_word_wrap(self, wrap):
        self.app.editor.text_area.configure(wrap=tk.WORD if wrap else tk.NONE)

    def _open_recent(self, path):
        try:
            if not os.path.exists(path): return messagebox.showwarning("Missing", f"File not found:\n{path}")
            with open(path, "r", encoding="utf-8") as f: content = f.read()
            self.app.editor.set_text(content)
            if hasattr(self.app, "menubar"): self.app.menubar.current_file = path
            self.app.root.title(f"LiquidPadPlus — {os.path.basename(path)}")
            add_recent_file(self.app.settings, path)
            self.app._safe_update()
            self._popup.destroy()
        except Exception as e: messagebox.showerror("Error", str(e))

    def _save_and_close(self, theme, family, size, ln, ww):
        self.settings.update({"theme": theme, "font_family": family, "font_size": size, "line_numbers": ln, "word_wrap": ww})
        save_settings(self.settings)
        if theme != self.app.current_theme_name and theme in self.app.themes:
            self.app.current_theme_name = theme
            self.app.current_theme = self.app.themes[theme]
        if hasattr(self.app, "menubar") and self.app.menubar: self.app.menubar.rebuild(theme)
        if self._popup and self._popup.winfo_exists(): self._popup.destroy()

class _TogglePill:
    W, H = 36, 20
    def __init__(self, parent, var, theme, command=None):
        self.var, self.theme, self.command = var, theme, command
        self.frame = tk.Frame(parent, bg=theme["accent"])
        self.canvas = tk.Canvas(self.frame, width=self.W, height=self.H, bg=theme["accent"], highlightthickness=0, bd=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._toggle)
        self._draw()
    def _draw(self):
        c, t = self.canvas, self.theme
        c.delete("all")
        on = self.var.get()
        track = t["gradient_start"] if on else t["border"]
        self._rounded_rect(c, 0, 0, self.W, self.H, radius=self.H//2, fill=track, outline="")
        margin = 3
        thumb_x = self.W - self.H + margin if on else margin
        c.create_oval(thumb_x, margin, thumb_x + self.H - 2*margin, self.H - margin, fill=t["fg"], outline="")
    @staticmethod
    def _rounded_rect(canvas, x1, y1, x2, y2, radius=10, **kw):
        r = min(radius, (y2-y1)//2, (x2-x1)//2)
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        return canvas.create_polygon(pts, smooth=True, **kw)
    def _toggle(self, event=None):
        self.var.set(not self.var.get())
        self._draw()
        if self.command: self.command()