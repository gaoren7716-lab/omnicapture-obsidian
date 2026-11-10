import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, ImageTk, Image, ImageDraw
import io
import threading
from datetime import datetime
from obsidian_writer import ObsidianWriter
from translation_service import TranslationService
from ai_service import AIService
from ui_theme import ThemeManager, make_window_draggable

class TranslationDialog:
    """截图翻译与 AI 深度管理悬浮面板 (支持全屏任意拖拽、深/浅苹果双色系)"""
    def __init__(self, parent, image: Image.Image, writer: ObsidianWriter):
        self.theme = ThemeManager.load_theme()
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("OmniCapture 截图识别、翻译与 AI 深度管理")
        self.dialog.attributes("-topmost", True)
        self.dialog.overrideredirect(True)  # 沉浸式无边框，通过自定义 macOS 顶栏拖动

        # 居中偏上定位
        screen_w = self.dialog.winfo_screenwidth()
        screen_h = self.dialog.winfo_screenheight()
        w, h = 640, 650
        x = max(20, (screen_w - w) // 2)
        y = max(20, (screen_h - h) // 2 - 30)
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())

        self.image = image
        self.writer = writer
        self.ai_service = AIService()
        self.original_text = "正在识别中..."
        self.translated_text = "正在翻译中..."
        self.ai_data = None

        self._build_ui()
        self.apply_theme()

        # 异步两步流水线：第一步瞬间返回翻译，第二步异步返回 AI 深度分析
        threading.Thread(target=self._async_process, daemon=True).start()

    def _build_ui(self):
        # 外层细腻描边
        self.outer_frame = tk.Frame(self.dialog, padx=1, pady=1)
        self.outer_frame.pack(fill="both", expand=True)

        self.main_frame = tk.Frame(self.outer_frame, padx=16, pady=12)
        self.main_frame.pack(fill="both", expand=True)

        # 1. macOS 风格标题栏 (支持鼠标按住自由拖拽窗口)
        self.top_bar = tk.Frame(self.main_frame)
        self.top_bar.pack(fill="x", pady=(0, 10))

        traffic_box = tk.Frame(self.top_bar)
        traffic_box.pack(side="left", padx=(0, 12))

        self.dot_red = tk.Label(traffic_box, text="●", font=("Arial", 12), cursor="hand2")
        self.dot_red.pack(side="left", padx=2)
        self.dot_red._is_interactive = True
        self.dot_red.bind("<Button-1>", lambda e: self.dialog.destroy())

        self.dot_yellow = tk.Label(traffic_box, text="●", font=("Arial", 12), cursor="hand2")
        self.dot_yellow.pack(side="left", padx=2)
        self.dot_yellow._is_interactive = True
        self.dot_yellow.bind("<Button-1>", lambda e: self.dialog.iconify() if hasattr(self.dialog, 'iconify') else None)

        self.dot_green = tk.Label(traffic_box, text="●", font=("Arial", 12), cursor="hand2")
        self.dot_green.pack(side="left", padx=2)
        self.dot_green._is_interactive = True
        self.dot_green.bind("<Button-1>", lambda e: self.save_to_obsidian())

        self.title_lbl = tk.Label(
            self.top_bar,
            text="🌐 截图识别、翻译与 AI 深度洞察 (可按住拖动窗口)",
            font=("Microsoft YaHei UI", 10, "bold")
        )
        self.title_lbl.pack(side="left")

        # 主题切换按钮
        self.theme_btn = tk.Label(
            self.top_bar,
            text=self.theme["theme_toggle_icon"],
            font=("Microsoft YaHei UI", 9),
            padx=8,
            pady=2,
            cursor="hand2"
        )
        self.theme_btn._is_interactive = True
        self.theme_btn.pack(side="right")
        self.theme_btn.bind("<Button-1>", lambda e: self.toggle_theme())

        # 绑定拖拽：按住顶栏或标题即可自由移动弹窗
        make_window_draggable(self.dialog, self.top_bar, self.title_lbl)

        # 2. 原文内容 (OCR) 卡片
        self.lbl_orig = tk.Label(self.main_frame, text="📝 原文内容 (OCR):", font=("Microsoft YaHei UI", 9, "bold"))
        self.lbl_orig.pack(anchor="w", pady=(0, 2))

        self.card_orig = tk.Frame(self.main_frame, padx=1, pady=1)
        self.card_orig.pack(fill="x", pady=(0, 8))
        self.txt_orig = tk.Text(self.card_orig, font=("Microsoft YaHei UI", 10), height=4, wrap="word", relief="flat", padx=10, pady=6)
        self.txt_orig.pack(fill="x")

        # 3. 中文译文 卡片
        self.lbl_trans = tk.Label(self.main_frame, text="🀄 中文译文 (快速双语对照):", font=("Microsoft YaHei UI", 9, "bold"))
        self.lbl_trans.pack(anchor="w", pady=(0, 2))

        self.card_trans = tk.Frame(self.main_frame, padx=1, pady=1)
        self.card_trans.pack(fill="x", pady=(0, 8))
        self.txt_trans = tk.Text(self.card_trans, font=("Microsoft YaHei UI", 10, "bold"), height=4, wrap="word", relief="flat", padx=10, pady=6)
        self.txt_trans.pack(fill="x")

        # 4. AI 智能提炼与双链知识卡片
        self.lbl_ai = tk.Label(self.main_frame, text="🤖 AI 核心洞察与双链知识图谱:", font=("Microsoft YaHei UI", 9, "bold"))
        self.lbl_ai.pack(anchor="w", pady=(0, 2))

        self.card_ai = tk.Frame(self.main_frame, padx=1, pady=1)
        self.card_ai.pack(fill="both", expand=True, pady=(0, 10))
        self.txt_ai = tk.Text(self.card_ai, font=("Microsoft YaHei UI", 9), height=7, wrap="word", relief="flat", padx=10, pady=8)
        self.txt_ai.pack(fill="both", expand=True)
        self.txt_ai.insert(tk.END, "AI 正在分析核心观点与关联主题...")

        # 5. 底部按钮与状态栏
        self.btn_bar = tk.Frame(self.main_frame)
        self.btn_bar.pack(fill="x", pady=(2, 0))

        self.status_lbl = tk.Label(self.btn_bar, text="正在处理...", font=("Microsoft YaHei UI", 9))
        self.status_lbl.pack(side="left")

        self.btn_close = tk.Label(self.btn_bar, text=" 关闭 [Esc] ", font=("Microsoft YaHei UI", 9), padx=10, pady=5, cursor="hand2")
        self.btn_close._is_interactive = True
        self.btn_close.pack(side="right", padx=3)
        self.btn_close.bind("<Button-1>", lambda e: self.dialog.destroy())

        self.btn_copy = tk.Label(self.btn_bar, text=" 📋 复制译文 ", font=("Microsoft YaHei UI", 9), padx=12, pady=5, cursor="hand2")
        self.btn_copy._is_interactive = True
        self.btn_copy.pack(side="right", padx=3)
        self.btn_copy.bind("<Button-1>", lambda e: self.copy_trans())

        self.btn_save = tk.Label(self.btn_bar, text=" 💾 存入 Obsidian ", font=("Microsoft YaHei UI", 9, "bold"), padx=14, pady=5, cursor="hand2")
        self.btn_save._is_interactive = True
        self.btn_save.pack(side="right", padx=3)
        self.btn_save.bind("<Button-1>", lambda e: self.save_to_obsidian())

    def apply_theme(self):
        th = self.theme
        self.dialog.configure(bg=th["bg_root"])
        self.outer_frame.configure(bg=th["bg_outer_border"])
        self.main_frame.configure(bg=th["bg_root"])
        self.top_bar.configure(bg=th["bg_root"])

        for dot, color in [(self.dot_red, th["traffic_close"]),
                           (self.dot_yellow, th["traffic_min"]),
                           (self.dot_green, th["traffic_max"])]:
            dot.master.configure(bg=th["bg_root"])
            dot.configure(fg=color, bg=th["bg_root"])

        self.title_lbl.configure(fg=th["text_primary"], bg=th["bg_root"])
        self.theme_btn.configure(
            text=th["theme_toggle_icon"],
            fg=th["btn_neutral_fg"],
            bg=th["btn_neutral_bg"]
        )

        # 标签与卡片颜色配置 (超高对比度清晰字)
        self.lbl_orig.configure(fg=th["accent_blue"], bg=th["bg_root"])
        self.card_orig.configure(bg=th["input_border"])
        self.txt_orig.configure(bg=th["bg_input"], fg=th["text_body"], insertbackground=th["accent_blue"])

        self.lbl_trans.configure(fg=th["accent_green"], bg=th["bg_root"])
        self.card_trans.configure(bg=th["input_border"])
        self.txt_trans.configure(bg=th["bg_input"], fg=th["text_primary"], insertbackground=th["accent_green"])

        self.lbl_ai.configure(fg=th["accent_orange"], bg=th["bg_root"])
        self.card_ai.configure(bg=th["input_border"])
        self.txt_ai.configure(bg=th["bg_input"], fg=th["text_body"], insertbackground=th["accent_orange"])

        self.btn_bar.configure(bg=th["bg_root"])
        self.status_lbl.configure(fg=th["text_muted"], bg=th["bg_root"])
        self.btn_close.configure(bg=th["btn_neutral_bg"], fg=th["btn_neutral_fg"])
        self.btn_copy.configure(bg=th["btn_primary_bg"], fg=th["btn_primary_fg"])
        self.btn_save.configure(bg=th["btn_success_bg"], fg=th["btn_success_fg"])

    def toggle_theme(self):
        self.theme = ThemeManager.toggle_theme()
        self.apply_theme()

    def _async_process(self):
        # 步骤 1：极速完成 OCR 与神经翻译
        res = TranslationService.ocr_and_translate(self.image)
        self.original_text = res.get("original", "")
        self.translated_text = res.get("translated", "")

        def update_trans_ui():
            self.txt_orig.delete("1.0", tk.END)
            self.txt_orig.insert(tk.END, self.original_text)
            self.txt_trans.delete("1.0", tk.END)
            self.txt_trans.insert(tk.END, self.translated_text)
            self.status_lbl.config(text="✓ 翻译完毕，正在进行 AI 深度解析...", fg=self.theme["accent_blue"])

        self.dialog.after(0, update_trans_ui)

        # 步骤 2：AI 深度提炼与双链建议
        ai_res = self.ai_service.analyze_content(self.translated_text or self.original_text, is_translation=True)
        self.ai_data = ai_res

        def update_ai_ui():
            self.txt_ai.delete("1.0", tk.END)
            summary = self.ai_data.get("summary", "")
            key_pts = "\n".join([f"• {p}" for p in self.ai_data.get("key_points", [])])
            links = " | ".join([f"[[{w}]]" for w in self.ai_data.get("wikilinks", [])])
            tags = " ".join([f"#{t}" for t in self.ai_data.get("tags", [])])

            ai_display = f"💡 核心要点：{summary}\n\n📌 价值提炼：\n{key_pts}\n\n🔗 推荐双链与标签：{links}  {tags}"
            self.txt_ai.insert(tk.END, ai_display)
            self.status_lbl.config(text="✓ 翻译与 AI 洞察分析全部就绪", fg=self.theme["accent_green"])

        self.dialog.after(0, update_ai_ui)

    def copy_trans(self):
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(self.txt_trans.get("1.0", tk.END).strip())
        self.status_lbl.config(text="✓ 译文已复制到系统剪贴板！", fg=self.theme["accent_blue"])

    def save_to_obsidian(self):
        orig = self.txt_orig.get("1.0", tk.END).strip()
        trans = self.txt_trans.get("1.0", tk.END).strip()
        self.writer.save_translation(self.image, orig, trans, ai_data=self.ai_data)
        self.status_lbl.config(text="✓ 已结构化存入今日 Obsidian 日记！", fg=self.theme["accent_green"])
        self.dialog.after(1200, self.dialog.destroy)


class OCRExtractDialog:
    """截图文字提取专属悬浮面板 (支持全屏拖动、深浅苹果双色系)"""
    def __init__(self, parent, image: Image.Image, writer: ObsidianWriter):
        self.theme = ThemeManager.load_theme()
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("OmniCapture 截图文字提取 (OCR)")
        self.dialog.attributes("-topmost", True)
        self.dialog.overrideredirect(True)  # 沉浸式无边框，通过 macOS 顶栏拖动

        # 居中偏上定位
        screen_w = self.dialog.winfo_screenwidth()
        screen_h = self.dialog.winfo_screenheight()
        w, h = 580, 480
        x = max(20, (screen_w - w) // 2)
        y = max(20, (screen_h - h) // 2 - 20)
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())

        self.image = image
        self.writer = writer
        self.extracted_text = "正在识别中..."

        self._build_ui()
        self.apply_theme()

        # 异步识别
        threading.Thread(target=self._async_ocr, daemon=True).start()

    def _build_ui(self):
        self.outer_frame = tk.Frame(self.dialog, padx=1, pady=1)
        self.outer_frame.pack(fill="both", expand=True)

        self.main_frame = tk.Frame(self.outer_frame, padx=16, pady=12)
        self.main_frame.pack(fill="both", expand=True)

        # 1. 顶部标题栏 (支持鼠标拖拽)
        self.top_bar = tk.Frame(self.main_frame)
        self.top_bar.pack(fill="x", pady=(0, 10))

        traffic_box = tk.Frame(self.top_bar)
        traffic_box.pack(side="left", padx=(0, 12))

        self.dot_red = tk.Label(traffic_box, text="●", font=("Arial", 12), cursor="hand2")
        self.dot_red.pack(side="left", padx=2)
        self.dot_red._is_interactive = True
        self.dot_red.bind("<Button-1>", lambda e: self.dialog.destroy())

        self.dot_yellow = tk.Label(traffic_box, text="●", font=("Arial", 12), cursor="hand2")
        self.dot_yellow.pack(side="left", padx=2)
        self.dot_yellow._is_interactive = True
        self.dot_yellow.bind("<Button-1>", lambda e: self.txt_content.delete("1.0", tk.END))

        self.dot_green = tk.Label(traffic_box, text="●", font=("Arial", 12), cursor="hand2")
        self.dot_green.pack(side="left", padx=2)
        self.dot_green._is_interactive = True
        self.dot_green.bind("<Button-1>", lambda e: self.save_to_obsidian())

        self.title_lbl = tk.Label(
            self.top_bar,
            text="📝 截图文字提取 (OCR) (可按住拖动窗口)",
            font=("Microsoft YaHei UI", 10, "bold")
        )
        self.title_lbl.pack(side="left")

        # 主题切换按钮
        self.theme_btn = tk.Label(
            self.top_bar,
            text=self.theme["theme_toggle_icon"],
            font=("Microsoft YaHei UI", 9),
            padx=8,
            pady=2,
            cursor="hand2"
        )
        self.theme_btn._is_interactive = True
        self.theme_btn.pack(side="right")
        self.theme_btn.bind("<Button-1>", lambda e: self.toggle_theme())

        # 拖拽绑定
        make_window_draggable(self.dialog, self.top_bar, self.title_lbl)

        # 2. 文本卡片
        self.card_content = tk.Frame(self.main_frame, padx=1, pady=1)
        self.card_content.pack(fill="both", expand=True, pady=(0, 10))

        self.txt_content = tk.Text(
            self.card_content,
            font=("Microsoft YaHei UI", 10),
            wrap="word",
            relief="flat",
            padx=12,
            pady=10
        )
        self.txt_content.pack(fill="both", expand=True)
        self.txt_content.insert(tk.END, self.extracted_text)

        # 3. 底部操作栏
        self.btn_bar = tk.Frame(self.main_frame)
        self.btn_bar.pack(fill="x")

        self.status_lbl = tk.Label(self.btn_bar, text="正在高精度识别...", font=("Microsoft YaHei UI", 9))
        self.status_lbl.pack(side="left")

        self.btn_close = tk.Label(self.btn_bar, text=" 关闭 [Esc] ", font=("Microsoft YaHei UI", 9), padx=10, pady=5, cursor="hand2")
        self.btn_close._is_interactive = True
        self.btn_close.pack(side="right", padx=3)
        self.btn_close.bind("<Button-1>", lambda e: self.dialog.destroy())

        self.btn_copy = tk.Label(self.btn_bar, text=" 📋 复制全部文字 ", font=("Microsoft YaHei UI", 9), padx=12, pady=5, cursor="hand2")
        self.btn_copy._is_interactive = True
        self.btn_copy.pack(side="right", padx=3)
        self.btn_copy.bind("<Button-1>", lambda e: self.copy_text())

        self.btn_save = tk.Label(self.btn_bar, text=" 💾 存入 Obsidian ", font=("Microsoft YaHei UI", 9, "bold"), padx=14, pady=5, cursor="hand2")
        self.btn_save._is_interactive = True
        self.btn_save.pack(side="right", padx=3)
        self.btn_save.bind("<Button-1>", lambda e: self.save_to_obsidian())

    def apply_theme(self):
        th = self.theme
        self.dialog.configure(bg=th["bg_root"])
        self.outer_frame.configure(bg=th["bg_outer_border"])
        self.main_frame.configure(bg=th["bg_root"])
        self.top_bar.configure(bg=th["bg_root"])

        for dot, color in [(self.dot_red, th["traffic_close"]),
                           (self.dot_yellow, th["traffic_min"]),
                           (self.dot_green, th["traffic_max"])]:
            dot.master.configure(bg=th["bg_root"])
            dot.configure(fg=color, bg=th["bg_root"])

        self.title_lbl.configure(fg=th["text_primary"], bg=th["bg_root"])
        self.theme_btn.configure(
            text=th["theme_toggle_icon"],
            fg=th["btn_neutral_fg"],
            bg=th["btn_neutral_bg"]
        )

        self.card_content.configure(bg=th["input_border"])
        self.txt_content.configure(
            bg=th["bg_input"],
            fg=th["text_body"],
            insertbackground=th["accent_blue"]
        )

        self.btn_bar.configure(bg=th["bg_root"])
        self.status_lbl.configure(fg=th["text_muted"], bg=th["bg_root"])
        self.btn_close.configure(bg=th["btn_neutral_bg"], fg=th["btn_neutral_fg"])
        self.btn_copy.configure(bg=th["btn_primary_bg"], fg=th["btn_primary_fg"])
        self.btn_save.configure(bg=th["btn_success_bg"], fg=th["btn_success_fg"])

    def toggle_theme(self):
        self.theme = ThemeManager.toggle_theme()
        self.apply_theme()

    def _async_ocr(self):
        text = TranslationService.ocr_image(self.image)
        self.extracted_text = text if text else "(未能识别到清晰文字，请尝试框选文字更密集的区域)"

        def update_ui():
            self.txt_content.delete("1.0", tk.END)
            self.txt_content.insert(tk.END, self.extracted_text)
            char_count = len(self.extracted_text)
            if self.extracted_text and not self.extracted_text.startswith("("):
                self.dialog.clipboard_clear()
                self.dialog.clipboard_append(self.extracted_text)
                self.status_lbl.config(text=f"✓ 识别完成 ({char_count}字)，已自动复制！", fg=self.theme["accent_green"])
            else:
                self.status_lbl.config(text=f"✓ 识别完成，共 {char_count} 字", fg=self.theme["accent_green"])

        self.dialog.after(0, update_ui)

    def copy_text(self):
        content = self.txt_content.get("1.0", tk.END).strip()
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(content)
        self.status_lbl.config(text="✓ 已复制全部文字到剪贴板！", fg=self.theme["accent_blue"])

    def save_to_obsidian(self):
        content = self.txt_content.get("1.0", tk.END).strip()
        self.writer.save_ocr_text(self.image, content)
        self.status_lbl.config(text="✓ 已存入今日 Obsidian 日记！", fg=self.theme["accent_green"])
        self.dialog.after(1200, self.dialog.destroy)


class ScreenCaptureTool:
    def __init__(self, root=None, on_finish_callback=None):
        self.root = root
        self.on_finish_callback = on_finish_callback
        self.writer = ObsidianWriter()
        self.window = None

    def start(self):
        try:
            self.full_screenshot = ImageGrab.grab()
        except Exception:
            try:
                import mss
                with mss.MSS() as sct:
                    m = sct.monitors[0]
                    raw = sct.grab(m)
                    self.full_screenshot = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
            except Exception as e:
                print(f"[ScreenCapture] 截图捕获失败: {e}")
                return

        self.screen_w, self.screen_h = self.full_screenshot.size

        self.window = tk.Toplevel(self.root) if self.root else tk.Tk()
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)
        self.window.config(cursor="cross")

        self.canvas = tk.Canvas(
            self.window,
            width=self.screen_w,
            height=self.screen_h,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.dimmed_bg = self.full_screenshot.copy()
        darken_layer = Image.new("RGBA", self.dimmed_bg.size, (0, 0, 0, 100))
        self.dimmed_bg.paste(Image.new("RGB", self.dimmed_bg.size, (0, 0, 0)), mask=darken_layer.split()[3])
        self.dimmed_tk = ImageTk.PhotoImage(self.dimmed_bg)
        self.canvas.create_image(0, 0, anchor="nw", image=self.dimmed_tk)

        self.start_x = None
        self.start_y = None
        self.crop_box = None
        self.current_tool = None
        self.drawing_layers = []
        self.last_pen_point = None
        self.toolbar_frame = None

        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.window.bind("<Escape>", lambda e: self.close())
        self.window.bind("<Control-z>", lambda e: self.undo())
        self.window.bind("<Return>", lambda e: self.copy_to_clipboard_and_close())
        self.window.bind("<Control-s>", lambda e: self.save_to_obsidian())

    def on_mouse_down(self, event):
        x, y = event.x, event.y
        if self.crop_box is None:
            self.start_x = x
            self.start_y = y
        else:
            x1, y1, x2, y2 = self.crop_box
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.draw_start_x = x
                self.draw_start_y = y
                self.last_pen_point = (x, y)
                if self.current_tool == "pen":
                    self.current_pen_points = [(x, y)]

    def on_mouse_drag(self, event):
        x, y = event.x, event.y
        if self.crop_box is None:
            self.redraw_selection(self.start_x, self.start_y, x, y)
        elif self.current_tool and self.crop_box:
            if self.current_tool == "rect":
                self.preview_rect(self.draw_start_x, self.draw_start_y, x, y)
            elif self.current_tool == "arrow":
                self.preview_arrow(self.draw_start_x, self.draw_start_y, x, y)
            elif self.current_tool == "pen":
                self.canvas.create_line(self.last_pen_point[0], self.last_pen_point[1], x, y, fill="#FF453A", width=3, tags="annotation")
                self.current_pen_points.append((x, y))
                self.last_pen_point = (x, y)

    def on_mouse_up(self, event):
        x, y = event.x, event.y
        if self.crop_box is None and self.start_x is not None:
            x1, x2 = min(self.start_x, x), max(self.start_x, x)
            y1, y2 = min(self.start_y, y), max(self.start_y, y)
            if x2 - x1 > 20 and y2 - y1 > 20:
                self.crop_box = (x1, y1, x2, y2)
                self.cropped_img = self.full_screenshot.crop(self.crop_box).copy()
                self.show_toolbar(x2, y2)
            else:
                self.close()
        elif self.current_tool and self.crop_box:
            if self.current_tool == "rect":
                self.canvas.create_rectangle(self.draw_start_x, self.draw_start_y, x, y, outline="#FF453A", width=3, tags="annotation")
                self.drawing_layers.append(("rect", self.draw_start_x, self.draw_start_y, x, y))
            elif self.current_tool == "arrow":
                self.canvas.create_line(self.draw_start_x, self.draw_start_y, x, y, fill="#FF453A", width=3, arrow=tk.LAST, arrowshape=(12, 15, 6), tags="annotation")
                self.drawing_layers.append(("arrow", self.draw_start_x, self.draw_start_y, x, y))
            elif self.current_tool == "pen":
                self.drawing_layers.append(("pen", list(self.current_pen_points)))
            elif self.current_tool == "mosaic":
                self.apply_mosaic(self.draw_start_x, self.draw_start_y, x, y)

    def on_double_click(self, event):
        x, y = event.x, event.y
        if self.crop_box:
            x1, y1, x2, y2 = self.crop_box
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.copy_to_clipboard_and_close()

    def redraw_selection(self, x1, y1, x2, y2):
        self.canvas.delete("selection")
        rx1, rx2 = min(x1, x2), max(x1, x2)
        ry1, ry2 = min(y1, y2), max(y1, y2)

        sub_img = self.full_screenshot.crop((rx1, ry1, rx2, ry2))
        self.sub_img_tk = ImageTk.PhotoImage(sub_img)
        self.canvas.create_image(rx1, ry1, anchor="nw", image=self.sub_img_tk, tags="selection")
        self.canvas.create_rectangle(rx1, ry1, rx2, ry2, outline="#0A84FF", width=2, tags="selection")

    def preview_rect(self, x1, y1, x2, y2):
        self.canvas.delete("preview")
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="#FF453A", width=3, tags="preview")

    def preview_arrow(self, x1, y1, x2, y2):
        self.canvas.delete("preview")
        self.canvas.create_line(x1, y1, x2, y2, fill="#FF453A", width=3, arrow=tk.LAST, tags="preview")

    def apply_mosaic(self, x1, y1, x2, y2):
        cx1, cy1, cx2, cy2 = self.crop_box
        bx1, bx2 = max(cx1, min(x1, x2)), min(cx2, max(x1, x2))
        by1, by2 = max(cy1, min(y1, y2)), min(cy2, max(y1, y2))
        if bx2 > bx1 and by2 > by1:
            part = self.full_screenshot.crop((bx1, by1, bx2, by2))
            small = part.resize((max(1, (bx2 - bx1) // 10), max(1, (by2 - by1) // 10)), Image.Resampling.NEAREST)
            mosaic_part = small.resize((bx2 - bx1, by2 - by1), Image.Resampling.NEAREST)
            self.mosaic_tk = ImageTk.PhotoImage(mosaic_part)
            self.canvas.create_image(bx1, by1, anchor="nw", image=self.mosaic_tk, tags="annotation")
            self.drawing_layers.append(("mosaic", bx1, by1, mosaic_part))

    def show_toolbar(self, x, y):
        if self.toolbar_frame:
            self.toolbar_frame.destroy()

        th = ThemeManager.load_theme()
        tb_w, tb_h = 630, 44
        tb_x = min(max(10, x - tb_w), self.screen_w - tb_w - 10)
        tb_y = y + 10 if y + tb_h + 20 < self.screen_h else y - tb_h - 10

        self.toolbar_frame = tk.Frame(
            self.canvas,
            bg=th["bg_root"],
            padx=8,
            pady=4,
            highlightthickness=1,
            highlightbackground=th["bg_outer_border"]
        )
        self.canvas.create_window(tb_x, tb_y, anchor="nw", window=self.toolbar_frame)

        tools = [
            ("🟥 矩形", "rect"),
            ("➡️ 箭头", "arrow"),
            ("✏️ 画笔", "pen"),
            ("🔲 马赛克", "mosaic"),
        ]

        self.tool_btns = {}
        for text, tool_id in tools:
            btn = tk.Label(
                self.toolbar_frame,
                text=text,
                font=("Microsoft YaHei UI", 9),
                fg=th["text_body"],
                bg=th["bg_root"],
                padx=6,
                pady=3,
                cursor="hand2"
            )
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, tid=tool_id: self.select_tool(tid))
            self.tool_btns[tool_id] = btn

        undo_btn = tk.Label(
            self.toolbar_frame,
            text="↩️",
            font=("Microsoft YaHei UI", 10),
            fg=th["text_body"],
            bg=th["bg_root"],
            padx=4,
            pady=3,
            cursor="hand2"
        )
        undo_btn.pack(side="left", padx=2)
        undo_btn.bind("<Button-1>", lambda e: self.undo())

        ocr_btn = tk.Label(
            self.toolbar_frame,
            text=" 📝 提取文字 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=th["accent_blue"],
            bg=th["btn_neutral_bg"],
            padx=8,
            pady=3,
            cursor="hand2"
        )
        ocr_btn.pack(side="left", padx=3)
        ocr_btn.bind("<Button-1>", lambda e: self.trigger_ocr_extraction())

        trans_btn = tk.Label(
            self.toolbar_frame,
            text=" 🌐 翻译 ",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=th["accent_blue"],
            bg=th["btn_neutral_bg"],
            padx=8,
            pady=3,
            cursor="hand2"
        )
        trans_btn.pack(side="left", padx=3)
        trans_btn.bind("<Button-1>", lambda e: self.trigger_translation())

        tk.Label(self.toolbar_frame, text="|", fg=th["bg_outer_border"], bg=th["bg_root"]).pack(side="left", padx=3)

        copy_btn = tk.Label(
            self.toolbar_frame,
            text=" 📋 复制(Enter) ",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=th["btn_primary_fg"],
            bg=th["btn_primary_bg"],
            padx=10,
            pady=4,
            cursor="hand2"
        )
        copy_btn.pack(side="left", padx=3)
        copy_btn.bind("<Button-1>", lambda e: self.copy_to_clipboard_and_close())

        save_btn = tk.Label(
            self.toolbar_frame,
            text=" 💾 存入Obsidian ",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=th["btn_success_fg"],
            bg=th["btn_success_bg"],
            padx=10,
            pady=4,
            cursor="hand2"
        )
        save_btn.pack(side="left", padx=3)
        save_btn.bind("<Button-1>", lambda e: self.save_to_obsidian())

        close_btn = tk.Label(
            self.toolbar_frame,
            text=" ✕ ",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg=th["traffic_close"],
            bg=th["bg_root"],
            padx=5,
            pady=3,
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=2)
        close_btn.bind("<Button-1>", lambda e: self.close())

    def select_tool(self, tool_id):
        self.current_tool = tool_id
        th = ThemeManager.load_theme()
        for tid, btn in self.tool_btns.items():
            if tid == tool_id:
                btn.configure(bg=th["accent_blue"], fg="#FFFFFF")
            else:
                btn.configure(bg=th["bg_root"], fg=th["text_body"])

    def undo(self):
        if self.drawing_layers:
            self.drawing_layers.pop()
            self.canvas.delete("annotation")
            for item in self.drawing_layers:
                t = item[0]
                if t == "rect":
                    self.canvas.create_rectangle(item[1], item[2], item[3], item[4], outline="#FF453A", width=3, tags="annotation")
                elif t == "arrow":
                    self.canvas.create_line(item[1], item[2], item[3], item[4], fill="#FF453A", width=3, arrow=tk.LAST, tags="annotation")
                elif t == "pen":
                    pts = item[1]
                    for i in range(len(pts) - 1):
                        self.canvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], fill="#FF453A", width=3, tags="annotation")
                elif t == "mosaic":
                    tk_img = ImageTk.PhotoImage(item[3])
                    self.canvas.create_image(item[1], item[2], anchor="nw", image=tk_img, tags="annotation")

    def get_annotated_image(self):
        x1, y1, x2, y2 = self.crop_box
        final_img = self.full_screenshot.crop((x1, y1, x2, y2)).copy()
        draw = ImageDraw.Draw(final_img)

        for item in self.drawing_layers:
            t = item[0]
            if t == "rect":
                draw.rectangle([item[1] - x1, item[2] - y1, item[3] - x1, item[4] - y1], outline="#FF453A", width=3)
            elif t == "arrow":
                draw.line([item[1] - x1, item[2] - y1, item[3] - x1, item[4] - y1], fill="#FF453A", width=3)
            elif t == "pen":
                pts = [(p[0] - x1, p[1] - y1) for p in item[1]]
                if len(pts) > 1:
                    draw.line(pts, fill="#FF453A", width=3)
            elif t == "mosaic":
                final_img.paste(item[3], (item[1] - x1, item[2] - y1))

        return final_img

    def copy_image_to_clipboard(self, img: Image.Image):
        try:
            output = io.BytesIO()
            img.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            print(f"[Clipboard Error] {e}")
            return False

    def copy_to_clipboard_and_close(self):
        if not self.crop_box:
            self.close()
            return
        final_img = self.get_annotated_image()
        self.copy_image_to_clipboard(final_img)
        self.close()

    def trigger_ocr_extraction(self):
        if not self.crop_box:
            return
        final_img = self.get_annotated_image()
        self.close()
        OCRExtractDialog(self.root, final_img, self.writer)

    def trigger_translation(self):
        if not self.crop_box:
            return
        final_img = self.get_annotated_image()
        self.close()
        TranslationDialog(self.root, final_img, self.writer)

    def save_to_obsidian(self):
        if not self.crop_box:
            self.close()
            return

        final_img = self.get_annotated_image()
        self.copy_image_to_clipboard(final_img)
        self.writer.save_screenshot(final_img, note="屏幕截图与标注")
        self.close()

    def close(self):
        if self.window:
            self.window.destroy()
            self.window = None
        if self.on_finish_callback:
            self.on_finish_callback()

if __name__ == "__main__":
    tool = ScreenCaptureTool()
    tool.start()
    tk.mainloop()
