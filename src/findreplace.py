"""
Find and Replace dialog for LiquidPad.
Provides search, replace, and replace-all functionality.
"""

import tkinter as tk
from tkinter import messagebox


class FindReplace:
    """Find and Replace dialog for text editor."""
    
    def __init__(self, parent, editor):
        """
        Initialize Find & Replace.
        
        Args:
            parent: Tkinter root window
            editor: Editor instance with .text_area
        """
        self.parent = parent
        self.editor = editor
        self.text_area = editor.text_area
        
        self.dialog = None
        self.find_entry = None
        self.replace_entry = None
        self.match_case_var = None
        self.whole_word_var = None
        self.current_theme = {"bg": "#1a1a2e", "fg": "#e0e0e0", "accent": "#0f3460"}
        
        # Track last search position
        self.last_search_pos = "1.0"
        
    def set_theme(self, theme):
        """Update dialog theme to match main app."""
        self.current_theme = theme
    
    def show(self):
        """Open the Find & Replace dialog."""
        if self.dialog and self.dialog.winfo_exists():
            self.dialog.lift()
            self.dialog.focus_force()
            return
        
        t = self.current_theme
        
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Find & Replace")
        self.dialog.geometry("450x220")
        self.dialog.configure(bg=t["bg"])
        self.dialog.resizable(False, False)
        
        # Make it float on top
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center relative to parent
        self._center_dialog()
        
        # === Find row ===
        find_frame = tk.Frame(self.dialog, bg=t["bg"])
        find_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        tk.Label(find_frame, text="Find:", bg=t["bg"], fg=t["fg"],
                font=('Segoe UI', 10), width=8, anchor=tk.W).pack(side=tk.LEFT)
        
        self.find_entry = tk.Entry(
            find_frame,
            bg=t["text_bg"],
            fg=t["fg"],
            insertbackground=t["fg"],
            font=('Consolas', 10),
            relief=tk.FLAT,
            bd=2
        )
        self.find_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.find_entry.focus_set()
        
        # === Replace row ===
        replace_frame = tk.Frame(self.dialog, bg=t["bg"])
        replace_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(replace_frame, text="Replace:", bg=t["bg"], fg=t["fg"],
                font=('Segoe UI', 10), width=8, anchor=tk.W).pack(side=tk.LEFT)
        
        self.replace_entry = tk.Entry(
            replace_frame,
            bg=t["text_bg"],
            fg=t["fg"],
            insertbackground=t["fg"],
            font=('Consolas', 10),
            relief=tk.FLAT,
            bd=2
        )
        self.replace_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # === Options ===
        options_frame = tk.Frame(self.dialog, bg=t["bg"])
        options_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.match_case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_frame,
            text="Match case",
            variable=self.match_case_var,
            bg=t["bg"],
            fg=t["fg"],
            selectcolor=t["accent"],
            activebackground=t["bg"],
            activeforeground=t["fg"],
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        self.whole_word_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_frame,
            text="Whole word",
            variable=self.whole_word_var,
            bg=t["bg"],
            fg=t["fg"],
            selectcolor=t["accent"],
            activebackground=t["bg"],
            activeforeground=t["fg"],
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT)
        
        # === Buttons ===
        btn_frame = tk.Frame(self.dialog, bg=t["bg"])
        btn_frame.pack(fill=tk.X, padx=15, pady=(10, 15))
        
        btn_style = {
            'font': ('Segoe UI', 9),
            'relief': tk.FLAT,
            'bd': 0,
            'padx': 12,
            'pady': 4,
            'cursor': 'hand2'
        }
        
        tk.Button(btn_frame, text="Find Next", bg=t["accent"], fg=t["fg"],
                 command=self.find_next, **btn_style).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(btn_frame, text="Replace", bg=t["accent"], fg=t["fg"],
                 command=self.replace_one, **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Replace All", bg=t["accent"], fg=t["fg"],
                 command=self.replace_all, **btn_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Close", bg="#555555", fg=t["fg"],
                 command=self.dialog.destroy, **btn_style).pack(side=tk.RIGHT)
        
        # Keyboard shortcuts within dialog
        self.dialog.bind('<Return>', lambda e: self.find_next())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        self.dialog.bind('<Control-f>', lambda e: self._focus_find())
        self.dialog.bind('<Control-r>', lambda e: self.replace_one())
        
        # When dialog closes
        self.dialog.protocol("WM_DELETE_WINDOW", self.dialog.destroy)
    
    def _center_dialog(self):
        """Center dialog relative to parent window."""
        self.dialog.update_idletasks()
        
        # Get parent position and size
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        
        # Get dialog size
        dw = self.dialog.winfo_width()
        dh = self.dialog.winfo_height()
        
        # Calculate center position
        x = px + (pw // 2) - (dw // 2)
        y = py + (ph // 2) - (dh // 2)
        
        self.dialog.geometry(f'+{x}+{y}')
    
    def _focus_find(self):
        """Focus the find entry field."""
        if self.find_entry:
            self.find_entry.focus_set()
    
    def _get_search_args(self):
        """Get search parameters from dialog."""
        search_text = self.find_entry.get()
        if not search_text:
            return None, None, None, None
        
        match_case = self.match_case_var.get()
        whole_word = self.whole_word_var.get()
        replace_text = self.replace_entry.get()
        
        return search_text, replace_text, match_case, whole_word
    
    def find_next(self):
        """Find next occurrence of search text."""
        search_text, _, match_case, whole_word = self._get_search_args()
        if not search_text:
            return
        
        # Remove previous highlights
        self._clear_highlights()
        
        # Start searching from current position
        start_pos = self.last_search_pos
        
        # Find the text
        pos = self._search(start_pos, search_text, match_case, whole_word)
        
        if pos:
            line, col = pos.split('.')
            end_pos = f"{line}.{int(col) + len(search_text)}"
            
            # Select the found text
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_area.tag_add(tk.SEL, pos, end_pos)
            self.text_area.mark_set(tk.INSERT, end_pos)
            self.text_area.see(pos)
            
            # Highlight all matches
            self._highlight_all(search_text, match_case, whole_word)
            
            # Update last position for next search
            self.last_search_pos = end_pos
        else:
            # Wrap around
            self.last_search_pos = "1.0"
            pos = self._search("1.0", search_text, match_case, whole_word)
            
            if pos:
                self.find_next()
            else:
                messagebox.showinfo("Find", f"'{search_text}' not found.")
                self.last_search_pos = "1.0"
    
    def _search(self, start_pos, text, match_case, whole_word):
        """Search for text from a position. Returns position or None."""
        # Configure search options
        nocase = not match_case
        regexp = False
        
        if whole_word:
            # Use regex for whole word search
            import re
            regexp = True
            text = f"\\m{re.escape(text)}\\M"
        
        pos = self.text_area.search(
            text, start_pos,
            stopindex=tk.END,
            nocase=nocase,
            regexp=regexp
        )
        
        return pos
    
    def _highlight_all(self, text, match_case, whole_word):
        """Highlight all occurrences of search text."""
        self._clear_highlights()
        
        # Configure tag for highlighting
        self.text_area.tag_configure(
            "search_highlight",
            background="#ffff00" if self.current_theme.get("glass_effect") or 
                        self.current_theme["bg"] < "#808080" else "#ffaa00",
            foreground="#000000"
        )
        
        start_pos = "1.0"
        count = 0
        while count < 500:  # Safety limit
            pos = self._search(start_pos, text, match_case, whole_word)
            if not pos:
                break
            
            line, col = pos.split('.')
            end_pos = f"{line}.{int(col) + len(text)}"
            
            self.text_area.tag_add("search_highlight", pos, end_pos)
            start_pos = end_pos
            count += 1
    
    def _clear_highlights(self):
        """Remove all search highlights."""
        self.text_area.tag_delete("search_highlight")
    
    def replace_one(self):
        """Replace current selection and find next."""
        search_text, replace_text, match_case, whole_word = self._get_search_args()
        if not search_text:
            return
        
        # Check if current selection matches search text
        try:
            selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            if self._matches(selected, search_text, match_case, whole_word):
                # Replace the selection
                self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
                self.text_area.insert(tk.INSERT, replace_text)
                self.last_search_pos = self.text_area.index(tk.INSERT)
        except tk.TclError:
            pass  # No selection
        
        # Find next
        self.find_next()
    
    def replace_all(self):
        """Replace all occurrences of search text."""
        search_text, replace_text, match_case, whole_word = self._get_search_args()
        if not search_text:
            return
        
        # Save cursor position
        original_pos = self.text_area.index(tk.INSERT)
        
        # Start from beginning
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.last_search_pos = "1.0"
        
        count = 0
        max_replace = 1000  # Safety limit
        
        while count < max_replace:
            pos = self._search(self.last_search_pos, search_text, match_case, whole_word)
            if not pos:
                break
            
            line, col = pos.split('.')
            end_pos = f"{line}.{int(col) + len(search_text)}"
            
            # Select and replace
            self.text_area.delete(pos, end_pos)
            self.text_area.insert(pos, replace_text)
            
            # Update position
            new_end = f"{line}.{int(col) + len(replace_text)}"
            self.last_search_pos = new_end
            count += 1
        
        # Restore cursor
        self.text_area.mark_set(tk.INSERT, original_pos)
        self._clear_highlights()
        
        messagebox.showinfo("Replace All", f"Replaced {count} occurrence(s).")
    
    def _matches(self, text, search_text, match_case, whole_word):
        """Check if text matches search criteria."""
        if match_case:
            if text != search_text:
                return False
        else:
            if text.lower() != search_text.lower():
                return False
        
        if whole_word:
            import re
            pattern = f"\\b{re.escape(search_text)}\\b"
            flags = 0 if match_case else re.IGNORECASE
            return bool(re.match(pattern, text, flags))
        
        return True