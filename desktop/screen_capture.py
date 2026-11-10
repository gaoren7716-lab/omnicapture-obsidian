import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, ImageTk, Image, ImageDraw
import io
import threading
from datetime import datetime
from obsidian_writer import ObsidianWriter
from translation_service import TranslationService
from ai_service import AIService

class TranslationDialog:
    """截图翻译与 AI 深度管理悬浮面板"""
    def __init__(self, parent, image: Image.Image, writer: ObsidianWriter):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🌐 OmniCapture 截图识别、翻译与 AI 深度管理")
        self.dialog.attributes("-topmost", True)
        self.dialog.configure(bg="#1E1E2E")
        self.dialog.geometry("620x640")
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())

        self.image = image
        self.writer = writer
        self.ai_service = AIService()
        self.original_text = "正在识别中..."
        self.translated_text = "正在翻译中..."
        self.ai_data = None

        main_frame = tk.Frame(self.dialog, bg="#1E1E2E", padx=16, pady=12)
        main_frame.pack(fill="both", expand=True)

        # 标题栏
        top_bar = tk.Frame(main_frame, bg="#1E1E2E")
        top_bar.pack(fill="x", pady=(0, 8))
        tk.Label(top_bar, text="🌐 截图识别、翻译与 AI 知识洞察", font=("Microsoft YaHei UI", 11, "bold"), fg="#CDD6F4", bg="#1E1E2E").pack(side="left")

        # 1. 原文部分
        tk.Label(main_frame, text="📝 原文内容 (OCR):", font=("Microsoft YaHei UI", 9, "bold"), fg="#89B4FA", bg="#1E1E2E").pack(anchor="w")
        self.txt_orig = tk.Text(main_frame, font=("Microsoft YaHei UI", 9), bg="#181825", fg="#CDD6F4", height=4, wrap="word", relief="flat", padx=8, pady=6)
        self.txt_orig.pack(fill="x", pady=(2, 6))

        # 2. 译文部分
        tk.Label(main_frame, text="🀄 中文译文:", font=("Microsoft YaHei UI", 9, "bold"), fg="#A6E3A1", bg="#1E1E2E").pack(anchor="w")
        self.txt_trans = tk.Text(main_frame, font=("Microsoft YaHei UI", 10), bg="#181825", fg="#A6E3A1", height=4, wrap="word", relief="flat", padx=8, pady=6)
        self.txt_trans.pack(fill="x", pady=(2, 6))

        # 3. AI 智能提炼与知识管理
        tk.Label(main_frame, text="🤖 AI 核心提炼与双链洞察:", font=("Microsoft YaHei UI", 9, "bold"), fg="#F9E2AF", bg="#1E1E2E").pack(anchor="w")
        self.txt_ai = tk.Text(main_frame, font=("Microsoft YaHei UI", 9), bg="#181825", fg="#F9E2AF", height=6, wrap="word", relief="flat", padx=8, pady=6)
        self.txt_ai.pack(fill="x", pady=(2, 8))
        self.txt_ai.insert(tk.END, "AI 正在分析核心观点与关联主题...")

        # 底部按钮栏
        btn_bar = tk.Frame(main_frame, bg="#1E1E2E")
        btn_bar.pack(fill="x", pady=(4, 0))

        self.status_lbl = tk.Label(btn_bar, text="正在处理...", font=("Microsoft YaHei UI", 9), fg="#6C7086", bg="#1E1E2E")
        self.status_lbl.pack(side="left")

        btn_copy = tk.Label(btn_bar, text=" 📋 复制译文 ", font=("Microsoft YaHei UI", 9), fg="#CDD6F4", bg="#313244", padx=10, pady=4, cursor="hand2")
        btn_copy.pack(side="right", padx=4)
        btn_copy.bind("<Button-1>", lambda e: self.copy_trans())

        btn_save = tk.Label(btn_bar, text=" 💾 结构化存入 Obsidian ", font=("Microsoft YaHei UI", 9, "bold"), fg="#11111B", bg="#A6E3A1", padx=12, pady=5, cursor="hand2")
        btn_save.pack(side="right", padx=4)
        btn_save.bind("<Button-1>", lambda e: self.save_to_obsidian())

        # 异步两步流水线：第一步瞬间返回翻译，第二步异步返回 AI 深度分析
        threading.Thread(target=self._async_process, daemon=True).start()

    def _async_process(self):
        # 步骤 1：0.2秒极速完成 OCR 与神经翻译
        res = TranslationService.ocr_and_translate(self.image)
        self.original_text = res.get("original", "")
        self.translated_text = res.get("translated", "")

        def update_trans_ui():
            self.txt_orig.delete("1.0", tk.END)
            self.txt_orig.insert(tk.END, self.original_text)
            self.txt_trans.delete("1.0", tk.END)
            self.txt_trans.insert(tk.END, self.translated_text)
            self.status_lbl.config(text="✓ 翻译完毕，正在进行 AI 深度解析...", fg="#89B4FA")

        self.dialog.after(0, update_trans_ui)

        # 步骤 2：AI 知识提炼与双链建议
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
            self.status_lbl.config(text="✓ 翻译与 AI 分析全部就绪", fg="#A6E3A1")

        self.dialog.after(0, update_ai_ui)

    def copy_trans(self):
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(self.txt_trans.get("1.0", tk.END).strip())
        self.status_lbl.config(text="✓ 译文已复制到剪贴板！", fg="#89B4FA")

    def save_to_obsidian(self):
        orig = self.txt_orig.get("1.0", tk.END).strip()
        trans = self.txt_trans.get("1.0", tk.END).strip()
        self.writer.save_translation(self.image, orig, trans, ai_data=self.ai_data)
        self.status_lbl.config(text="✓ 已结构化存入今日 Obsidian 日记！", fg="#A6E3A1")
        self.dialog.after(1200, self.dialog.destroy)


