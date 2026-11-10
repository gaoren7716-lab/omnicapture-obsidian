import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

THEMES = {
    "dark": {
        "name": "dark",
        "label": "深色石墨",
        "bg_root": "#1A1B22",          # 沉浸暗夜主背景
        "bg_outer_border": "#323440",  # 细腻外框描边
        "bg_card": "#22242D",          # 内容卡片层
        "bg_input": "#14151A",         # 文本输入凹槽
        "input_border": "#2E303C",     # 输入框微边框
        "text_primary": "#FFFFFF",     # 顶层标题文字 (极高清晰度)
        "text_body": "#F0F2FA",        # 主体文本 (极高清晰度，不发虚)
        "text_secondary": "#B5B8C8",   # 次级指引文字
        "text_muted": "#7A7E94",       # 占位符/热键提示
        "accent_blue": "#0A84FF",      # 苹果蓝
        "accent_green": "#30D158",     # 苹果绿
        "accent_orange": "#FF9F0A",    # 苹果橙
        "tag_bg": "#2A2C38",           # 标签常态背景
        "tag_fg": "#7FB7FF",           # 标签文字
        "tag_active_bg": "#0A84FF",    # 选中标签背景
        "tag_active_fg": "#FFFFFF",    # 选中标签文字
        "btn_primary_bg": "#0A84FF",   # 主按钮背景
        "btn_primary_fg": "#FFFFFF",
        "btn_success_bg": "#30D158",   # 存入按钮背景
        "btn_success_fg": "#0E1C12",
        "btn_neutral_bg": "#2E313E",   # 中性按钮背景
        "btn_neutral_fg": "#E2E5F2",
        "traffic_close": "#FF5F56",    # 红
        "traffic_min": "#FFBD2E",      # 黄
        "traffic_max": "#27C93F",      # 绿
        "theme_toggle_icon": "☀️ 浅色模式",
    },
    "light": {
        "name": "light",
        "label": "银白晨露",
        "bg_root": "#F2F2F7",          # 苹果浅灰底色
        "bg_outer_border": "#D1D1D6",  # 精致边框
        "bg_card": "#FFFFFF",          # 纯净白卡片
        "bg_input": "#FAFAFC",         # 输入区域
        "input_border": "#E5E5EA",     # 输入框轻边框
        "text_primary": "#111113",     # 极黑高清晰度标题
        "text_body": "#1D1D1F",        # 极清晰正文
        "text_secondary": "#48484A",   # 次级文字
        "text_muted": "#8E8E93",       # 占位与热键
        "accent_blue": "#007AFF",      # 苹果官方蓝
        "accent_green": "#34C759",     # 苹果官方绿
        "accent_orange": "#FF9500",    # 苹果官方橙
        "tag_bg": "#EBEBF0",           # 标签浅灰底
        "tag_fg": "#0066CC",           # 标签字
        "tag_active_bg": "#007AFF",    # 选中标签背景
        "tag_active_fg": "#FFFFFF",    # 选中标签文字
        "btn_primary_bg": "#007AFF",   # 主按钮背景
        "btn_primary_fg": "#FFFFFF",
        "btn_success_bg": "#34C759",   # 存入按钮背景
        "btn_success_fg": "#FFFFFF",
        "btn_neutral_bg": "#E5E5EA",   # 中性按钮
        "btn_neutral_fg": "#1C1C1E",
        "traffic_close": "#FF5F56",
        "traffic_min": "#FFBD2E",
        "traffic_max": "#27C93F",
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
