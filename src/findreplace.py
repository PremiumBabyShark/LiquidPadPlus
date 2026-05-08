"""
Find and Replace dialog for LiquidPadPlus.
Robust search, contrast-safe highlighting, and memory-safe cleanup.
"""

import tkinter as tk
from tkinter import messagebox
import re

class FindReplace:
    def __init__(self, parent, editor):
        self.parent = parent
        self.editor = editor
        self.text_area = editor.text_area
        self.dialog = None
        self.find_entry = None
        self.replace_entry = None
        self.match_case_var = None
        self.whole_word_var = None
        self.current_theme = {"bg": "#1a1a2e", "fg": "#e0e0e0", "accent": "#0f3460", "text_bg": "#16213e"}
        self.last_search_pos = "1.0"
        self._highlight_tag = "search_highlight"

    def set_theme(self, theme): self.current_theme = theme

    def show(self):
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.lift()
            self.find_entry.focus_set()
            return
        t = self.current_theme
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Find & Replace")
        self.dialog.geometry("450x220")
        self.dialog.configure(bg=t["bg"])
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self._center_dialog()
        self._build_ui(t)
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        self.find_entry.focus_set()

    def _build_ui(self, t):
        f1 = tk.Frame(self.dialog, bg=t["bg"])
        f1.pack(fill=tk.X, padx=15, pady=(15, 5))
        tk.Label(f1, text="Find:", bg=t["bg"], fg=t["fg"], font=("Segoe UI", 10), width=8, anchor=tk.W).pack(side=tk.LEFT)
        self.find_entry = tk.Entry(f1, bg=t.get("text_bg", t["bg"]), fg=t["fg"], insertbackground=t["fg"], font=("Consolas", 10), relief=tk.FLAT, bd=2)
        self.find_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        f2 = tk.Frame(self.dialog, bg=t["bg"])
        f2.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(f2, text="Replace:", bg=t["bg"], fg=t["fg"], font=("Segoe UI", 10), width=8, anchor=tk.W).pack(side=tk.LEFT)
        self.replace_entry = tk.Entry(f2, bg=t.get("text_bg", t["bg"]), fg=t["fg"], insertbackground=t["fg"], font=("Consolas", 10), relief=tk.FLAT, bd=2)
        self.replace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        f3 = tk.Frame(self.dialog, bg=t["bg"])
        f3.pack(fill=tk.X, padx=15, pady=5)
        self.match_case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(f3, text="Match case", variable=self.match_case_var, bg=t["bg"], fg=t["fg"], selectcolor=t["accent"], activebackground=t["bg"], activeforeground=t["fg"], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 15))
        self.whole_word_var = tk.BooleanVar(value=False)
        tk.Checkbutton(f3, text="Whole word", variable=self.whole_word_var, bg=t["bg"], fg=t["fg"], selectcolor=t["accent"], activebackground=t["bg"], activeforeground=t["fg"], font=("Segoe UI", 9)).pack(side=tk.LEFT)

        f4 = tk.Frame(self.dialog, bg=t["bg"])
        f4.pack(fill=tk.X, padx=15, pady=(10, 15))
        bs = {"font": ("Segoe UI", 9), "relief": tk.FLAT, "bd": 0, "padx": 12, "pady": 4, "cursor": "hand2"}
        tk.Button(f4, text="Find Next", bg=t["accent"], fg=t["fg"], command=self.find_next, **bs).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(f4, text="Replace", bg=t["accent"], fg=t["fg"], command=self.replace_one, **bs).pack(side=tk.LEFT, padx=5)
        tk.Button(f4, text="Replace All", bg=t["accent"], fg=t["fg"], command=self.replace_all, **bs).pack(side=tk.LEFT, padx=5)
        tk.Button(f4, text="Close", bg=t.get("button_secondary", "#555"), fg=t["fg"], command=self._on_close, **bs).pack(side=tk.RIGHT)

        self.dialog.bind("<Return>", lambda e: self.find_next())
        self.dialog.bind("<Escape>", lambda e: self._on_close())
        self.dialog.bind("<Control-f>", lambda e: self.find_entry.focus_set())
        self.dialog.bind("<Control-r>", lambda e: self.replace_one())

    def _center_dialog(self):
        self.dialog.update_idletasks()
        px, py = self.parent.winfo_rootx(), self.parent.winfo_rooty()
        pw, ph = self.parent.winfo_width(), self.parent.winfo_height()
        dw, dh = self.dialog.winfo_width(), self.dialog.winfo_height()
        self.dialog.geometry(f"+{px + (pw//2) - (dw//2)}+{py + (ph//2) - (dh//2)}")

    def _on_close(self):
        self._clear_highlights()
        self.last_search_pos = "1.0"
        if self.dialog and self.dialog.winfo_exists(): self.dialog.destroy()
        self.dialog = None

    def _get_search_args(self):
        s = self.find_entry.get().strip()
        return (s, self.replace_entry.get(), self.match_case_var.get(), self.whole_word_var.get()) if s else (None, None, None, None)

    @staticmethod
    def _is_dark(bg):
        try:
            bg = bg.lstrip("#")
            if len(bg) == 3: bg = "".join(c*2 for c in bg)
            r, g, b = [int(bg[i:i+2], 16) for i in (0, 2, 4)]
            return (0.299*r + 0.587*g + 0.114*b) < 128
        except: return True

    def find_next(self):
        search, _, case, whole = self._get_search_args()
        if not search: return
        self._clear_highlights()
        pos = self._search(self.last_search_pos, search, case, whole)
        if pos:
            end = f"{pos}+{len(search)}c"
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_area.tag_add(tk.SEL, pos, end)
            self.text_area.mark_set(tk.INSERT, end)
            self.text_area.see(pos)
            self._highlight_all(search, case, whole)
            self.last_search_pos = end
        else:
            self.last_search_pos = "1.0"
            pos = self._search("1.0", search, case, whole)
            if pos: self.find_next()
            else:
                messagebox.showinfo("Find", f"'{search}' not found.")
                self.last_search_pos = "1.0"

    def _search(self, start, text, case, whole):
        if whole:
            esc = text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("*", "\\*")
            return self.text_area.search(f"\\y{esc}\\Y", start, stopindex=tk.END, nocase=not case, regexp=True)
        return self.text_area.search(text, start, stopindex=tk.END, nocase=not case, regexp=False)

    def _highlight_all(self, text, case, whole):
        self._clear_highlights()
        is_dark = self._is_dark(self.current_theme.get("bg", "#1a1a2e"))
        self.text_area.tag_configure(self._highlight_tag, background="#ffff00" if is_dark else "#ffaa00", foreground="#000" if is_dark else "#fff")
        pos, count = "1.0", 0
        while count < 500:
            p = self._search(pos, text, case, whole)
            if not p: break
            self.text_area.tag_add(self._highlight_tag, p, f"{p}+{len(text)}c")
            pos = f"{p}+{len(text)}c"
            count += 1

    def _clear_highlights(self):
        try: self.text_area.tag_remove(self._highlight_tag, "1.0", tk.END)
        except: pass

    def replace_one(self):
        search, repl, case, whole = self._get_search_args()
        if not search: return
        try:
            s, e = self.text_area.index(tk.SEL_FIRST), self.text_area.index(tk.SEL_LAST)
            sel = self.text_area.get(s, e)
            if (sel == search) or (not case and sel.lower() == search.lower()):
                self.text_area.delete(s, e)
                self.text_area.insert(s, repl)
                self.last_search_pos = self.text_area.index(f"{s}+{len(repl)}c")
        except: pass
        self.find_next()

    def replace_all(self):
        search, repl, case, whole = self._get_search_args()
        if not search: return
        matches, pos, count = [], "1.0", 0
        while count < 1000:
            p = self._search(pos, search, case, whole)
            if not p: break
            matches.append((p, f"{p}+{len(search)}c"))
            pos = f"{p}+{len(search)}c"
            count += 1
        for s, e in reversed(matches):
            self.text_area.delete(s, e)
            self.text_area.insert(s, repl)
        self._clear_highlights()
        messagebox.showinfo("Replace All", f"Replaced {count} occurrence(s).")