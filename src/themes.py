"""
Theme definitions for LiquidPadPlus.
Validated, safe-access color palettes with automatic dark/light detection.
"""

_THEMES_DATA = {
    "onyx": {
        "name": "🖤 Onyx", "glass_effect": True,
        "bg": "#0f0f14", "text_bg": "#16161d", "fg": "#d4d4dc",
        "cursor": "#c4a7e7", "select_bg": "#2d2d3a",
        "accent": "#1a1a24", "accent_hover": "#222230", "accent_active": "#8888aa",
        "border": "#1e1e2a", "tab_active": "#252535", "tab_inactive": "#1a1a24",
        "status_bg": "#0a0a10", "gradient_start": "#c4a7e7", "gradient_end": "#7aa2f7",
        "sidebar_bg": "#0d0d16", "slider_trough": "#2a2a3a", "slider_puck": "#c4a7e7"
    },
    "graphite": {
        "name": "⬛ Graphite", "glass_effect": False,
        "bg": "#1c1c24", "text_bg": "#22222c", "fg": "#e0e0e8",
        "cursor": "#fca5a5", "select_bg": "#3a3a48",
        "accent": "#262630", "accent_hover": "#2e2e3a", "accent_active": "#888899",
        "border": "#2a2a36", "tab_active": "#303040", "tab_inactive": "#262630",
        "status_bg": "#16161e", "gradient_start": "#fca5a5", "gradient_end": "#f9a8d4",
        "sidebar_bg": "#14141a", "slider_trough": "#323242", "slider_puck": "#fca5a5"
    },
    "paper": {
        "name": "📄 Paper", "glass_effect": False,
        "bg": "#f5f0e8", "text_bg": "#faf7f2", "fg": "#3d3828",
        "cursor": "#c4a7e7", "select_bg": "#e8e0d0",
        "accent": "#ede8e0", "accent_hover": "#e5dfd5", "accent_active": "#999080",
        "border": "#e0d8c8", "tab_active": "#ffffff", "tab_inactive": "#ede8e0",
        "status_bg": "#ebe4d8", "gradient_start": "#b8a080", "gradient_end": "#c4a7e7",
        "sidebar_bg": "#e8e0d4", "slider_trough": "#d5ccbc", "slider_puck": "#b8a080"
    },
    "ocean_dark": {
        "name": "🌊 Ocean Dark", "glass_effect": True,
        "bg": "#0a1628", "text_bg": "#0f1f35", "fg": "#c4ddf6",
        "cursor": "#7dcfff", "select_bg": "#1a3550",
        "accent": "#111d30", "accent_hover": "#162538", "accent_active": "#7799bb",
        "border": "#162538", "tab_active": "#1b3050", "tab_inactive": "#111d30",
        "status_bg": "#060e1a", "gradient_start": "#7dcfff", "gradient_end": "#5eead4",
        "sidebar_bg": "#081220", "slider_trough": "#1a2a40", "slider_puck": "#7dcfff"
    },
    "midnight": {
        "name": "🌑 Midnight", "glass_effect": False,
        "bg": "#0d1117", "text_bg": "#161b22", "fg": "#c9d1d9",
        "cursor": "#58a6ff", "select_bg": "#264f78",
        "accent": "#161b26", "accent_hover": "#1c2433", "accent_active": "#8899aa",
        "border": "#21262d", "tab_active": "#1f2a3a", "tab_inactive": "#161b26",
        "status_bg": "#0a0e13", "gradient_start": "#58a6ff", "gradient_end": "#3fb950",
        "sidebar_bg": "#090d13", "slider_trough": "#1c2433", "slider_puck": "#58a6ff"
    },
    "forest": {
        "name": " Forest", "glass_effect": False,
        "bg": "#0f1a0f", "text_bg": "#162416", "fg": "#c8dcc8",
        "cursor": "#6fcf6f", "select_bg": "#1f3a1f",
        "accent": "#141f14", "accent_hover": "#1a281a", "accent_active": "#779977",
        "border": "#1a2a1a", "tab_active": "#1f301f", "tab_inactive": "#141f14",
        "status_bg": "#0a120a", "gradient_start": "#6fcf6f", "gradient_end": "#4ecdc4",
        "sidebar_bg": "#0a150a", "slider_trough": "#1a2a1a", "slider_puck": "#6fcf6f"
    },
    "rose": {
        "name": "🌹 Rose", "glass_effect": True,
        "bg": "#1a1018", "text_bg": "#241822", "fg": "#e8d4e4",
        "cursor": "#f0a0c0", "select_bg": "#3d2035",
        "accent": "#20141e", "accent_hover": "#281a26", "accent_active": "#997788",
        "border": "#281a26", "tab_active": "#352030", "tab_inactive": "#20141e",
        "status_bg": "#120a10", "gradient_start": "#f0a0c0", "gradient_end": "#d4a0f0",
        "sidebar_bg": "#140c12", "slider_trough": "#2a1a28", "slider_puck": "#f0a0c0"
    }
}

DEFAULT_THEME = "onyx"
_REQUIRED_KEYS = {"name", "bg", "text_bg", "fg", "cursor", "select_bg", "accent", "accent_hover", "accent_active", "border", "tab_active", "tab_inactive", "status_bg", "gradient_start", "gradient_end", "sidebar_bg", "slider_trough", "slider_puck"}
_FALLBACK = {"glass_effect": False, "slider_trough": "#333333", "slider_puck": "#888888", "accent_active": "#777777", "accent_hover": "#2a2a2a"}

def _norm_hex(c):
    """Safely normalize any hex string to #RRGGBB"""
    if not isinstance(c, str): return "#888888"
    c = c.strip().lower()
    if c.startswith("#"): c = c[1:]
    if len(c) == 3: c = "".join(ch*2 for ch in c)
    if len(c) < 6: c = c[:6].ljust(6, "0")
    return f"#{c[:6]}"

def _luminance(hex_color):
    """Calculate perceived brightness (0-255)"""
    h = _norm_hex(hex_color)[1:]  # Remove #
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return 0.299*r + 0.587*g + 0.114*b

def validate_theme(data):
    v = dict(data)
    for k in _REQUIRED_KEYS:
        if k not in v: v[k] = _FALLBACK.get(k, "#888888")
        elif k not in ("name", "glass_effect"): v[k] = _norm_hex(v[k])
    v.setdefault("is_dark", _luminance(v["bg"]) < 128)
    v.setdefault("glass_effect", False)
    return v

def get_theme(name):
    if name in _THEMES_DATA: return validate_theme(_THEMES_DATA[name])
    return validate_theme(_THEMES_DATA[DEFAULT_THEME])

def list_themes():
    return sorted([(k, validate_theme(v)) for k, v in _THEMES_DATA.items()], key=lambda x: x[1]["name"].lstrip("🌹🌊🌲🌑📄⬛"))

# Export validated themes for backward compatibility
THEMES = {k: validate_theme(v) for k, v in _THEMES_DATA.items()}