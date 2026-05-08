"""
Menu bar component for LiquidPadPlus.
Memory-safe rebuilds, error-handled I/O, live checkmarks, and Recent Files menu.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from findreplace import FindReplace
from settings import get_recent_files, save_settings

class MenuBar:
    def __init__(self, root, editor, statusbar, theme_callback):
        self.root, self.editor, self.statusbar, self.change_theme = root, editor, statusbar, theme_callback
        self.current_file = None
        self.themes = {}
        self.current_theme_name = "glass"
        self.find_replace = None
        self._menu_refs = []

    def setup(self, themes, theme_name):
        self.themes = themes
        self.current_theme_name = theme_name
        self._create_menus()
        self._bind_keys()

    def rebuild(self, theme_name):
        self.current_theme_name = theme_name
        self._create_menus()
        self._bind_keys()
        if self.find_replace and hasattr(self.find_replace, "set_theme"): self.find_replace.set_theme(self._theme())

    def _theme(self):
        return self.themes.get(self.current_theme_name, {"bg":"#1a1a2e","fg":"#ffffff","accent":"#333","text_bg":"#1e1e3a","button_secondary":"#555"})

    def _create_menus(self):
        for m in self._menu_refs:
            try: m.destroy()
            except: pass
        self._menu_refs = []
        t = self._theme()
        self.root.config(menu=None)

        mb = tk.Menu(self.root, bg=t["bg"], fg=t["fg"], activebackground=t["accent"], activeforeground=t["fg"], relief=tk.FLAT, bd=0, font=("Segoe UI", 9))
        self._menu_refs.append(mb); self.root.config(menu=mb)

        def _menu(name):
            m = tk.Menu(mb, tearoff=0, bg=t["bg"], fg=t["fg"], activebackground=t["accent"], activeforeground=t["fg"])
            self._menu_refs.append(m)
            mb.add_cascade(label=name, menu=m)
            return m

        # === FILE MENU ===
        fm = _menu("File")
        fm.add_command(label="New", command=self._new_tab, accelerator="Ctrl+N")
        fm.add_separator()
        fm.add_command(label="Open", command=self._open, accelerator="Ctrl+O")
        
        # Recent Files Submenu
        recent = self._get_recent_files()
        if recent:
            recent_menu = tk.Menu(fm, tearoff=0, bg=t["bg"], fg=t["fg"], activebackground=t["accent"], activeforeground=t["fg"])
            self._menu_refs.append(recent_menu)
            fm.add_cascade(label="Open Recent", menu=recent_menu)
            for path in recent:
                label = os.path.basename(path)
                recent_menu.add_command(label=label, command=lambda p=path: self._open_recent(p))
            recent_menu.add_separator()
            recent_menu.add_command(label="Clear Recent", command=self._clear_recent)
        else:
            fm.add_command(label="Open Recent", state=tk.DISABLED)
            
        fm.add_separator()
        fm.add_command(label="Save", command=self._save, accelerator="Ctrl+S")
        fm.add_command(label="Save As...", command=self._save_as, accelerator="Ctrl+Shift+S")
        fm.add_separator()
        fm.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")

        # === EDIT MENU ===
        em = _menu("Edit")
        em.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        em.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Y")
        em.add_separator()
        em.add_command(label="Cut", command=self._cut, accelerator="Ctrl+X")
        em.add_command(label="Copy", command=self._copy, accelerator="Ctrl+C")
        em.add_command(label="Paste", command=self._paste, accelerator="Ctrl+V")
        em.add_separator()
        em.add_command(label="Select All", command=self._select_all, accelerator="Ctrl+A")
        em.add_separator()
        em.add_command(label="Find & Replace", command=self._show_find_replace, accelerator="Ctrl+F")

        # === VIEW MENU ===
        vm = _menu("View")
        # Themes menu removed as requested
        
        font_m = tk.Menu(vm, tearoff=0, bg=t["bg"], fg=t["fg"], activebackground=t["accent"], activeforeground=t["fg"])
        self._menu_refs.append(font_m)
        vm.add_cascade(label="Font Size", menu=font_m)
        for sz in [8,9,10,11,12,14,16,18,20,24]:
            lbl = f"✓ {sz} pt" if sz == self.editor._font_size else f"{sz} pt"
            font_m.add_command(label=lbl, command=self._font_switcher(sz))

        hm = _menu("Help")
        hm.add_command(label="About", command=self._about)
        hm.add_command(label="Shortcuts", command=self._shortcuts)

    def _get_recent_files(self):
        try: return get_recent_files(self.root._app.settings) if hasattr(self.root, '_app') else []
        except: return []

    def _open_recent(self, path):
        try: self._open_file_direct(path)
        except Exception as e: messagebox.showerror("Open Error", str(e))

    def _clear_recent(self):
        if hasattr(self.root, '_app'):
            self.root._app.settings["recent_files"] = []
            save_settings(self.root._app.settings)
            self._create_menus()

    def _open_file_direct(self, path):
        if hasattr(self.root, '_app'): self.root._app._load_file(path)

    def _theme_switcher(self, name):
        def sw(): self.change_theme(name); self._create_menus()
        return sw
    def _font_switcher(self, sz):
        def sw(): self.editor.set_font_size(sz); self._create_menus()
        return sw

    def _bind_keys(self):
        self.root.bind("<Control-t>", lambda e: self._new_tab())
        self.root.bind("<Control-w>", lambda e: self._close_tab())
        self.root.bind("<Control-o>", lambda e: self._open())
        self.root.bind("<Control-s>", lambda e: self._save())
        self.root.bind("<Control-Shift-S>", lambda e: self._save_as())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-f>", lambda e: self._show_find_replace())

    def _show_find_replace(self):
        if not self.find_replace: self.find_replace = FindReplace(self.root, self.editor)
        self.find_replace.set_theme(self._theme())
        self.find_replace.show()

    def _set_opacity(self, v):
        try: self.root.attributes("-alpha", v); self._create_menus()
        except: pass

    def _new_tab(self): pass
    def _close_tab(self): pass
    def _open(self):
        try:
            path = filedialog.askopenfilename(title="Open", filetypes=[("Text", "*.txt"), ("All", "*.*")])
            if path and os.path.exists(path) and hasattr(self.root, "_app"):
                self.root._app._load_file(path)
        except Exception as e: messagebox.showerror("Open Error", str(e))

    def _save(self):
        try:
            if hasattr(self.root, "_app") and self.root._app.file_path:
                with open(self.root._app.file_path, "w", encoding="utf-8") as f: f.write(self.editor.get_text())
                self.root._app.is_modified = False
                self.root._app._update_title()
            else: self._save_as()
        except Exception as e: messagebox.showerror("Save Error", str(e))

    def _save_as(self):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt"), ("All", "*.*")])
            if path and hasattr(self.root, "_app"):
                with open(path, "w", encoding="utf-8") as f: f.write(self.editor.get_text())
                self.root._app.file_path = path
                self.root._app.is_modified = False
                self.root._app._update_title()
        except Exception as e: messagebox.showerror("Save As Error", str(e))

    def _undo(self):
        try: self.editor.text_area.edit_undo()
        except: pass
    def _redo(self):
        try: self.editor.text_area.edit_redo()
        except: pass
    def _cut(self): self.editor.text_area.event_generate("<<Cut>>")
    def _copy(self): self.editor.text_area.event_generate("<<Copy>>")
    def _paste(self): self.editor.text_area.event_generate("<<Paste>>")
    def _select_all(self): self.editor.text_area.tag_add(tk.SEL, "1.0", tk.END); self.editor.text_area.mark_set(tk.INSERT, "1.0")

    def _about(self):
        messagebox.showinfo("About LiquidPadPlus", "LiquidPadPlus v1.2\n\nClick 'Sidebar' button in status bar to toggle\nCtrl+Scroll to zoom\nGlass effects | Multiple themes\n\nBuilt with Python & Tkinter")
    def _shortcuts(self):
        messagebox.showinfo("Shortcuts", "Ctrl+O  Open\nCtrl+S  Save\nCtrl+Shift+S  Save As\nCtrl+F  Find & Replace\nCtrl+Z/Y  Undo/Redo\nCtrl+Q  Exit")