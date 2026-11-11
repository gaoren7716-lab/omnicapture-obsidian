import os
import time
import ctypes
from ctypes import wintypes
from PIL import ImageGrab, Image

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def get_process_name_by_pid(pid: int) -> str:
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    h_proc = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h_proc:
        return ""
    buf = ctypes.create_unicode_buffer(1024)
    size = wintypes.DWORD(1024)
    res = kernel32.QueryFullProcessImageNameW(h_proc, 0, buf, ctypes.byref(size))
    kernel32.CloseHandle(h_proc)
    if res:
        return os.path.basename(buf.value)
    return ""

def get_foreground_context() -> dict:
    """获取当前处于焦点的窗口标题与应用程序名称"""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return {"app": "系统桌面", "title": "", "raw": ""}
    
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        raw_title = buff.value.strip()
    else:
        raw_title = ""

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    proc_name = get_process_name_by_pid(pid.value).lower()

    # 应用别名与标题智能清洗
    app_map = {
        "chrome.exe": "Google Chrome",
        "msedge.exe": "Microsoft Edge",
        "brave.exe": "Brave",
        "firefox.exe": "Firefox",
        "code.exe": "VS Code",
        "obsidian.exe": "Obsidian",
        "wechat.exe": "微信",
        "acrobat.exe": "Adobe Acrobat",
        "foxitreader.exe": "福昕阅读器",
        "windowsterminal.exe": "Windows 终端",
        "notepad.exe": "记事本"
    }

    app_name = app_map.get(proc_name, proc_name.replace(".exe", "").capitalize() if proc_name else "应用程序")
    clean_title = raw_title

    # 清洗常见浏览器后缀：如 "DeepSeek 报告 - Google Chrome" -> "DeepSeek 报告"
    for suffix in [" - Google Chrome", " - Microsoft Edge", " - 个人 - Microsoft Edge", " - Brave", " - Mozilla Firefox", " - Visual Studio Code", " - 微信"]:
        if clean_title.endswith(suffix):
            clean_title = clean_title[:-len(suffix)].strip()
            break

    return {
        "app": app_name,
        "title": clean_title,
        "raw": raw_title,
        "hwnd": hwnd
    }

def capture_selected_text() -> str:
    """
    通过剪贴板序列号感知机制，零侵入探测前台选区文本。
    若用户未划选文本，绝不破坏用户原有剪贴板！
    """
    try:
        import win32clipboard
    except ImportError:
        return ""

    seq_before = user32.GetClipboardSequenceNumber()

    # 1. 模拟松开 Alt 键（避免热键残留影响 Ctrl+C）
    user32.keybd_event(0x12, 0, 0x0002, 0)  # VK_MENU (Alt) UP
    time.sleep(0.02)

    # 2. 模拟发送 Ctrl + C
    VK_CONTROL = 0x11
    VK_C = 0x43
    KEYEVENTF_KEYUP = 0x0002

    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_C, 0, 0, 0)
    time.sleep(0.01)
    user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

    # 3. 等待应用响应剪贴板
    time.sleep(0.06)
    seq_after = user32.GetClipboardSequenceNumber()

    # 如果序列号改变，说明前台成功复制了选中文本！
    if seq_after != seq_before:
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                if data and data.strip():
                    return data.strip()
            win32clipboard.CloseClipboard()
        except Exception:
            pass

    return ""

def check_clipboard_image() -> Image.Image:
    """探测剪贴板是否含图像"""
    try:
        im = ImageGrab.grabclipboard()
        if isinstance(im, Image.Image):
            return im
    except Exception:
        pass
    return None
