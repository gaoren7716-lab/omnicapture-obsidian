import tkinter as tk
from tkinter import ttk, messagebox
import threading
from PIL import ImageGrab, ImageTk, Image
from obsidian_writer import ObsidianWriter

class QuickJotWindow:
    def __init__(self, root=None, on_close_callback=None):
        self.writer = ObsidianWriter()
        self.on_close_callback = on_close_callback
        self.root = root
        self.window = None
        self.selected_tags = set()
        self.pasted_image = None

    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            self.window.attributes("-topmost", True)
            self.window.focus_force()
            self.text_input.focus_set()
            self.window.after(50, lambda: self.text_input.focus_force())
            return

        self.window = tk.Toplevel(self.root) if self.root else tk.Tk()
        self.window.title("💡 OmniCapture 闪念速记")
        self.window.attributes("-topmost", True)
        self.window.overrideredirect(True)  # 无边框沉浸式窗口
        self.window.configure(bg="#1E1E2E")

        # 居中偏上定位
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        w, h = 580, 260
        x = (screen_w - w) // 2
        y = int(screen_h * 0.22)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        # 外层圆角质感边框容器
        outer_frame = tk.Frame(self.window, bg="#313244", padx=2, pady=2)
        outer_frame.pack(fill="both", expand=True)

        main_frame = tk.Frame(outer_frame, bg="#1E1E2E", padx=16, pady=14)
        main_frame.pack(fill="both", expand=True)

        # 顶部标题栏
        top_bar = tk.Frame(main_frame, bg="#1E1E2E")
        top_bar.pack(fill="x", pady=(0, 10))

        title_lbl = tk.Label(
            top_bar,
            text="⚡ 闪念随手记  →  直接存入 Obsidian",
            font=("Microsoft YaHei UI", 11, "bold"),
            fg="#CDD6F4",
            bg="#1E1E2E"
        )
        title_lbl.pack(side="left")

        close_btn = tk.Label(
            top_bar,
            text="✕",
            font=("Microsoft YaHei UI", 10, "bold"),
            fg="#6C7086",
            bg="#1E1E2E",
            cursor="hand2"
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.hide())

        # 文本输入区域
        self.text_input = tk.Text(
            main_frame,
            font=("Microsoft YaHei UI", 11),
            bg="#181825",
            fg="#CDD6F4",
            insertbackground="#89B4FA",
            relief="flat",
            wrap="word",
            padx=10,
            pady=10,
            height=5
        )
        self.text_input.pack(fill="both", expand=True, pady=(0, 10))
        self.text_input.focus_set()

        # 标签快速选择区
        tag_bar = tk.Frame(main_frame, bg="#1E1E2E")
        tag_bar.pack(fill="x", pady=(0, 10))

        tk.Label(tag_bar, text="标签:", font=("Microsoft YaHei UI", 9), fg="#A6ADC8", bg="#1E1E2E").pack(side="left", padx=(0, 6))

        preset_tags = ["灵感", "待办", "自媒体素材", "金句", "认知"]
        self.tag_buttons = {}
        for tag in preset_tags:
            btn = tk.Label(
                tag_bar,
                text=f"#{tag}",
                font=("Microsoft YaHei UI", 9),
                fg="#89B4FA",
                bg="#313244",
                padx=8,
                pady=2,
                cursor="hand2"
            )
            btn.pack(side="left", padx=4)
            btn.bind("<Button-1>", lambda e, t=tag, b=btn: self.toggle_tag(t, b))
            self.tag_buttons[tag] = btn

        # 底部操作栏
        bottom_bar = tk.Frame(main_frame, bg="#1E1E2E")
        bottom_bar.pack(fill="x")

        hint_lbl = tk.Label(
            bottom_bar,
            text="快捷键: [Ctrl+Enter] 立即保存  |  [Esc] 退出",
            font=("Microsoft YaHei UI", 8),
            fg="#6C7086",
            bg="#1E1E2E"
        )
        hint_lbl.pack(side="left")

        save_btn = tk.Label(
            bottom_bar,
            text=" 存入 Obsidian ↵ ",
            font=("Microsoft YaHei UI", 9, "bold"),
            fg="#11111B",
            bg="#A6E3A1",
            padx=12,
            pady=4,
            cursor="hand2"
        )
        save_btn.pack(side="right")
        save_btn.bind("<Button-1>", lambda e: self.submit())

        # 键盘事件绑定
        self.window.bind("<Control-Return>", lambda e: self.submit())
        self.window.bind("<Escape>", lambda e: self.hide())
        self.window.bind("<Control-v>", lambda e: self.check_clipboard_image())

    def toggle_tag(self, tag, btn):
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
            btn.configure(bg="#313244", fg="#89B4FA")
        else:
            self.selected_tags.add(tag)
            btn.configure(bg="#89B4FA", fg="#11111B")

    def check_clipboard_image(self):
        try:
            im = ImageGrab.grabclipboard()
            if isinstance(im, Image.Image):
                self.pasted_image = im
                # 在文本框中显示提示
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
                # 提取目标 target
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