class OCRExtractDialog:
    """截图文字提取专属悬浮面板"""
    def __init__(self, parent, image: Image.Image, writer: ObsidianWriter):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📝 OmniCapture 截图文字提取 (OCR)")
        self.dialog.attributes("-topmost", True)
        self.dialog.configure(bg="#1E1E2E")
        self.dialog.geometry("560x460")
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.bind("<Escape>", lambda e: self.dialog.destroy())

        self.image = image
        self.writer = writer
        self.extracted_text = "正在识别中..."

        main_frame = tk.Frame(self.dialog, bg="#1E1E2E", padx=16, pady=12)
        main_frame.pack(fill="both", expand=True)

        # 标题栏
        top_bar = tk.Frame(main_frame, bg="#1E1E2E")
        top_bar.pack(fill="x", pady=(0, 8))
        tk.Label(top_bar, text="📝 截图文字提取 (OCR)", font=("Microsoft YaHei UI", 11, "bold"), fg="#CDD6F4", bg="#1E1E2E").pack(side="left")

        # 文本框
        self.txt_content = tk.Text(main_frame, font=("Microsoft YaHei UI", 10), bg="#181825", fg="#CDD6F4", wrap="word", relief="flat", padx=10, pady=10)
        self.txt_content.pack(fill="both", expand=True, pady=(2, 10))
        self.txt_content.insert(tk.END, self.extracted_text)

        # 底部操作栏
        btn_bar = tk.Frame(main_frame, bg="#1E1E2E")
        btn_bar.pack(fill="x")

        self.status_lbl = tk.Label(btn_bar, text="正在高精度识别...", font=("Microsoft YaHei UI", 9), fg="#6C7086", bg="#1E1E2E")
        self.status_lbl.pack(side="left")

        btn_copy = tk.Label(btn_bar, text=" 📋 复制全部文字 ", font=("Microsoft YaHei UI", 9, "bold"), fg="#11111B", bg="#89B4FA", padx=12, pady=5, cursor="hand2")
        btn_copy.pack(side="right", padx=4)
        btn_copy.bind("<Button-1>", lambda e: self.copy_text())

        btn_save = tk.Label(btn_bar, text=" 💾 存入 Obsidian ", font=("Microsoft YaHei UI", 9, "bold"), fg="#11111B", bg="#A6E3A1", padx=12, pady=5, cursor="hand2")
        btn_save.pack(side="right", padx=4)
        btn_save.bind("<Button-1>", lambda e: self.save_to_obsidian())

        # 异步识别
        threading.Thread(target=self._async_ocr, daemon=True).start()

    def _async_ocr(self):
        text = TranslationService.ocr_image(self.image)
        self.extracted_text = text if text else "(未能识别到清晰文字，请尝试框选文字更密集的区域)"

        def update_ui():
            self.txt_content.delete("1.0", tk.END)
            self.txt_content.insert(tk.END, self.extracted_text)
            char_count = len(self.extracted_text)
            # 默认自动复制到剪贴板，彻底降低用户操作阻力
            if self.extracted_text and not self.extracted_text.startswith("("):
                self.dialog.clipboard_clear()
                self.dialog.clipboard_append(self.extracted_text)
                self.status_lbl.config(text=f"✓ 识别完成 ({char_count}字)，已自动复制到剪贴板！", fg="#A6E3A1")
            else:
                self.status_lbl.config(text=f"✓ 识别完成，共 {char_count} 字", fg="#A6E3A1")

        self.dialog.after(0, update_ui)

    def copy_text(self):
        content = self.txt_content.get("1.0", tk.END).strip()
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(content)
        self.status_lbl.config(text="✓ 已复制全部文字到剪贴板！", fg="#89B4FA")

    def save_to_obsidian(self):
        content = self.txt_content.get("1.0", tk.END).strip()
        self.writer.save_ocr_text(self.image, content)
        self.status_lbl.config(text="✓ 已存入今日 Obsidian 日记！", fg="#A6E3A1")
        self.dialog.after(1200, self.dialog.destroy)


