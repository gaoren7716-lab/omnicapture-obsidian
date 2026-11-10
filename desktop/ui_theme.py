import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

THEMES = {
    "dark": {
        "name": "dark",
        "label": "深色石墨",
        "bg_root": "#1E2028",          # 温暖深石墨灰 (Apple macOS Sequoia 质感)
        "bg_outer_border": "#363948",  # 外边框微描边
        "bg_card": "#272A36",          # 悬浮卡片层
        "bg_input": "#181920",         # 凹槽输入区 (柔和深邃而不死黑)
        "input_border": "#343746",     # 输入框边缘
        "text_primary": "#FFFFFF",     # 纯白一级标题 (超高清晰度)
        "text_body": "#F2F4FC",        # 高清正文
        "text_secondary": "#A6A9BC",   # 次级文字
        "text_muted": "#7A7E94",       # 占位/热键提示
        "accent_blue": "#0A84FF",      # 苹果蓝
        "accent_blue_hover": "#0071E3",
        "accent_green": "#34C759",     # 苹果精炼翡翠绿 (柔和高端，非死板荧光绿)
        "accent_green_hover": "#30B752",
        "accent_orange": "#FF9F0A",    # 苹果橙
        "tag_bg": "#2E3140",           # 药丸标签常态底色
        "tag_hover": "#3A3D50",
        "tag_fg": "#88BCFF",           # 标签字
        "tag_active_bg": "#0A84FF",    # 激活药丸底色
        "tag_active_hover": "#0071E3",
        "tag_active_fg": "#FFFFFF",    # 激活药丸字
        "btn_pill_bg": "#34C759",      # 提交药丸主色
        "btn_pill_hover": "#30B752",
        "btn_pill_fg": "#FFFFFF",
        "btn_primary_bg": "#0A84FF",
        "btn_primary_hover": "#0071E3",
        "btn_primary_fg": "#FFFFFF",
        "btn_neutral_bg": "#2E3140",   # 中性功能胶囊底
        "btn_neutral_hover": "#3A3D50",
        "btn_neutral_fg": "#E8EAF5",
        "theme_toggle_icon": "☀️ 浅色模式",
    },
    "light": {
        "name": "light",
        "label": "银白晨露",
        "bg_root": "#F2F2F7",          # 苹果官方系统浅灰
        "bg_outer_border": "#D1D1D6",  # 细腻浅灰边框
        "bg_card": "#FFFFFF",          # 纯净白卡片
        "bg_input": "#FFFFFF",         # 纯净白输入卡
        "input_border": "#E5E5EA",     # 输入框边缘
        "text_primary": "#111113",     # 深黑一级标题 (高清晰度)
        "text_body": "#1D1D1F",        # 极清晰正文
        "text_secondary": "#48484A",   # 次级文字
        "text_muted": "#8E8E93",       # 占位/热键
        "accent_blue": "#007AFF",      # 苹果官方蓝
        "accent_blue_hover": "#0068D6",
        "accent_green": "#34C759",     # 苹果官方绿
        "accent_green_hover": "#2DB84D",
        "accent_orange": "#FF9500",    # 苹果官方橙
        "tag_bg": "#E5E5EA",           # 药丸浅灰底
        "tag_hover": "#DADAE0",
        "tag_fg": "#0066CC",
        "tag_active_bg": "#007AFF",
        "tag_active_hover": "#0068D6",
        "tag_active_fg": "#FFFFFF",
        "btn_pill_bg": "#34C759",
        "btn_pill_hover": "#2DB84D",
        "btn_pill_fg": "#FFFFFF",
        "btn_primary_bg": "#007AFF",
        "btn_primary_hover": "#0068D6",
        "btn_primary_fg": "#FFFFFF",
        "btn_neutral_bg": "#E5E5EA",
        "btn_neutral_hover": "#DADAE0",
        "btn_neutral_fg": "#1D1D1F",
        "theme_toggle_icon": "🌙 深色模式",
    }
}

class ThemeManager:
    _current_theme = "dark"

    @classmethod
    def load_theme(cls) -> dict:
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    theme_key = cfg.get("theme", "dark")
                    if theme_key in THEMES:
                        cls._current_theme = theme_key
        except Exception:
            pass
        return THEMES[cls._current_theme]

    @classmethod
    def get_current(cls) -> dict:
        return THEMES.get(cls._current_theme, THEMES["dark"])

    @classmethod
    def toggle_theme(cls) -> dict:
        cls._current_theme = "light" if cls._current_theme == "dark" else "dark"
        cls.save_theme_preference(cls._current_theme)
        return THEMES[cls._current_theme]

    @classmethod
    def save_theme_preference(cls, theme_name: str):
        try:
            cfg = {}
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            cfg["theme"] = theme_name
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

def make_window_draggable(window, *handles):
    """
    使任意 Tkinter 窗口可鼠标拖动（支持多个手柄区域和其子组件），
    使用屏幕全局坐标 winfo_pointerx/y 实现丝滑平移，彻底避免抖动。
    """
    def start_drag(event):
        try:
            window._drag_start_x = window.winfo_pointerx() - window.winfo_x()
            window._drag_start_y = window.winfo_pointery() - window.winfo_y()
        except Exception:
            pass

    def do_drag(event):
        try:
            cur_x = window.winfo_pointerx()
            cur_y = window.winfo_pointery()
            new_x = cur_x - window._drag_start_x
            new_y = cur_y - window._drag_start_y
            window.geometry(f"+{new_x}+{new_y}")
        except Exception:
            pass

    for handle in handles:
        if handle is None:
            continue
        handle.bind("<ButtonPress-1>", start_drag, add="+")
        handle.bind("<B1-Motion>", do_drag, add="+")
        for child in handle.winfo_children():
            if not getattr(child, "_is_interactive", False):
                child.bind("<ButtonPress-1>", start_drag, add="+")
                child.bind("<B1-Motion>", do_drag, add="+")
