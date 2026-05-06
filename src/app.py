"""
LiquidPadPlus — Main application.
macOS-inspired, clean, modern.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from themes import THEMES, DEFAULT_THEME
from editor import Editor
from statusbar import StatusBar
from menubar import MenuBar
from sidebar import Sidebar
from settings import load_settings, save_settings, add_recent_file, SettingsPopup


class LiquidPad:

    def __init__(self, root):
        self.root = root
        self.root.title("LiquidPadPlus — Untitled")
        self.root.geometry("1020x680")
        self.root._app = self

        self._set_icon()

        self.settings = load_settings()
        self.themes   = THEMES

        self.current_theme_name = self.settings.get("theme", DEFAULT_THEME)
        if self.current_theme_name not in self.themes:
            self.current_theme_name = DEFAULT_THEME
        self.current_theme = self.themes[self.current_theme_name]

        self.root.configure(bg=self.current_theme["bg"])
        self.root.attributes("-alpha", 0.97)

        self.statusbar    = None
        self.menubar      = None
        self.sidebar      = None
        self.editor       = None
        self.main_frame   = None
        self.editor_frame = None
        self.accent_line  = None
        self._settings_popup = None
        self._built           = False
        self._current_font_size = self.settings.get("font_size", 12)
        self._zoom_after_id     = None

        self._build_ui()
        self._apply_saved_settings()
        self._center_window()
        self._built = True

        self.root.bind("<KeyRelease>", lambda e: self._safe_update())
        self._bind_scroll_zoom()

    def _set_icon(self):
        base_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

    def _build_ui(self):
        t = self.current_theme

        # Status bar — anchors to bottom first
        self.statusbar = StatusBar(self.root, t)

        # Main container
        self.main_frame = tk.Frame(self.root, bg=t["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar — packed first so it locks to left
        callbacks = {
            "new":      self._new_file,
            "open":     self._open_file,
            "save":     self._save_file,
            "save_as":  self._save_as_file,
            "cut":      self._cut,
            "copy":     self._copy,
            "paste":    self._paste,
            "find":     self._show_find,
            "themes":   self._show_themes,
            "opacity":  self._show_opacity,
            "settings": self._show_settings,
            "about":    self._show_about,
        }
        self.sidebar = Sidebar(self.main_frame, t, callbacks)

        # Thin vertical separator between sidebar and editor
        self.sidebar_sep = tk.Frame(self.main_frame, bg=t["border"], width=1)
        self.sidebar_sep.pack(side=tk.LEFT, fill=tk.Y)

        # Editor area
        self.editor_frame = tk.Frame(self.main_frame, bg=t["bg"])
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Thin top accent line above editor
        self.accent_line = tk.Frame(self.editor_frame, bg=t["gradient_start"], height=2)
        self.accent_line.pack(fill=tk.X)

        self.editor = Editor(self.editor_frame, t)

        # Menu bar
        self.menubar = MenuBar(self.root, self.editor, self.statusbar, self._change_theme)
        self.menubar.setup(self.themes, self.current_theme_name)

        # Settings controller
        self._settings_popup = SettingsPopup(self.root, self)

        self._safe_update()

    def _apply_saved_settings(self):
        s = self.settings
        family = s.get("font_family", "JetBrains Mono")
        size   = s.get("font_size", 12)
        self.editor._font_family = family
        self.editor.set_font_size(size)
        self._current_font_size = size

        if not s.get("line_numbers", True):
            self.editor.gutter.pack_forget()
            self.editor.gutter_sep.pack_forget()

        wrap = tk.WORD if s.get("word_wrap", True) else tk.NONE
        self.editor.text_area.configure(wrap=wrap)

    def _center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - 510
        y = (self.root.winfo_screenheight() // 2) - 340
        self.root.geometry(f"1020x680+{x}+{y}")

    def _bind_scroll_zoom(self):
        def on_scroll(event):
            if event.state & 0x4:
                if event.delta > 0 or event.num == 4:
                    self._current_font_size = min(30, self._current_font_size + 1)
                else:
                    self._current_font_size = max(6, self._current_font_size - 1)
                if self._zoom_after_id:
                    self.root.after_cancel(self._zoom_after_id)
                self._zoom_after_id = self.root.after(
                    10, lambda: self.editor.set_font_size(self._current_font_size)
                )

        self.root.bind("<Control-MouseWheel>", on_scroll)
        self.root.bind("<Control-Button-4>",   on_scroll)
        self.root.bind("<Control-Button-5>",   on_scroll)

    def _change_theme(self, theme_name):
        if not self._built:
            return

        self.current_theme_name = theme_name
        self.current_theme      = self.themes[theme_name]
        t = self.current_theme

        self.root.configure(bg=t["bg"])
        self.main_frame.configure(bg=t["bg"])
        self.editor_frame.configure(bg=t["bg"])
        self.accent_line.configure(bg=t["gradient_start"])
        self.sidebar_sep.configure(bg=t["border"])

        self.statusbar.update_theme(t)
        self.sidebar.update_theme(t)
        self.editor.update_theme(t)
        self.menubar.rebuild(theme_name)

        self.settings["theme"] = theme_name
        save_settings(self.settings)

        self._safe_update()

    def _safe_update(self):
        if not self._built or not self.editor:
            return
        try:
            words, chars = self.editor.get_stats()
            fname   = self.menubar.get_filename() if self.menubar else "Untitled"
            tname   = self.themes.get(self.current_theme_name, {}).get("name", "Unknown")
            opacity = self.menubar.get_opacity() if self.menubar else 97
            self.statusbar.update(fname, words, chars, tname, opacity)
        except tk.TclError:
            pass

    # ── File ops ──────────────────────────────────────────────────────────────

    def _new_file(self):
        if self.editor.get_text().strip():
            if messagebox.askyesno("New File", "Clear current text?"):
                self.editor.clear()
                self.menubar.current_file = None
                self.root.title("LiquidPadPlus — Untitled")
        else:
            self.editor.clear()
            self.menubar.current_file = None
            self.root.title("LiquidPadPlus — Untitled")
        self._safe_update()

    def _open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.set_text(f.read())
            self.menubar.current_file = path
            self.root.title(f"LiquidPadPlus — {os.path.basename(path)}")
            add_recent_file(self.settings, path)
            self._safe_update()

    def _save_file(self):
        if self.menubar.current_file:
            with open(self.menubar.current_file, "w", encoding="utf-8") as f:
                f.write(self.editor.get_text())
            self.root.title(f"LiquidPadPlus — {os.path.basename(self.menubar.current_file)}")
        else:
            self._save_as_file()
        self._safe_update()

    def _save_as_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.menubar.current_file = path
            self._save_file()
            add_recent_file(self.settings, path)

    # ── Edit ops ──────────────────────────────────────────────────────────────

    def _cut(self):   self.editor.text_area.event_generate("<<Cut>>")
    def _copy(self):  self.editor.text_area.event_generate("<<Copy>>")
    def _paste(self): self.editor.text_area.event_generate("<<Paste>>")

    # ── Popups ────────────────────────────────────────────────────────────────

    def _show_find(self):
        if self.menubar:
            self.menubar._show_find_replace()

    def _show_settings(self):
        if self._settings_popup:
            self._settings_popup.show()

    def _show_themes(self):
        """Quick theme switcher popup."""
        t = self.current_theme
        popup = tk.Toplevel(self.root)
        popup.title("Themes")
        popup.geometry("240x360")
        popup.configure(bg=t["bg"])
        popup.transient(self.root)
        popup.resizable(False, False)

        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width()  // 2) - 120
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 180
        popup.geometry(f"+{px}+{py}")

        # Header
        tk.Frame(popup, bg=t["gradient_start"], height=3).pack(fill=tk.X)
        hdr = tk.Frame(popup, bg=t["accent"])
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="Choose Theme", bg=t["accent"], fg=t["fg"],
                 font=("Segoe UI", 10, "bold"), padx=16, pady=10).pack(side=tk.LEFT)
        tk.Frame(popup, bg=t["border"], height=1).pack(fill=tk.X)

        for key, data in self.themes.items():
            is_active = key == self.current_theme_name
            row = tk.Frame(popup, bg=t["accent_hover"] if is_active else t["accent"])
            row.pack(fill=tk.X, padx=10, pady=2)

            dot = data.get("gradient_start", t["gradient_start"])
            tk.Label(row, text="●", bg=row["bg"], fg=dot,
                     font=("Segoe UI", 8), padx=10, pady=8).pack(side=tk.LEFT)
            tk.Label(row, text=data["name"], bg=row["bg"], fg=t["fg"],
                     font=("Segoe UI", 9), anchor=tk.W, pady=8).pack(side=tk.LEFT, fill=tk.X, expand=True)
            if is_active:
                tk.Label(row, text="✓", bg=row["bg"], fg=t["gradient_start"],
                         font=("Segoe UI", 9), padx=10).pack(side=tk.RIGHT)

            def _in(e, r=row):  r.configure(bg=t["accent_hover"]); [c.configure(bg=t["accent_hover"]) for c in r.winfo_children()]
            def _out(e, r=row, k=key): bg = t["accent_hover"] if k == self.current_theme_name else t["accent"]; r.configure(bg=bg); [c.configure(bg=bg) for c in r.winfo_children()]
            def _click(e, k=key, p=popup): self._change_theme(k); p.destroy()

            for w in [row] + list(row.winfo_children()):
                w.configure(cursor="hand2")
                w.bind("<Enter>", _in)
                w.bind("<Leave>", _out)
                w.bind("<Button-1>", _click)

    def _show_opacity(self):
        t = self.current_theme
        popup = tk.Toplevel(self.root)
        popup.title("Opacity")
        popup.geometry("280x120")
        popup.configure(bg=t["bg"])
        popup.transient(self.root)
        popup.resizable(False, False)

        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width()  // 2) - 140
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 60
        popup.geometry(f"+{px}+{py}")

        tk.Frame(popup, bg=t["gradient_start"], height=3).pack(fill=tk.X)
        tk.Label(popup, text="Window Opacity", bg=t["bg"], fg=t["fg"],
                 font=("Segoe UI", 10, "bold")).pack(pady=(12, 4))

        slider = tk.Scale(
            popup, from_=30, to=100, orient=tk.HORIZONTAL,
            bg=t["bg"], fg=t["fg"], troughcolor=t["accent"],
            highlightthickness=0, length=240, bd=0,
            sliderrelief=tk.FLAT,
        )
        slider.set(int(self.root.attributes("-alpha") * 100))
        slider.pack(pady=4)
        slider.configure(command=lambda v: self.root.attributes("-alpha", float(v) / 100))

    def _show_about(self):
        t = self.current_theme
        popup = tk.Toplevel(self.root)
        popup.title("About")
        popup.geometry("320x200")
        popup.configure(bg=t["bg"])
        popup.transient(self.root)
        popup.resizable(False, False)

        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width()  // 2) - 160
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 100
        popup.geometry(f"+{px}+{py}")

        tk.Frame(popup, bg=t["gradient_start"], height=3).pack(fill=tk.X)

        body = tk.Frame(popup, bg=t["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=28, pady=20)

        tk.Label(body, text="LiquidPad Plus", bg=t["bg"], fg=t["fg"],
                 font=("Segoe UI", 14, "bold")).pack(anchor=tk.W)
        tk.Label(body, text="v1.0  ·  Built with Python & Tkinter", bg=t["bg"],
                 fg=t["accent_active"], font=("Segoe UI", 8)).pack(anchor=tk.W, pady=(2, 14))

        for line in ["Ctrl+Scroll — Zoom", "Ctrl+F — Find & Replace", "Ctrl+S — Save", "Ctrl+O — Open"]:
            tk.Label(body, text=line, bg=t["bg"], fg=t["fg"],
                     font=("Segoe UI", 9)).pack(anchor=tk.W, pady=1)