"""
Text editor component for LiquidPadPlus.
Optimized line numbers, smart undo, and seamless scroll sync.
"""

import tkinter as tk

class Editor:
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.text_area = None
        self.line_numbers = None
        self.gutter_sep = None
        self._scrollbar = None
        self.container = None
        self._font_family = "JetBrains Mono"
        self._font_size = 12
        self._after_id = None
        self._last_line_count = 0
        self._build()

    def _build(self):
        t = self.theme
        self.container = tk.Frame(self.parent, bg=t["bg"])
        self.container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(self.container, width=4, padx=8, pady=18, bg=t["accent"], fg=t["gradient_start"],
                                    font=(self._font_family, self._font_size), relief=tk.FLAT, bd=0, highlightthickness=0,
                                    state=tk.DISABLED, wrap=tk.NONE, cursor="arrow", spacing1=3, spacing2=2, spacing3=3, takefocus=False)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.gutter_sep = tk.Frame(self.container, bg=t["border"], width=1)
        self.gutter_sep.pack(side=tk.LEFT, fill=tk.Y)

        self.text_area = tk.Text(self.container, wrap=tk.WORD, undo=True, autoseparators=False, bg=t["text_bg"], fg=t["fg"],
                                 insertbackground=t["cursor"], selectbackground=t["select_bg"], selectforeground=t["fg"],
                                 relief=tk.FLAT, bd=0, padx=20, pady=18, font=(self._font_family, self._font_size),
                                 highlightthickness=0, borderwidth=0, spacing1=3, spacing2=2, spacing3=3)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._scrollbar = tk.Scrollbar(self.container, bg=t["accent"], troughcolor=t["text_bg"], activebackground=t["gradient_start"],
                                       width=8, relief=tk.FLAT, bd=0, highlightthickness=0)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area.config(yscrollcommand=self._on_text_scroll)
        self._scrollbar.config(command=lambda *args: (self.line_numbers.yview(*args), self.text_area.yview(*args)))

        self.line_numbers.bind("<MouseWheel>", self._redirect_scroll)
        self.line_numbers.bind("<Button-4>", self._redirect_scroll)
        self.line_numbers.bind("<Button-5>", self._redirect_scroll)

        self.text_area.bind("<<Modified>>", self._on_modified)
        self.text_area.bind("<KeyRelease>", self._smart_undo_sep)
        self.text_area.bind("<ButtonRelease>", lambda e: self.text_area.edit_separator())

        self.text_area.focus_set()
        self._update_line_numbers()

    def _on_text_scroll(self, first, last):
        self.line_numbers.yview_moveto(first)
        self._scrollbar.set(first, last)

    def _redirect_scroll(self, event):
        if event.num == 4: self.text_area.yview_scroll(-1, "units")
        elif event.num == 5: self.text_area.yview_scroll(1, "units")
        else: self.text_area.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    def _on_modified(self, event=None):
        self.text_area.edit_modified(False)
        self._schedule_update()

    def _schedule_update(self):
        if self._after_id: self.text_area.after_cancel(self._after_id)
        self._after_id = self.text_area.after(10, self._update_line_numbers)

    def _smart_undo_sep(self, event=None):
        if event and event.keysym in ("Return", "space", "BackSpace", "Delete"):
            try: self.text_area.edit_separator()
            except: pass

    def _update_line_numbers(self):
        self._after_id = None
        line_count = int(self.text_area.index("end-1c").split(".")[0])
        if line_count == self._last_line_count: return
        self._last_line_count = line_count

        digits = len(str(line_count))
        new_width = max(4, digits + 1)
        if self.line_numbers.cget("width") != new_width:
            self.line_numbers.config(width=new_width)

        numbers = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", numbers)
        self.line_numbers.config(state=tk.DISABLED)
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

    def get_text(self): return self.text_area.get("1.0", "end-1c")

    def set_text(self, content):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content.replace("\r\n", "\n").replace("\r", "\n"))
        self._last_line_count = 0
        self._update_line_numbers()
        self.text_area.edit_modified(False)

    def clear(self):
        self.text_area.delete("1.0", tk.END)
        self._last_line_count = 0
        self._update_line_numbers()
        self.text_area.edit_modified(False)

    def get_stats(self):
        text = self.get_text()
        return (len(text.split()), len(text)) if text.strip() else (0, 0)

    def set_font_size(self, size):
        self._font_size = size
        font = (self._font_family, size)
        self.text_area.configure(font=font)
        self.line_numbers.configure(font=font)

    def update_theme(self, theme):
        self.theme = theme
        t = theme
        self.container.configure(bg=t["bg"])
        self.text_area.configure(bg=t["text_bg"], fg=t["fg"], insertbackground=t["cursor"], selectbackground=t["select_bg"], selectforeground=t["fg"])
        self.line_numbers.configure(bg=t["accent"], fg=t["gradient_start"])
        self.gutter_sep.configure(bg=t["border"])
        self._scrollbar.configure(bg=t["accent"], troughcolor=t["text_bg"], activebackground=t["gradient_start"])