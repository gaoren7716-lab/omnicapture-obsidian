import os
import sys
import json
import queue
import threading
import ctypes
from ctypes import wintypes
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import uvicorn

# 确保在 pythonw 无控制台环境下 print 不会因 NoneType 报错
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")

# 确保本目录模块优先加载
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# 开启 Windows 高分屏 DPI 适配
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from obsidian_writer import ObsidianWriter
from quick_jot import QuickJotWindow
from screen_capture import ScreenCaptureTool

class NativeWindowsHotkeys:
    """Windows 原生系统级快捷键注册器 (基于 RegisterHotKey，100% 避开输入法与软件拦截)"""
    def __init__(self, on_jot, on_capture):
        self.on_jot = on_jot
        self.on_capture = on_capture
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        user32 = ctypes.windll.user32
        MOD_ALT = 0x0001
        MOD_NOREPEAT = 0x4000
        WM_HOTKEY = 0x0312
        HOTKEY_ID_JOT = 1
        HOTKEY_ID_CAPTURE = 2

        # 注册 Alt+J (闪念) 和 Alt+X (截图)
        r1 = user32.RegisterHotKey(None, HOTKEY_ID_JOT, MOD_ALT | MOD_NOREPEAT, ord('J'))
        r2 = user32.RegisterHotKey(None, HOTKEY_ID_CAPTURE, MOD_ALT | MOD_NOREPEAT, ord('X'))
        print(f"[OmniCapture] Windows 原生全局热键注册结果: Alt+J: {bool(r1)}, Alt+X: {bool(r2)}")

        msg = wintypes.MSG()
        while self.running:
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res <= 0:
                break
            if msg.message == WM_HOTKEY:
                if msg.wParam == HOTKEY_ID_JOT:
                    self.on_jot()
                elif msg.wParam == HOTKEY_ID_CAPTURE:
                    self.on_capture()
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(None, HOTKEY_ID_JOT)
        user32.UnregisterHotKey(None, HOTKEY_ID_CAPTURE)

class OmniCaptureApp:
    def __init__(self):
        self.base_dir = CURRENT_DIR.parent
        self.config_path = self.base_dir / "config.json"
        self.writer = ObsidianWriter(self.config_path)

        # 跨线程操作队列（保证 GUI 必在 Tkinter 主线程执行）
        self.action_queue = queue.Queue()

        # Tk 主线程与隐藏宿主窗口
        self.root = tk.Tk()
        self.root.withdraw()

        self.jot_window = QuickJotWindow(self.root)
        self.capture_tool = ScreenCaptureTool(self.root)

        # 启动主线程心跳轮询队列 (40ms)
        self.root.after(40, self._process_queue)

    def _process_queue(self):
        try:
            while not self.action_queue.empty():
                action = self.action_queue.get_nowait()
                if action == "jot":
                    self.jot_window.show()
                elif action == "capture":
                    self.capture_tool.start()
        except Exception as e:
            print(f"[Queue Error] {e}")
        self.root.after(40, self._process_queue)

    def start_api_server(self):
        cfg = self.writer.config
        host = cfg.get("server_host", "127.0.0.1")
        port = cfg.get("server_port", 27123)

        def run_uvicorn():
            from api_server import app
            uvicorn.run(app, host=host, port=port, log_level="warning")

        server_thread = threading.Thread(target=run_uvicorn, daemon=True)
        server_thread.start()
        print(f"[OmniCapture] 本地核心服务已启动: http://{host}:{port}")

    def trigger_quick_jot(self):
        self.action_queue.put("jot")

    def trigger_screen_capture(self):
        self.action_queue.put("capture")

    def open_obsidian_daily(self):
        daily_file = self.writer._get_today_daily_file()
        if daily_file.exists():
            os.startfile(str(daily_file))

    def open_config(self):
        if self.config_path.exists():
            os.startfile(str(self.config_path))

    def start_global_hotkeys(self):
        self.hotkey_listener = NativeWindowsHotkeys(
            on_jot=self.trigger_quick_jot,
            on_capture=self.trigger_screen_capture
        )
        self.hotkey_listener.start()

    def create_tray_icon(self):
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([4, 4, 60, 60], fill="#7C3AED")
        draw.polygon([(36, 12), (20, 36), (32, 36), (28, 52), (46, 28), (34, 28)], fill="#FDE047")

        menu = pystray.Menu(
            item("💡 闪念速记 (Alt+J)", lambda: self.trigger_quick_jot()),
            item("📸 截图标注 (Alt+X)", lambda: self.trigger_screen_capture()),
            pystray.Menu.SEPARATOR,
            item("📅 打开今日 Obsidian 日记", lambda: self.open_obsidian_daily()),
            item("📂 打开知识库目录", lambda: os.startfile(str(self.writer.vault_path))),
            item("⚙️ 编辑设置 (config.json)", lambda: self.open_config()),
            pystray.Menu.SEPARATOR,
            item("❌ 退出程序", lambda: self.quit_app())
        )

        self.tray = pystray.Icon("OmniCapture", img, "OmniCapture for Obsidian", menu)

        def run_tray():
            self.tray.run()

        tray_thread = threading.Thread(target=run_tray, daemon=True)
        tray_thread.start()

    def quit_app(self):
        if hasattr(self, 'hotkey_listener') and self.hotkey_listener:
            self.hotkey_listener.running = False
        if hasattr(self, 'tray') and self.tray:
            self.tray.stop()
        self.root.quit()
        sys.exit(0)

    def run(self):
        self.start_api_server()
        self.start_global_hotkeys()
        self.create_tray_icon()
        print("\n========================================================")
        print("  OmniCapture for Obsidian 已常驻后台运行！")
        print("  - 快捷键 闪念速记: Alt + J (Windows 原生内核级无冲突)")
        print("  - 快捷键 截图标注: Alt + X (Windows 原生内核级无冲突)")
        print(f"  - Obsidian 库路径: {self.writer.vault_path}")
        print("========================================================\n")
        self.root.mainloop()

if __name__ == "__main__":
    app = OmniCaptureApp()
    app.run()
