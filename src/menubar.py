"""
Menu bar component for LiquidPadPlus.
Creates all menus and keyboard shortcuts.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from findreplace import FindReplace


class MenuBar:
    """Application menu bar with File, Edit, View, and Help menus."""
    
    def __init__(self, root, editor, statusbar, theme_callback):
        self.root = root
        self.editor = editor
        self.statusbar = statusbar
        self.change_theme = theme_callback
        self.current_file = None
        self.themes = {}
        self.current_theme_name = "glass"
        self.find_replace = None
        
    def setup(self, themes, theme_name):
        """Set themes and build menus."""
        self.themes = themes
        self.current_theme_name = theme_name
        self._create_menus()
        self._bind_keys()
        self.find_replace = FindReplace(self.root, self.editor)
    
    def rebuild(self, theme_name):
        """Rebuild menus after theme change."""
        self.current_theme_name = theme_name
        self._create_menus()
        self._bind_keys()
        if self.find_replace:
            self.find_replace.set_theme(self._theme())
    
    def _theme(self):
        """Get current theme safely."""
        return self.themes.get(self.current_theme_name, {
            "bg": "#1a1a2e", "fg": "#ffffff", "accent": "#333333", "text_bg": "#1e1e3a"
        })
    
    def _create_menus(self):
        """Create all menus."""
        t = self._theme()
        
        blank = tk.Menu(self.root)
        self.root.config(menu=blank)
        
        menubar = tk.Menu(
            self.root,
            bg=t["bg"],
            fg=t["fg"],
            activebackground=t["accent"],
            activeforeground=t["fg"],
            relief=tk.FLAT,
            bd=0,
            font=('Segoe UI', 9)
        )
        self.root.config(menu=menubar)
        
        # === FILE MENU ===
        file_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Tab", command=self._new_tab, accelerator="Ctrl+T")
        file_menu.add_command(label="Close Tab", command=self._close_tab, accelerator="Ctrl+W")
        file_menu.add_separator()
        file_menu.add_command(label="Open", command=self._open, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self._save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # === EDIT MENU ===
        edit_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self._cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self._copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self._paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self._select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find & Replace", command=self._show_find_replace, accelerator="Ctrl+F")
        
        # === VIEW MENU ===
        view_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Transparency
        trans_menu = tk.Menu(view_menu, tearoff=0, bg=t["bg"], fg=t["fg"],
                            activebackground=t["accent"], activeforeground=t["fg"])
        view_menu.add_cascade(label="Transparency", menu=trans_menu)
        for pct in [95, 90, 85, 80, 75, 70, 60, 50]:
            trans_menu.add_command(
                label=f"{pct}%",
                command=lambda v=pct: self._set_opacity(v/100)
            )
        
        # Themes
        theme_menu = tk.Menu(view_menu, tearoff=0, bg=t["bg"], fg=t["fg"],
                            activebackground=t["accent"], activeforeground=t["fg"])
        view_menu.add_cascade(label="Themes", menu=theme_menu)
        
        glass = [(k, v) for k, v in self.themes.items() if v.get("glass_effect")]
        normal = [(k, v) for k, v in self.themes.items() if not v.get("glass_effect")]
        
        for key, data in glass:
            theme_menu.add_command(label=data["name"], command=self._theme_switcher(key))
        if glass:
            theme_menu.add_separator()
        for key, data in normal:
            theme_menu.add_command(label=data["name"], command=self._theme_switcher(key))
        
        # Font size
        font_menu = tk.Menu(view_menu, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        view_menu.add_cascade(label="Font Size", menu=font_menu)
        for size in [8, 9, 10, 11, 12, 14, 16, 18, 20, 24]:
            font_menu.add_command(label=f"{size} pt", command=self._font_switcher(size))
        
        # === HELP MENU ===
        help_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About LiquidPadPlus", command=self._about)
        help_menu.add_command(label="Shortcuts", command=self._shortcuts)
    
    def _theme_switcher(self, name):
        return lambda: self.change_theme(name)
    
    def _font_switcher(self, size):
        return lambda: self.editor.set_font_size(size)
    
    def _bind_keys(self):
        """Bind keyboard shortcuts."""
        self.root.bind('<Control-t>', lambda e: self._new_tab())
        self.root.bind('<Control-w>', lambda e: self._close_tab())
        self.root.bind('<Control-o>', lambda e: self._open())
        self.root.bind('<Control-s>', lambda e: self._save())
        self.root.bind('<Control-S>', lambda e: self._save_as())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-f>', lambda e: self._show_find_replace())
    
    def _show_find_replace(self):
        if self.find_replace:
            self.find_replace.set_theme(self._theme())
            self.find_replace.show()
    
    # ---- Actions ----
    
    def _set_opacity(self, value):
        self.root.attributes('-alpha', value)
    
    def _new_tab(self):
        if hasattr(self.root, '_app') and hasattr(self.root._app, 'tab_manager'):
            self.root._app.tab_manager.add_tab()
    
    def _close_tab(self):
        if hasattr(self.root, '_app') and hasattr(self.root._app, 'tab_manager'):
            tm = self.root._app.tab_manager
            if tm.active_tab:
                tm.close_tab(tm.active_tab)
    
    def _open(self):
        path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            if hasattr(self.root, '_app') and hasattr(self.root._app, 'tab_manager'):
                self.root._app.tab_manager.add_tab(file_path=path)
    
    def _save(self):
        if hasattr(self.root, '_app') and hasattr(self.root._app, 'tab_manager'):
            tm = self.root._app.tab_manager
            active_file = tm.get_active_file()
            editor = tm.get_active_editor()
            
            if active_file and editor:
                with open(active_file, 'w', encoding='utf-8') as f:
                    f.write(editor.get_text())
                self.root.title(f"LiquidPadPlus - {os.path.basename(active_file)}")
            else:
                self._save_as()
    
    def _save_as(self):
        path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path and hasattr(self.root, '_app') and hasattr(self.root._app, 'tab_manager'):
            tm = self.root._app.tab_manager
            editor = tm.get_active_editor()
            if editor:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(editor.get_text())
                tm.set_active_file(path)
                self.root.title(f"LiquidPadPlus - {os.path.basename(path)}")
    
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
    
    def _cut(self):
        self.editor.text_area.event_generate("<<Cut>>")
    
    def _copy(self):
        self.editor.text_area.event_generate("<<Copy>>")
    
    def _paste(self):
        self.editor.text_area.event_generate("<<Paste>>")
    
    def _select_all(self):
        self.editor.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.text_area.mark_set(tk.INSERT, "1.0")
    
    def get_filename(self):
        if hasattr(self.root, '_app') and hasattr(self.root._app, 'tab_manager'):
            f = self.root._app.tab_manager.get_active_file()
            return os.path.basename(f) if f else "Untitled"
        return "Untitled"
    
    def get_opacity(self):
        return int(self.root.attributes('-alpha') * 100)
    
    def _about(self):
        messagebox.showinfo("About LiquidPadPlus",
            "LiquidPadPlus v1.0\n\n"
            "LiquidPad with experimental features.\n"
            "Tabs | Find & Replace\n"
            "Glass effects | Live stats\n\n"
            "Built with Python & Tkinter")
    
    def _shortcuts(self):
        messagebox.showinfo("Shortcuts",
            "Ctrl+N/T  New Tab\n"
            "Ctrl+W    Close Tab\n"
            "Ctrl+O    Open\n"
            "Ctrl+S    Save\n"
            "Ctrl+Shift+S  Save As\n"
            "Ctrl+Q    Exit\n\n"
            "Ctrl+Z    Undo\n"
            "Ctrl+Y    Redo\n"
            "Ctrl+X    Cut\n"
            "Ctrl+C    Copy\n"
            "Ctrl+V    Paste\n"
            "Ctrl+A    Select All\n"
            "Ctrl+F    Find & Replace")