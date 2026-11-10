import tkinter as tk
from tkinter import messagebox
import threading
from PIL import ImageGrab, ImageTk, Image
from pathlib import Path
from obsidian_writer import ObsidianWriter
from ui_theme import ThemeManager, make_window_draggable
from apple_widgets import AppleTrafficLights, ApplePillButton, apply_apple_window_corners

class QuickJotWindow:
    def __init__(self, root=None, on_close_callback=None):
        self.writer = ObsidianWriter()
        self.on_close_callback = on_close_callback
        self.root = root
        self.window = None
        self.selected_tags = set()
        self.pasted_image = None
        self.theme = ThemeManager.load_theme()

    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            self.window.attributes("-topmost", True)
            self.window.focus_force()
            self.text_input.focus_set()
            self.window.after(50, lambda: self.text_input.focus_force())
            return

        self.theme = ThemeManager.load_theme()
        self.window = tk.Toplevel(self.root) if self.root else tk.Tk()
        self.window.title("OmniCapture 闪念速记")
        self.window.attributes("-topmost", True)
        self.window.overrideredirect(True)  # 沉浸式现代无边框

        # 居中偏上定位
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        w, h = 640, 310
        x = (screen_w - w) // 2
        y = int(screen_h * 0.22)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()
        self.apply_theme()

        # 物理裁剪为 Apple 24px 大圆角窗口 (支持 Win10 & Win11)
        apply_apple_window_corners(self.window, radius=24)

        # 键盘事件绑定
        self.window.bind("<Control-Return>", lambda e: self.submit())
        self.window.bind("<Escape>", lambda e: self.hide())
        self.window.bind("<Control-v>", lambda e: self.check_clipboard_image())

        self.text_input.focus_set()
        self.window.after(60, lambda: self.text_input.focus_force())

    def _build_ui(self):
        th = self.theme
        # 外层圆角质感描边容器
        self.outer_frame = tk.Frame(self.window, padx=1, pady=1)
        self.outer_frame.pack(fill="both", expand=True)

        self.main_frame = tk.Frame(self.outer_frame, padx=18, pady=14)
        self.main_frame.pack(fill="both", expand=True)

        # 1. 顶部苹果 macOS 标题栏
        self.top_bar = tk.Frame(self.main_frame)
        self.top_bar.pack(fill="x", pady=(0, 10))

        # 饱满的红黄绿交通灯 (14px 饱满大圆点，带悬停微符)
        self.traffic_lights = AppleTrafficLights(
            self.top_bar,
            on_close=self.hide,
            on_minimize=self._clear_input,
            on_maximize=self.submit,
            bg=th["bg_root"]
        )
        self.traffic_lights._is_interactive = True
        self.traffic_lights.pack(side="left", padx=(0, 10))

        # 标题文本 (极清加粗)
        self.title_lbl = tk.Label(
            self.top_bar,
            text="⚡ 闪念速记  →  直接存入 Obsidian",
            font=("Microsoft YaHei UI", 11, "bold")
        )
        self.title_lbl.pack(side="left")

        # 右侧：模式切换胶囊按钮 (☀️/🌙 药丸按键)
        self.theme_btn = ApplePillButton(
            self.top_bar,
            text=th["theme_toggle_icon"],
            command=self.toggle_theme,
            width=105,
            height=28,
            bg_color=th["bg_root"],
            pill_color=th["btn_neutral_bg"],
            hover_color=th["btn_neutral_hover"],
            text_color=th["btn_neutral_fg"],
            font=("Microsoft YaHei UI", 9)
        )
        self.theme_btn.pack(side="right")

        # 绑定鼠标拖拽手柄
        make_window_draggable(self.window, self.top_bar, self.title_lbl)

        # 2. 文本输入区域 (卡片凹槽质感，超清对比度)
        self.input_card = tk.Frame(self.main_frame, padx=1, pady=1)
        self.input_card.pack(fill="both", expand=True, pady=(0, 12))

        self.text_input = tk.Text(
            self.input_card,
            font=("Microsoft YaHei UI", 11),
            relief="flat",
            wrap="word",
            padx=12,
            pady=10,
            height=5
        )
        self.text_input.pack(fill="both", expand=True)

        # 3. 标签快速选择区 (胶囊药丸标签)
        self.tag_bar = tk.Frame(self.main_frame)
        self.tag_bar.pack(fill="x", pady=(0, 12))

        self.tag_prompt_lbl = tk.Label(
            self.tag_bar,
            text="快捷标签:",
            font=("Microsoft YaHei UI", 9, "bold")
        )
        self.tag_prompt_lbl.pack(side="left", padx=(0, 8))

        preset_tags = [
            ("灵感", 66),
            ("待办", 66),
            ("自媒体素材", 94),
            ("金句", 66),
            ("认知", 66)
        ]
        self.tag_buttons = {}
        for tag, btn_w in preset_tags:
            btn = ApplePillButton(
                self.tag_bar,
                text=f"#{tag}",
                command=lambda t=tag: self.toggle_tag(t),
                width=btn_w,
                height=26,
                bg_color=th["bg_root"],
                pill_color=th["tag_bg"],
                hover_color=th["tag_hover"],
                text_color=th["tag_fg"],
                font=("Microsoft YaHei UI", 9)
            )
            btn.pack(side="left", padx=4)
            self.tag_buttons[tag] = btn

        # 4. 底部操作栏
        self.bottom_bar = tk.Frame(self.main_frame)
        self.bottom_bar.pack(fill="x")

        self.hint_lbl = tk.Label(
            self.bottom_bar,
            text="快捷键: [Ctrl+Enter] 保存  |  [Esc] 退出  |  支持直接 [Ctrl+V] 贴图",
            font=("Microsoft YaHei UI", 9)
        )
        self.hint_lbl.pack(side="left")

        # Apple 经典翡翠绿胶囊主按钮 (圆润药丸外观)
        self.save_btn = ApplePillButton(
            self.bottom_bar,
            text="存入 Obsidian ↵",
            command=self.submit,
            width=140,
            height=32,
            bg_color=th["bg_root"],
            pill_color=th["btn_pill_bg"],
            hover_color=th["btn_pill_hover"],
            text_color=th["btn_pill_fg"],
            font=("Microsoft YaHei UI", 9, "bold")
        )
        self.save_btn.pack(side="right")

    def apply_theme(self):
        th = self.theme
        self.window.configure(bg=th["bg_root"])
        self.outer_frame.configure(bg=th["bg_outer_border"])
        self.main_frame.configure(bg=th["bg_root"])
        self.top_bar.configure(bg=th["bg_root"])

        self.traffic_lights.set_bg(th["bg_root"])
        self.title_lbl.configure(fg=th["text_primary"], bg=th["bg_root"])
        
        self.theme_btn.update_colors(
            parent_bg=th["bg_root"],
            pill_color=th["btn_neutral_bg"],
            hover_color=th["btn_neutral_hover"],
            text_color=th["btn_neutral_fg"],
            text=th["theme_toggle_icon"]
        )

        self.input_card.configure(bg=th["input_border"])
        self.text_input.configure(
            bg=th["bg_input"],
            fg=th["text_body"],
            insertbackground=th["accent_blue"],
            selectbackground=th["accent_blue"],
            selectforeground="#FFFFFF"
        )

        self.tag_bar.configure(bg=th["bg_root"])
        self.tag_prompt_lbl.configure(fg=th["text_secondary"], bg=th["bg_root"])
        self._refresh_tag_buttons()

        self.bottom_bar.configure(bg=th["bg_root"])
        self.hint_lbl.configure(fg=th["text_muted"], bg=th["bg_root"])
        self.save_btn.update_colors(
            parent_bg=th["bg_root"],
            pill_color=th["btn_pill_bg"],
            hover_color=th["btn_pill_hover"],
            text_color=th["btn_pill_fg"]
        )

    def _refresh_tag_buttons(self):
        th = self.theme
        for tag, btn in self.tag_buttons.items():
            if tag in self.selected_tags:
                btn.update_colors(
                    parent_bg=th["bg_root"],
                    pill_color=th["tag_active_bg"],
                    hover_color=th["tag_active_hover"],
                    text_color=th["tag_active_fg"]
                )
            else:
                btn.update_colors(
                    parent_bg=th["bg_root"],
                    pill_color=th["tag_bg"],
                    hover_color=th["tag_hover"],
                    text_color=th["tag_fg"]
                )

    def toggle_theme(self):
        self.theme = ThemeManager.toggle_theme()
        self.apply_theme()

    def _clear_input(self):
        self.text_input.delete("1.0", tk.END)

    def toggle_tag(self, tag):
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
        else:
            self.selected_tags.add(tag)
        self._refresh_tag_buttons()

    def check_clipboard_image(self):
        try:
            im = ImageGrab.grabclipboard()
            if isinstance(im, Image.Image):
                self.pasted_image = im
                self.text_input.insert(tk.END, "\n[📎 已捕获剪贴板图片，将在保存时自动归档至 attachments]")
        except Exception:
            pass

    def submit(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text and not self.pasted_image:
            self.hide()
            return

        images = []
        if self.pasted_image:
            img_res = self.writer.save_screenshot(self.pasted_image, note="闪记内嵌图")
            if "wikilink" in img_res:
                target = img_res["wikilink"].replace("![[", "").replace("]]", "")
                images.append(target)
            self.pasted_image = None

        tags_list = list(self.selected_tags)
        self.writer.save_quick_jot(text=text, tags=tags_list, images=images)
        self.hide()

    def hide(self):
        if self.window and self.window.winfo_exists():
            self.window.destroy()
            self.window = None
        self.selected_tags.clear()
        self.pasted_image = None
        if self.on_close_callback:
            self.on_close_callback()

if __name__ == "__main__":
    app = QuickJotWindow()
    app.show()
    tk.mainloop()
