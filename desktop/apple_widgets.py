import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import ctypes

def apply_apple_window_corners(window, radius=24):
    """通过 Windows 原生 GDI 和 DWM 为顶层无边框窗口赋予真正的物理圆角与阴影"""
    try:
        if not isinstance(window, (tk.Tk, tk.Toplevel)):
            return
        window.update_idletasks()
        w = window.winfo_width()
        h = window.winfo_height()
        if w < 100 or h < 50:
            return
        hwnd = window.winfo_id()
        
        # 1. GDI 物理裁剪真实圆角
        rgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, w + 1, h + 1, radius, radius)
        ctypes.windll.user32.SetWindowRgn(hwnd, rgn, True)

        # 2. Windows 11 DWM 圆角与阴影属性
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
            ctypes.sizeof(ctypes.c_int)
        )
    except Exception:
        pass


class AppleTrafficLights(tk.Canvas):
    """macOS 原生质感红黄绿交通灯 (14px 饱满圆润，带悬停微符号)"""
    def __init__(self, parent, on_close=None, on_minimize=None, on_maximize=None, bg="#1E1F26", **kwargs):
        super().__init__(parent, width=76, height=28, bg=bg, highlightthickness=0, **kwargs)
        self.on_close = on_close
        self.on_minimize = on_minimize
        self.on_maximize = on_maximize
        self.bg_color = bg
        self.is_hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Motion>", self._on_motion)
        self.bind("<Button-1>", self._on_click)
        self._draw_dots()

    def set_bg(self, bg_color):
        self.bg_color = bg_color
        self.configure(bg=bg_color)
        self._draw_dots()

    def _draw_dots(self):
        self.delete("all")
        # 3个圆心坐标: x = 14, 38, 62; y = 14; 半径 = 7 (直径 14px)
        r = 7
        dots = [
            (14, 14, "#FF5F56", "#E0443E", "✕", "close"),
            (38, 14, "#FFBD2E", "#DEA123", "—", "min"),
            (62, 14, "#27C93F", "#1AAB29", "+", "max")
        ]
        
        for cx, cy, fill_col, border_col, symbol, tag in dots:
            # 绘制饱满有边框的原型胶囊
            self.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=fill_col,
                outline=border_col,
                width=1,
                tags=(tag, "dot")
            )
            if self.is_hovered:
                self.create_text(
                    cx, cy - 1,
                    text=symbol,
                    fill="#4D0000" if tag == "close" else ("#5C3D00" if tag == "min" else "#004D11"),
                    font=("Segoe UI", 8, "bold"),
                    tags=(tag, "symbol")
                )

    def _on_enter(self, e):
        self.is_hovered = True
        self._draw_dots()

    def _on_leave(self, e):
        self.is_hovered = False
        self._draw_dots()

    def _on_motion(self, e):
        # 悬停在小球上时光标变为手势
        x, y = e.x, e.y
        if (7 <= x <= 21 and 7 <= y <= 21) or (31 <= x <= 45 and 7 <= y <= 21) or (55 <= x <= 69 and 7 <= y <= 21):
            self.config(cursor="hand2")
        else:
            self.config(cursor="")

    def _on_click(self, e):
        x, y = e.x, e.y
        if 7 <= x <= 21 and 7 <= y <= 21:
            if self.on_close:
                self.on_close()
        elif 31 <= x <= 45 and 7 <= y <= 21:
            if self.on_minimize:
                self.on_minimize()
        elif 55 <= x <= 69 and 7 <= y <= 21:
            if self.on_maximize:
                self.on_maximize()


class ApplePillButton(tk.Canvas):
    """真正的 Apple 胶囊药丸按钮 (Anti-Aliased Squircle / Capsule)"""
    def __init__(self, parent, text, command=None, width=120, height=32,
                 bg_color="#1E1F26", pill_color="#34C759", hover_color="#2DB84D",
                 text_color="#FFFFFF", font=("Microsoft YaHei UI", 9, "bold"),
                 outline_color=None, **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0, **kwargs)
        self.text = text
        self.command = command
        self.btn_w = width
        self.btn_h = height
        self.parent_bg = bg_color
        self.pill_color = pill_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.outline_color = outline_color
        self.is_hovered = False
        self._is_interactive = True

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.config(cursor="hand2")
        self.render()

    def update_colors(self, parent_bg, pill_color, hover_color, text_color, outline_color=None, text=None):
        self.parent_bg = parent_bg
        self.pill_color = pill_color
        self.hover_color = hover_color
        self.text_color = text_color
        if outline_color is not None:
            self.outline_color = outline_color
        if text is not None:
            self.text = text
        self.configure(bg=parent_bg)
        self.render()

    def render(self):
        self.delete("all")
        cur_color = self.hover_color if self.is_hovered else self.pill_color
        
        # 绘制药丸圆角底色 (使用圆角矩形)
        r = self.btn_h // 2
        # 画左半圆、右半圆和中间矩形
        self.create_arc(1, 1, self.btn_h - 1, self.btn_h - 1, start=90, extent=180, fill=cur_color, outline=self.outline_color or cur_color)
        self.create_arc(self.btn_w - self.btn_h + 1, 1, self.btn_w - 1, self.btn_h - 1, start=270, extent=180, fill=cur_color, outline=self.outline_color or cur_color)
        self.create_rectangle(r, 1, self.btn_w - r + 1, self.btn_h - 1, fill=cur_color, outline=cur_color)
        if self.outline_color:
            self.create_line(r, 1, self.btn_w - r + 1, 1, fill=self.outline_color)
            self.create_line(r, self.btn_h - 1, self.btn_w - r + 1, self.btn_h - 1, fill=self.outline_color)

        self.create_text(
            self.btn_w // 2, self.btn_h // 2,
            text=self.text,
            fill=self.text_color,
            font=self.font
        )

    def _on_enter(self, e):
        self.is_hovered = True
        self.render()

    def _on_leave(self, e):
        self.is_hovered = False
        self.render()

    def _on_click(self, e):
        if self.command:
            self.command()
