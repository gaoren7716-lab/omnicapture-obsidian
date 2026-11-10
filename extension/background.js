// OmniCapture Background Service Worker

const API_BASE = "http://127.0.0.1:27123";

chrome.runtime.onInstalled.addListener(() => {
  // 创建右键菜单
  chrome.contextMenus.create({
    id: "omni_clip_selection",
    title: "⚡ 存入 Obsidian 今日日记",
    contexts: ["selection"]
  });

  chrome.contextMenus.create({
    id: "omni_capture_visible_tab",
    title: "📸 截取当前网页可视区存入 Obsidian",
    contexts: ["page", "image"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "omni_clip_selection") {
    const text = info.selectionText;
    if (!text) return;

    try {
      const res = await fetch(`${API_BASE}/api/clip/text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          url: tab.url,
          title: tab.title,
          tags: ["网页剪藏"]
        })
      });

      if (res.ok) {
        notifyTab(tab.id, "✓ 已存入 Obsidian 今日日记！", false);
      } else {
        notifyTab(tab.id, "⚠ 存入失败，请确认桌面服务运行正常", true);
      }
    } catch (err) {
      notifyTab(tab.id, "⚠ 无法连接桌面服务，请先启动 run_desktop.bat", true);
    }
  } else if (info.menuItemId === "omni_capture_visible_tab") {
    try {
      const dataUrl = await chrome.tabs.captureVisibleTab(null, { format: "png" });
      const res = await fetch(`${API_BASE}/api/clip/image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_base64: dataUrl,
          url: tab.url,
          note: `网页截屏: ${tab.title}`
        })
      });

      if (res.ok) {
        notifyTab(tab.id, "✓ 网页截屏已存入 Obsidian 附件与日记！", false);
      } else {
        notifyTab(tab.id, "⚠ 网页截图保存失败", true);
      }
    } catch (err) {
      notifyTab(tab.id, "⚠ 截图处理失败或桌面端未启动", true);
    }
  }
});

function notifyTab(tabId, message, isError = false) {
  if (!tabId) return;
  chrome.tabs.sendMessage(tabId, {
    action: "show_toast",
    message: message,
    isError: isError
  }).catch(() => {});
}
