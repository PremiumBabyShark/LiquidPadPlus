"""
LiquidPadPlus - Main application class.
Left sidebar + scroll-to-zoom + dark titlebar + keyboard shortcuts.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from themes import THEMES, DEFAULT_THEME
from editor import Editor
from statusbar import StatusBar
from sidebar import Sidebar
from settings import load_settings, save_settings, add_recent_file, SettingsPopup


class LiquidPad:
    """Main LiquidPadPlus application."""

    def __init__(self, root):
        self.root = root
        self.root.title("LiquidPadPlus - Untitled")
        self.root.geometry("950x650")
        self.root.attributes('-alpha', 0.92)
        self.root._app = self

        self._set_icon()
        self._set_dark_titlebar()

        self.settings = load_settings()

        self.themes = THEMES
        self.current_theme_name = self.settings.get("theme", DEFAULT_THEME)
        if self.current_theme_name not in self.themes:
            self.current_theme_name = DEFAULT_THEME
        self.current_theme = self.themes[self.current_theme_name]
        self.root.configure(bg=self.current_theme["bg"])

        self.statusbar = None
        self.sidebar = None
        self.editor = None
        self.main_frame = None
        self.editor_frame = None
        self.accent_line = None
        self._settings_popup = None
        self._built = False
        self._current_font_size = self.settings.get("font_size", 12)
        self._zoom_after_id = None
        self._always_on_top = False

        self._build_ui()
        self._apply_saved_editor_settings()
        self._center_window()
        self._built = True

        self.root.bind('<KeyRelease>', lambda e: self._safe_update())
        self._bind_scroll_zoom()
        self._bind_shortcuts()

    def _set_icon(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

    def _set_dark_titlebar(self):
        try:
            import ctypes
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            value = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 20, ctypes.byref(value), ctypes.sizeof(value)
            )
        except:
            pass

    def _build_ui(self):
        t = self.current_theme

        self.statusbar = StatusBar(self.root, t)

        self.main_frame = tk.Frame(self.root, bg=t["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        callbacks = {
            'new':     self._new_file,
            'open':    self._open_file,
            'save':    self._save_file,
            'save_as': self._save_as_file,
            'cut':     self._cut,
            'copy':    self._copy,
            'paste':   self._paste,
            'find':    self._show_find,
            'themes':  self._show_themes,
            'opacity': self._show_opacity,
            'always_on_top': self._toggle_always_on_top,
            'settings': self._show_settings,
            'about':   self._show_about,
        }
        self.sidebar = Sidebar(self.main_frame, t, callbacks)

        self.editor_frame = tk.Frame(self.main_frame, bg=t["bg"])
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.accent_line = tk.Frame(self.editor_frame, bg=t["gradient_start"], height=2)
        self.accent_line.pack(fill=tk.X)

        self.editor = Editor(self.editor_frame, t)

        self._settings_popup = SettingsPopup(self.root, self)

        self._safe_update()

    def _apply_saved_editor_settings(self):
        s = self.settings
        font_family = s.get("font_family", "JetBrains Mono")
        font_size   = s.get("font_size", 12)
        self.editor._font_family = font_family
        self.editor.set_font_size(font_size)
        self._current_font_size = font_size

        if not s.get("line_numbers", True):
            self.editor.line_numbers.pack_forget()
            self.editor.gutter_sep.pack_forget()

        wrap = tk.WORD if s.get("word_wrap", True) else tk.NONE
        self.editor.text_area.configure(wrap=wrap)

    def _center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - 475
        y = (self.root.winfo_screenheight() // 2) - 325
        self.root.geometry(f'950x650+{x}+{y}')

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
        self.root.bind('<Control-MouseWheel>', on_scroll)
        self.root.bind('<Control-Button-4>',   on_scroll)
        self.root.bind('<Control-Button-5>',   on_scroll)

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts directly to app."""
        self.root.bind('<Control-n>', lambda e: self._new_file())
        self.root.bind('<Control-o>', lambda e: self._open_file())
        self.root.bind('<Control-s>', lambda e: self._save_file())
        self.root.bind('<Control-S>', lambda e: self._save_as_file())
        self.root.bind('<Control-f>', lambda e: self._show_find())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-x>', lambda e: self._cut())
        self.root.bind('<Control-c>', lambda e: self._copy())
        self.root.bind('<Control-v>', lambda e: self._paste())
        self.root.bind('<Control-a>', lambda e: self._select_all())
        self.root.bind('<Control-z>', lambda e: self._undo())
        self.root.bind('<Control-y>', lambda e: self._redo())

    def _change_theme(self, theme_name):
        if not self._built:
            return
        self.current_theme_name = theme_name
        self.current_theme = self.themes[theme_name]
        t = self.current_theme
        self.root.configure(bg=t["bg"])
        self.main_frame.configure(bg=t["bg"])
        self.editor_frame.configure(bg=t["bg"])
        self.accent_line.configure(bg=t["gradient_start"])
        self.statusbar.update_theme(t)
        self.sidebar.update_theme(t)
        self.editor.update_theme(t)
        self.settings["theme"] = theme_name
        save_settings(self.settings)
        self._safe_update()

    def _safe_update(self):
        if not self._built or not self.editor:
            return
        try:
            words, chars = self.editor.get_stats()
            fname = "Untitled"
            tname = self.themes.get(self.current_theme_name, {}).get("name", "Unknown")
            opacity = int(self.root.attributes('-alpha') * 100)
            self.statusbar.update(fname, words, chars, tname, opacity)
        except tk.TclError:
            pass

    def _select_all(self):
        self.editor.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.text_area.mark_set(tk.INSERT, "1.0")

    def _undo(self):
        try:
            self.editor.text_area.edit_undo()
        except:
            pass

    def _redo(self):
        try:
            self.editor.text_area.edit_redo()
        except:
            pass

    def _new_file(self):
        if self.editor.get_text().strip():
            if messagebox.askyesno("New", "Clear current text?"):
                self.editor.clear()
                self.root.title("LiquidPadPlus - Untitled")
        else:
            self.editor.clear()
            self.root.title("LiquidPadPlus - Untitled")
        self._safe_update()

    def _open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.editor.set_text(f.read())
            self.root.title(f"LiquidPadPlus - {os.path.basename(path)}")
            add_recent_file(self.settings, path)
            self._safe_update()

    def _save_file(self):
        self._save_as_file()
        self._safe_update()

    def _save_as_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_text())
            self.root.title(f"LiquidPadPlus - {os.path.basename(path)}")
            add_recent_file(self.settings, path)

    def _cut(self):
        self.editor.text_area.event_generate("<<Cut>>")

    def _copy(self):
        self.editor.text_area.event_generate("<<Copy>>")

    def _paste(self):
        self.editor.text_area.event_generate("<<Paste>>")

    def _toggle_always_on_top(self):
        self._always_on_top = not self._always_on_top
        self.root.attributes('-topmost', self._always_on_top)

    def _show_find(self):
        from findreplace import FindReplace
        fr = FindReplace(self.root, self.editor)
        fr.set_theme(self.current_theme)
        fr.show()

    def _show_settings(self):
        if self._settings_popup:
            self._settings_popup.show()

    def _show_themes(self):
        t = self.current_theme
        popup = tk.Toplevel(self.root)
        popup.title("Themes")
        popup.geometry("220x340")
        popup.configure(bg=t["bg"])
        popup.transient(self.root)
        popup.resizable(False, False)
        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width()  // 2) - 110
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 170
        popup.geometry(f'+{px}+{py}')
        tk.Label(popup, text="Choose Theme", bg=t["bg"], fg=t["fg"],
                font=('Segoe UI', 10, 'bold')).pack(pady=10)
        for key, data in self.themes.items():
            btn = tk.Label(popup, text=data["name"], bg=t["accent"], fg=t["fg"],
                          font=('Segoe UI', 9), padx=14, pady=6, cursor='hand2')
            btn.pack(fill=tk.X, padx=14, pady=1)
            btn.bind('<Button-1>', lambda e, k=key, p=popup: [self._change_theme(k), p.destroy()])

    def _show_opacity(self):
        t = self.current_theme
        popup = tk.Toplevel(self.root)
        popup.title("Opacity")
        popup.geometry("260x110")
        popup.configure(bg=t["bg"])
        popup.transient(self.root)
        popup.resizable(False, False)
        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width()  // 2) - 130
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 55
        popup.geometry(f'+{px}+{py}')
        tk.Label(popup, text="Window Opacity", bg=t["bg"], fg=t["fg"],
                font=('Segoe UI', 10, 'bold')).pack(pady=(10, 2))
        slider = tk.Scale(
            popup, from_=30, to=100, orient=tk.HORIZONTAL,
            bg=t["bg"], fg=t["fg"],
            troughcolor=t.get("slider_trough", t["accent"]),
            activebackground=t.get("slider_puck", t["gradient_start"]),
            highlightthickness=0, length=220, bd=0
        )
        slider.set(int(self.root.attributes('-alpha') * 100))
        slider.pack(pady=4)
        slider.configure(command=lambda v: self.root.attributes('-alpha', float(v) / 100))

    def _show_about(self):
        messagebox.showinfo(
            "About LiquidPadPlus",
            "LiquidPadPlus v1.0\n\n"
            "Modern sidebar notepad.\n"
            "Ctrl+Scroll to zoom\n"
            "Glass effects | Multiple themes\n\n"
            "Built with Python & Tkinter"
        )