class ScreenCaptureTool:
    def __init__(self, root=None, on_finish_callback=None):
        self.root = root
        self.on_finish_callback = on_finish_callback
        self.writer = ObsidianWriter()
        self.window = None

    def start(self):
        # 1. 抓取全屏幕 (带多重容错)
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

        # 2. 建立全屏覆盖窗口
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

        # 变暗背景图
        self.dimmed_bg = self.full_screenshot.copy()
        darken_layer = Image.new("RGBA", self.dimmed_bg.size, (0, 0, 0, 100))
        self.dimmed_bg.paste(Image.new("RGB", self.dimmed_bg.size, (0, 0, 0)), mask=darken_layer.split()[3])
        self.dimmed_tk = ImageTk.PhotoImage(self.dimmed_bg)
        self.canvas.create_image(0, 0, anchor="nw", image=self.dimmed_tk)

        # 状态变量
        self.start_x = None
        self.start_y = None
        self.crop_box = None
        self.current_tool = None
        self.drawing_layers = []
        self.last_pen_point = None
        self.toolbar_frame = None

        # 事件绑定
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.window.bind("<Escape>", lambda e: self.close())
        self.window.bind("<Control-z>", lambda e: self.undo())
        # 默认回车 -> 复制到剪贴板并关闭
        self.window.bind("<Return>", lambda e: self.copy_to_clipboard_and_close())
        # Ctrl+S -> 存入 Obsidian
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
                self.canvas.create_line(self.last_pen_point[0], self.last_pen_point[1], x, y, fill="#EF4444", width=3, tags="annotation")
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
                self.canvas.create_rectangle(self.draw_start_x, self.draw_start_y, x, y, outline="#EF4444", width=3, tags="annotation")
                self.drawing_layers.append(("rect", self.draw_start_x, self.draw_start_y, x, y))
            elif self.current_tool == "arrow":
                self.canvas.create_line(self.draw_start_x, self.draw_start_y, x, y, fill="#EF4444", width=3, arrow=tk.LAST, arrowshape=(12, 15, 6), tags="annotation")
                self.drawing_layers.append(("arrow", self.draw_start_x, self.draw_start_y, x, y))
            elif self.current_tool == "pen":
                self.drawing_layers.append(("pen", list(self.current_pen_points)))
            elif self.current_tool == "mosaic":
                self.apply_mosaic(self.draw_start_x, self.draw_start_y, x, y)

    def on_double_click(self, event):
        """双击选区直接默认复制并退出"""
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
        self.canvas.create_rectangle(rx1, ry1, rx2, ry2, outline="#3B82F6", width=2, tags="selection")

    def preview_rect(self, x1, y1, x2, y2):
        self.canvas.delete("preview")
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="#EF4444", width=3, tags="preview")

    def preview_arrow(self, x1, y1, x2, y2):
        self.canvas.delete("preview")
        self.canvas.create_line(x1, y1, x2, y2, fill="#EF4444", width=3, arrow=tk.LAST, tags="preview")

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

        tb_w, tb_h = 600, 42
        tb_x = min(max(10, x - tb_w), self.screen_w - tb_w - 10)
        tb_y = y + 10 if y + tb_h + 20 < self.screen_h else y - tb_h - 10

        self.toolbar_frame = tk.Frame(self.canvas, bg="#1E1E2E", padx=6, pady=4, highlightthickness=1, highlightbackground="#45475A")
        self.canvas.create_window(tb_x, tb_y, anchor="nw", window=self.toolbar_frame)

        tools = [
            ("🟥 矩形", "rect"),
            ("➡️ 箭头", "arrow"),
            ("✏️ 画笔", "pen"),
            ("🔲 马赛克", "mosaic"),
        ]

        self.tool_btns = {}
        for text, tool_id in tools:
            btn = tk.Label(self.toolbar_frame, text=text, font=("Microsoft YaHei UI", 9), fg="#CDD6F4", bg="#1E1E2E", padx=5, pady=2, cursor="hand2")
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda e, tid=tool_id: self.select_tool(tid))
            self.tool_btns[tool_id] = btn

        # 撤销按钮
        undo_btn = tk.Label(self.toolbar_frame, text="↩️", font=("Microsoft YaHei UI", 10), fg="#CDD6F4", bg="#1E1E2E", padx=4, pady=2, cursor="hand2")
        undo_btn.pack(side="left", padx=2)
        undo_btn.bind("<Button-1>", lambda e: self.undo())

        # 📝 提取文字按钮 (OCR)
        ocr_btn = tk.Label(self.toolbar_frame, text=" 📝 提取文字 ", font=("Microsoft YaHei UI", 9, "bold"), fg="#89B4FA", bg="#313244", padx=6, pady=3, cursor="hand2")
        ocr_btn.pack(side="left", padx=3)
        ocr_btn.bind("<Button-1>", lambda e: self.trigger_ocr_extraction())

        # 🌐 截图翻译按钮
        trans_btn = tk.Label(self.toolbar_frame, text=" 🌐 翻译 ", font=("Microsoft YaHei UI", 9, "bold"), fg="#89B4FA", bg="#313244", padx=6, pady=3, cursor="hand2")
        trans_btn.pack(side="left", padx=3)
        trans_btn.bind("<Button-1>", lambda e: self.trigger_translation())

        # 分割线
        tk.Label(self.toolbar_frame, text="|", fg="#45475A", bg="#1E1E2E").pack(side="left", padx=3)

        # 默认分支 1：📋 复制到剪贴板 (Enter / 双击)
        copy_btn = tk.Label(self.toolbar_frame, text=" 📋 复制(Enter) ", font=("Microsoft YaHei UI", 9, "bold"), fg="#11111B", bg="#89B4FA", padx=8, pady=3, cursor="hand2")
        copy_btn.pack(side="left", padx=3)
        copy_btn.bind("<Button-1>", lambda e: self.copy_to_clipboard_and_close())

        # 可选分支 2：💾 存入 Obsidian
        save_btn = tk.Label(self.toolbar_frame, text=" 💾 存入Obsidian ", font=("Microsoft YaHei UI", 9, "bold"), fg="#11111B", bg="#A6E3A1", padx=8, pady=3, cursor="hand2")
        save_btn.pack(side="left", padx=3)
        save_btn.bind("<Button-1>", lambda e: self.save_to_obsidian())

        # 取消按钮
        close_btn = tk.Label(self.toolbar_frame, text=" ✕ ", font=("Microsoft YaHei UI", 9), fg="#F38BA8", bg="#1E1E2E", padx=4, pady=3, cursor="hand2")
        close_btn.pack(side="right", padx=2)
        close_btn.bind("<Button-1>", lambda e: self.close())

    def select_tool(self, tool_id):
        self.current_tool = tool_id
        for tid, btn in self.tool_btns.items():
            if tid == tool_id:
                btn.configure(bg="#89B4FA", fg="#11111B")
            else:
                btn.configure(bg="#1E1E2E", fg="#CDD6F4")

    def undo(self):
        if self.drawing_layers:
            self.drawing_layers.pop()
            self.canvas.delete("annotation")
            cx1, cy1, cx2, cy2 = self.crop_box
            for item in self.drawing_layers:
                t = item[0]
                if t == "rect":
                    self.canvas.create_rectangle(item[1], item[2], item[3], item[4], outline="#EF4444", width=3, tags="annotation")
                elif t == "arrow":
                    self.canvas.create_line(item[1], item[2], item[3], item[4], fill="#EF4444", width=3, arrow=tk.LAST, tags="annotation")
                elif t == "pen":
                    pts = item[1]
                    for i in range(len(pts) - 1):
                        self.canvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], fill="#EF4444", width=3, tags="annotation")
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
                draw.rectangle([item[1] - x1, item[2] - y1, item[3] - x1, item[4] - y1], outline="#EF4444", width=3)
            elif t == "arrow":
                draw.line([item[1] - x1, item[2] - y1, item[3] - x1, item[4] - y1], fill="#EF4444", width=3)
            elif t == "pen":
                pts = [(p[0] - x1, p[1] - y1) for p in item[1]]
                if len(pts) > 1:
                    draw.line(pts, fill="#EF4444", width=3)
            elif t == "mosaic":
                final_img.paste(item[3], (item[1] - x1, item[2] - y1))

        return final_img

    def copy_image_to_clipboard(self, img: Image.Image):
        """将图片以 CF_DIB 格式写入系统剪贴板"""
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
        """默认行为：复制到剪贴板并退出"""
        if not self.crop_box:
            self.close()
            return
        final_img = self.get_annotated_image()
        self.copy_image_to_clipboard(final_img)
        self.close()

    def trigger_ocr_extraction(self):
        """退出遮罩，弹出文字提取面板"""
        if not self.crop_box:
            return
        final_img = self.get_annotated_image()
        self.close()
        OCRExtractDialog(self.root, final_img, self.writer)

    def trigger_translation(self):
        if not self.crop_box:
            return
        final_img = self.get_annotated_image()
        # 退出全屏遮罩，弹出翻译面板
        self.close()
        TranslationDialog(self.root, final_img, self.writer)

    def save_to_obsidian(self):
        """可选行为：同时存入 Obsidian 并复制到剪贴板"""
        if not self.crop_box:
            self.close()
            return

        final_img = self.get_annotated_image()
        # 先复制到剪贴板，方便即时使用
        self.copy_image_to_clipboard(final_img)
        # 再存入 Obsidian 附件与日记
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
