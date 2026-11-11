import tkinter as tk
from tkinter import messagebox
import threading
from PIL import ImageGrab, ImageTk, Image
from pathlib import Path
from obsidian_writer import ObsidianWriter
from ui_theme import ThemeManager, make_window_draggable
from apple_widgets import AppleTrafficLights, ApplePillButton, apply_apple_window_corners
from context_tracker import get_foreground_context, capture_selected_text, check_clipboard_image

class QuickJotWindow:
    def __init__(self, root=None, on_close_callback=None):
        self.writer = ObsidianWriter()
        self.on_close_callback = on_close_callback
        self.root = root
        self.window = None
        self.selected_tags = set()
        self.pasted_image = None
        self.theme = ThemeManager.load_theme()
        self.quote = ""
        self.context = {}
        self.has_clipboard_img = False

    def show(self, quote: str = "", context: dict = None):
        """呼出闪记窗口（支持自动传入划选文本与前台上下文）"""
        self.quote = (quote or "").strip()
        self.context = context or {}
        
        # 探测系统剪贴板是否有最新截图
        clip_img = check_clipboard_image()
        if clip_img:
            self.pasted_image = clip_img
            self.has_clipboard_img = True
        else:
            self.has_clipboard_img = False

        if self.window and self.window.winfo_exists():
            self.window.destroy()
            self.window = None

        self.theme = ThemeManager.load_theme()
        self.window = tk.Toplevel(self.root) if self.root else tk.Tk()
        self.window.title("OmniCapture 闪念速记")
        self.window.attributes("-topmost", True)
        self.window.overrideredirect(True)

        # 动态自适应尺寸：划词态高度 350px，纯打字态 240px
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        w = 660
        h = 350 if self.quote else 240
        x = (screen_w - w) // 2
        y = int(screen_h * 0.22)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()
        self.apply_theme()

        # 物理级 24px 大圆角
        apply_apple_window_corners(self.window, radius=24)

        # 键盘事件
        self.window.bind("<Control-Return>", lambda e: self.submit())
        self.window.bind("<Escape>", lambda e: self.hide())
        self.window.bind("<Control-v>", lambda e: self._on_manual_paste())

        self.text_input.focus_set()
        self.window.after(60, lambda: self.text_input.focus_force())

    def _build_ui(self):
        th = self.theme
        self.outer_frame = tk.Frame(self.window, padx=1, pady=1)
        self.outer_frame.pack(fill="both", expand=True)

        self.main_frame = tk.Frame(self.outer_frame, padx=18, pady=12)
        self.main_frame.pack(fill="both", expand=True)

        # 1. 顶部苹果 macOS 标题栏
        self.top_bar = tk.Frame(self.main_frame)
        self.top_bar.pack(fill="x", pady=(0, 8))

        # 14px 饱满红黄绿交通灯
        self.traffic_lights = AppleTrafficLights(
            self.top_bar,
            on_close=self.hide,
            on_minimize=self._clear_input,
            on_maximize=self.submit,
            bg=th["bg_root"]
        )
        self.traffic_lights._is_interactive = True
        self.traffic_lights.pack(side="left", padx=(0, 8))

        # 标题
        title_text = "灵感闪记 · 划词直录" if self.quote else "灵感闪记 · 极简随手记"
        self.title_lbl = tk.Label(
            self.top_bar,
            text=f"⚡ {title_text}",
            font=("Microsoft YaHei UI", 10, "bold")
        )
        self.title_lbl.pack(side="left")

        # 模式切换胶囊
        self.theme_btn = ApplePillButton(
            self.top_bar,
            text=th["theme_toggle_icon"],
            command=self.toggle_theme,
            width=96,
            height=26,
            bg_color=th["bg_root"],
            pill_color=th["btn_neutral_bg"],
            hover_color=th["btn_neutral_hover"],
            text_color=th["btn_neutral_fg"],
            font=("Microsoft YaHei UI", 8)
        )
        self.theme_btn.pack(side="right")

        # 前台来源自动嗅探小胶囊 (乔木核心亮点)
        app_name = self.context.get("app", "")
        doc_title = self.context.get("title", "")
        if app_name or doc_title:
            short_title = doc_title[:18] + ("..." if len(doc_title) > 18 else "")
            src_display = f"来源: {app_name} - {short_title}" if short_title else f"来源: {app_name}"
            self.src_pill = tk.Label(
                self.top_bar,
                text=src_display,
                font=("Microsoft YaHei UI", 8),
                padx=8,
                pady=2
            )
            self.src_pill.pack(side="right", padx=(0, 6))
        else:
            self.src_pill = None

        make_window_draggable(self.window, self.top_bar, self.title_lbl)

        # 2. 如果存在划词选中文本：展示自动包裹的引用条
        if self.quote:
            self.quote_frame = tk.Frame(self.main_frame, padx=1, pady=1)
            self.quote_frame.pack(fill="x", pady=(0, 8))

            self.quote_inner = tk.Frame(self.quote_frame, padx=10, pady=6)
            self.quote_inner.pack(fill="x")

            # 引用左侧装饰蓝条
            self.quote_bar = tk.Frame(self.quote_inner, width=3)
            self.quote_bar.pack(side="left", fill="y", padx=(0, 8))

            quote_text_disp = self.quote.replace("\n", " ")
            if len(quote_text_disp) > 140:
                quote_text_disp = quote_text_disp[:140] + "..."

            self.quote_lbl = tk.Label(
                self.quote_inner,
                text=f"“{quote_text_disp}”",
                font=("Microsoft YaHei UI", 9),
                wraplength=570,
                justify="left"
            )
            self.quote_lbl.pack(side="left", fill="x", expand=True)

        # 3. 核心思考输入框
        self.input_card = tk.Frame(self.main_frame, padx=1, pady=1)
        self.input_card.pack(fill="both", expand=True, pady=(0, 10))

        input_h = 4 if self.quote else 5
        self.text_input = tk.Text(
            self.input_card,
            font=("Microsoft YaHei UI", 11),
            relief="flat",
            wrap="word",
            padx=12,
            pady=8,
            height=input_h
        )
        self.text_input.pack(fill="both", expand=True)

        # 4. 底部快捷栏 (标签 + 剪贴板附件指示 + 存入按钮)
        self.bottom_bar = tk.Frame(self.main_frame)
        self.bottom_bar.pack(fill="x")

        # 快捷药丸标签
        preset_tags = [
            ("自媒体素材", 88),
            ("灵感", 56),
            ("待办", 56),
            ("深度学习", 76),
            ("认知", 56)
        ]
        self.tag_buttons = {}
        for tag, btn_w in preset_tags:
            btn = ApplePillButton(
                self.bottom_bar,
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
            btn.pack(side="left", padx=2)
            self.tag_buttons[tag] = btn

        # 剪贴板自动嗅探截图附着胶囊
        if self.has_clipboard_img:
            self.clip_pill = ApplePillButton(
                self.bottom_bar,
                text="📎 附带截图",
                command=self._toggle_clip_img,
                width=86,
                height=26,
                bg_color=th["bg_root"],
                pill_color=th["accent_blue"],
                hover_color=th["accent_blue_hover"],
                text_color="#FFFFFF",
                font=("Microsoft YaHei UI", 8, "bold")
            )
            self.clip_pill.pack(side="left", padx=4)
        else:
            self.clip_pill = None

        # 存入 Obsidian 按钮
        self.save_btn = ApplePillButton(
            self.bottom_bar,
            text="存入 Obsidian ↵",
            command=self.submit,
            width=135,
            height=30,
            bg_color=th["bg_root"],
            pill_color=th["btn_pill_bg"],
            hover_color=th["btn_pill_hover"],
            text_color=th["btn_pill_fg"],
            font=("Microsoft YaHei UI", 9, "bold")
        )
        self.save_btn.pack(side="right")

    def _toggle_clip_img(self):
        th = self.theme
        if self.pasted_image:
            self.pasted_image = None
            if self.clip_pill:
                self.clip_pill.update_colors(th["bg_root"], th["btn_neutral_bg"], th["btn_neutral_hover"], th["text_muted"], text="📎 不附带")
        else:
            clip_img = check_clipboard_image()
            if clip_img:
                self.pasted_image = clip_img
                if self.clip_pill:
                    self.clip_pill.update_colors(th["bg_root"], th["accent_blue"], th["accent_blue_hover"], "#FFFFFF", text="📎 附带截图")

    def apply_theme(self):
        th = self.theme
        self.window.configure(bg=th["bg_root"])
        self.outer_frame.configure(bg=th["bg_outer_border"])
        self.main_frame.configure(bg=th["bg_root"])
        self.top_bar.configure(bg=th["bg_root"])

        self.traffic_lights.set_bg(th["bg_root"])
        self.title_lbl.configure(fg=th["text_primary"], bg=th["bg_root"])

        if self.src_pill:
            self.src_pill.configure(bg=th["btn_neutral_bg"], fg=th["accent_blue"])

        self.theme_btn.update_colors(
            parent_bg=th["bg_root"],
            pill_color=th["btn_neutral_bg"],
            hover_color=th["btn_neutral_hover"],
            text_color=th["btn_neutral_fg"],
            text=th["theme_toggle_icon"]
        )

        if self.quote and hasattr(self, "quote_frame"):
            self.quote_frame.configure(bg=th["input_border"])
            self.quote_inner.configure(bg=th["bg_card"])
            self.quote_bar.configure(bg=th["accent_blue"])
            self.quote_lbl.configure(bg=th["bg_card"], fg=th["text_secondary"])

        self.input_card.configure(bg=th["input_border"])
        self.text_input.configure(
            bg=th["bg_input"],
            fg=th["text_body"],
            insertbackground=th["accent_blue"],
            selectbackground=th["accent_blue"],
            selectforeground="#FFFFFF"
        )

        self.bottom_bar.configure(bg=th["bg_root"])
        self._refresh_tag_buttons()

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

    def _on_manual_paste(self):
        clip_img = check_clipboard_image()
        if clip_img:
            self.pasted_image = clip_img
            self.text_input.insert(tk.END, "\n[📎 已捕获剪贴板图片，将在保存时自动归档至 attachments]")

    def submit(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text and not self.quote and not self.pasted_image:
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
        self.writer.save_quick_jot(
            text=text,
            tags=tags_list,
            images=images,
            quote=self.quote,
            context=self.context
        )
        self.hide()

    def hide(self):
        if self.window and self.window.winfo_exists():
            self.window.destroy()
            self.window = None
        self.selected_tags.clear()
        self.pasted_image = None
        self.quote = ""
        self.context = {}
        if self.on_close_callback:
            self.on_close_callback()

if __name__ == "__main__":
    app = QuickJotWindow()
    app.show(quote="测试划选引用文本，自动追踪前台来源。", context={"app": "Chrome", "title": "DeepSeek 技术报告"})
    tk.mainloop()
