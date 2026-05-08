"""
LiquidPadPlus - Main application class.
Session restore, retractable sidebar, fixed save logic, and clean module integration.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from themes import THEMES, DEFAULT_THEME, get_theme
from editor import Editor
from statusbar import StatusBar
from sidebar import Sidebar
from settings import load_settings, save_settings, add_recent_file, SettingsPopup
from menubar import MenuBar

class LiquidPad:
    def __init__(self, root):
        self.root = root
        self.root.title("LiquidPadPlus - Untitled")
        self.root.geometry("950x650")
        self.root.attributes("-alpha", 0.92)
        self.root._app = self

        self._set_dark_titlebar()
        self.settings = load_settings()
        self.themes = THEMES
        self.current_theme_name = self.settings.get("theme", DEFAULT_THEME)
        self.current_theme = get_theme(self.current_theme_name)
        self.root.configure(bg=self.current_theme["bg"])

        self.file_path = None
        self.is_modified = False
        self.sidebar_visible = self.settings.get("sidebar_visible", False)
        self.statusbar = None
        self.sidebar = None
        self.editor = None
        self.main_frame = None
        self.editor_frame = None
        self.accent_line = None
        self._settings_popup = SettingsPopup(self.root, self)
        self._built = False
        self._current_font_size = self.settings.get("font_size", 12)
        self._zoom_after_id = None
        self._always_on_top = False

        self._build_ui()
        self._apply_saved_editor_settings()
        self._center_window()
        self._built = True

        # Session Restore: Reopen last file if it still exists
        self._restore_session()

        self._bind_scroll_zoom()
        self._bind_shortcuts()
        
        # Ensure settings save on window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """Save session state and exit cleanly."""
        self.settings["last_opened_file"] = self.file_path
        save_settings(self.settings)
        self.root.destroy()

    def _restore_session(self):
        """Automatically reopen the last file if it still exists."""
        last_file = self.settings.get("last_opened_file")
        if last_file and os.path.exists(last_file):
            self._load_file(last_file)

    def _set_dark_titlebar(self):
        try:
            import ctypes
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int(1)))
        except: pass

    def _build_ui(self):
        t = self.current_theme
        self.statusbar = StatusBar(self.root, t, self._show_settings, self._toggle_sidebar)
        self.main_frame = tk.Frame(self.root, bg=t["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        callbacks = {"new": self._new_file, "open": self._open_file, "save": self._save_file, "save_as": self._save_as_file,
                     "cut": self._cut, "copy": self._copy, "paste": self._paste, "find": self._show_find, "themes": self._show_themes,
                     "opacity": self._show_opacity, "always_on_top": self._toggle_always_on_top, "settings": self._show_settings, "about": self._show_about}
        
        self.sidebar = Sidebar(self.main_frame, t, callbacks)
        if self.sidebar_visible:
            self.sidebar.frame.pack(side=tk.LEFT, fill=tk.Y)
        else:
            self.sidebar.frame.pack_forget()

        self.editor_frame = tk.Frame(self.main_frame, bg=t["bg"])
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.accent_line = tk.Frame(self.editor_frame, bg=t["gradient_start"], height=2)
        self.accent_line.pack(fill=tk.X)
        self.editor = Editor(self.editor_frame, t)
        self.menubar = MenuBar(self.root, self.editor, self.statusbar, self._change_theme)
        self.menubar.setup(self.themes, self.current_theme_name)
        self._safe_update()

    def _apply_saved_editor_settings(self):
        s = self.settings
        self.editor._font_family = s.get("font_family", "JetBrains Mono")
        self.editor.set_font_size(self._current_font_size)
        if not s.get("line_numbers", True):
            self.editor.line_numbers.pack_forget()
            self.editor.gutter_sep.pack_forget()
        self.editor.text_area.configure(wrap=tk.WORD if s.get("word_wrap", True) else tk.NONE)

    def _center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 475
        y = (self.root.winfo_screenheight() // 2) - 325
        self.root.geometry(f"950x650+{x}+{y}")

    def _bind_scroll_zoom(self):
        def on_scroll(event):
            if event.state & 0x4:
                self._current_font_size = min(30, max(6, self._current_font_size + (1 if event.delta > 0 or event.num == 4 else -1)))
                if self._zoom_after_id: self.root.after_cancel(self._zoom_after_id)
                self._zoom_after_id = self.root.after(10, lambda: self.editor.set_font_size(self._current_font_size))
        self.root.bind("<Control-MouseWheel>", on_scroll)
        self.root.bind("<Control-Button-4>", on_scroll)
        self.root.bind("<Control-Button-5>", on_scroll)

    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self._new_file())
        self.root.bind("<Control-o>", lambda e: self._open_file())
        self.root.bind("<Control-s>", lambda e: self._save_file())
        self.root.bind("<Control-S>", lambda e: self._save_as_file())
        self.root.bind("<Control-f>", lambda e: self._show_find())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-x>", lambda e: self._cut())
        self.root.bind("<Control-c>", lambda e: self._copy())
        self.root.bind("<Control-v>", lambda e: self._paste())
        self.root.bind("<Control-a>", lambda e: self._select_all())
        self.root.bind("<Control-z>", lambda e: self._undo())
        self.root.bind("<Control-y>", lambda e: self._redo())

    def _toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_visible:
            self.sidebar.frame.pack(side=tk.LEFT, fill=tk.Y, before=self.editor_frame)
        else:
            self.sidebar.frame.pack_forget()
        self.settings["sidebar_visible"] = self.sidebar_visible
        save_settings(self.settings)

    def _change_theme(self, theme_name):
        if not self._built: return
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
        if not self._built or not self.editor: return
        try:
            words, chars = self.editor.get_stats()
            fname = os.path.basename(self.file_path) if self.file_path else "Untitled"
            tname = self.themes.get(self.current_theme_name, {}).get("name", "Unknown")
            opacity = int(self.root.attributes("-alpha") * 100)
            cursor = self.editor.text_area.index(tk.INSERT).split(".")
            self.statusbar.update(filename=fname, words=words, chars=chars, theme_name=tname, opacity=opacity,
                                  cursor_pos=(int(cursor[0]), int(cursor[1])+1), encoding="UTF-8", is_modified=self.is_modified)
        except tk.TclError: pass

    def _select_all(self): self.editor.text_area.tag_add(tk.SEL, "1.0", tk.END); self.editor.text_area.mark_set(tk.INSERT, "1.0")
    def _undo(self):
        try: self.editor.text_area.edit_undo()
        except: pass
    def _redo(self):
        try: self.editor.text_area.edit_redo()
        except: pass
    def _cut(self): self.editor.text_area.event_generate("<<Cut>>")
    def _copy(self): self.editor.text_area.event_generate("<<Copy>>")
    def _paste(self): self.editor.text_area.event_generate("<<Paste>>")
    def _toggle_always_on_top(self):
        self._always_on_top = not self._always_on_top
        self.root.attributes("-topmost", self._always_on_top)

    def _show_find(self):
        from findreplace import FindReplace
        fr = FindReplace(self.root, self.editor)
        fr.set_theme(self.current_theme)
        fr.show()

    def _show_settings(self): self._settings_popup.show()

    def _show_themes(self):
        t = self.current_theme
        popup = tk.Toplevel(self.root)
        popup.title("Themes"); popup.geometry("220x340"); popup.configure(bg=t["bg"]); popup.transient(self.root); popup.resizable(False, False)
        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 110
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 170
        popup.geometry(f"+{px}+{py}")
        tk.Label(popup, text="Choose Theme", bg=t["bg"], fg=t["fg"], font=("Segoe UI", 10, "bold")).pack(pady=10)
        for key, data in self.themes.items():
            btn = tk.Label(popup, text=data["name"], bg=t["accent"], fg=t["fg"], font=("Segoe UI", 9), padx=14, pady=6, cursor="hand2")
            btn.pack(fill=tk.X, padx=14, pady=1)
            btn.bind("<Button-1>", lambda e, k=key, p=popup: [self._change_theme(k), p.destroy()])

    def _show_opacity(self):
        t = self.current_theme
        popup = tk.Toplevel(self.root)
        popup.title("Opacity"); popup.geometry("260x110"); popup.configure(bg=t["bg"]); popup.transient(self.root); popup.resizable(False, False)
        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 130
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 55
        popup.geometry(f"+{px}+{py}")
        tk.Label(popup, text="Window Opacity", bg=t["bg"], fg=t["fg"], font=("Segoe UI", 10, "bold")).pack(pady=(10, 2))
        slider = tk.Scale(popup, from_=30, to=100, orient=tk.HORIZONTAL, bg=t["bg"], fg=t["fg"], troughcolor=t.get("slider_trough", t["accent"]), activebackground=t.get("slider_puck", t["gradient_start"]), highlightthickness=0, length=220, bd=0)
        slider.set(int(self.root.attributes("-alpha") * 100))
        slider.pack(pady=4)
        slider.configure(command=lambda v: self.root.attributes("-alpha", float(v)/100))

    def _show_about(self):
        messagebox.showinfo("About LiquidPadPlus", "LiquidPadPlus v1.2\n\nClick 'Sidebar' button in status bar to toggle\nCtrl+Scroll to zoom\nGlass effects | Multiple themes\n\nBuilt with Python & Tkinter")

    def _new_file(self):
        if self.editor.get_text().strip():
            if messagebox.askyesno("New", "Clear current text?"):
                self.editor.clear()
                self.file_path = None
                self.is_modified = False
                self._update_title()
                # Clear session so it doesn't reopen old file on next launch
                self.settings["last_opened_file"] = None
                save_settings(self.settings)
        else:
            self.editor.clear()
            self.file_path = None
            self.is_modified = False
            self._update_title()
            self.settings["last_opened_file"] = None
            save_settings(self.settings)
        self._safe_update()

    def _load_file(self, path):
        for enc in ["utf-8", "cp1252", "latin-1"]:
            try:
                with open(path, "r", encoding=enc) as f: content = f.read()
                self.editor.set_text(content)
                self.file_path = path
                self.is_modified = False
                self._update_title()
                add_recent_file(self.settings, path)
                
                # Update session path
                self.settings["last_opened_file"] = path
                save_settings(self.settings)
                
                self._safe_update()
                return
            except UnicodeDecodeError: continue
        messagebox.showerror("Error", "Could not decode file with any known encoding")

    def _open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path: self._load_file(path)

    def _save_file(self):
        if not self.file_path: return self._save_as_file()
        try:
            with open(self.file_path, "w", encoding="utf-8") as f: f.write(self.editor.get_text())
            self.is_modified = False
            self._update_title()
            self._safe_update()
        except Exception as e: messagebox.showerror("Save Error", str(e))

    def _save_as_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f: f.write(self.editor.get_text())
                self.file_path = path
                self.is_modified = False
                self._update_title()
                add_recent_file(self.settings, path)
                self._safe_update()
            except Exception as e: messagebox.showerror("Save As Error", str(e))

    def _update_title(self):
        base = os.path.basename(self.file_path) if self.file_path else "Untitled"
        marker = "*" if self.is_modified else ""
        self.root.title(f"{marker}{base} - LiquidPadPlus")

    def _mark_modified(self, event=None):
        if not self.is_modified:
            self.is_modified = True
            self._update_title()
            self._safe_update()

if __name__ == "__main__":
    root = tk.Tk()
    app = LiquidPad(root)
    app.editor.text_area.bind("<<Modified>>", lambda e: app._mark_modified(e))
    app.editor.text_area.bind("<KeyRelease>", lambda e: app._safe_update())
    app.editor.text_area.bind("<ButtonRelease>", lambda e: app._safe_update())
    root.mainloop()