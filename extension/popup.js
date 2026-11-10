// OmniCapture Popup Script

const API_BASE = "http://127.0.0.1:27123";

document.addEventListener("DOMContentLoaded", async () => {
  const dot = document.getElementById("status-dot");
  const statusText = document.getElementById("status-text");
  const msgBox = document.getElementById("status-msg");
  const jotInput = document.getElementById("jot-input");
  const btnSaveJot = document.getElementById("btn-save-jot");
  const btnClipFull = document.getElementById("btn-clip-full");
  const btnScreenshot = document.getElementById("btn-screenshot-tab");

  function showMsg(text, isError = false) {
    msgBox.style.display = "block";
    msgBox.innerText = text;
    msgBox.style.background = isError ? "#452230" : "#243d34";
    msgBox.style.color = isError ? "#f38ba8" : "#a6e3a1";
    setTimeout(() => {
      msgBox.style.display = "none";
    }, 2500);
  }

  // 1. 检查本地服务连通性
  try {
    const res = await fetch(`${API_BASE}/api/health`, { method: "GET" });
    if (res.ok) {
      const data = await res.json();
      dot.className = "status-dot online";
      statusText.innerText = "桌面端已就绪";
    } else {
      dot.className = "status-dot";
      statusText.innerText = "服务异常";
    }
  } catch (err) {
    dot.className = "status-dot";
    statusText.innerText = "桌面服务未连接";
    showMsg("请先在桌面运行 run_desktop.bat", true);
  }

  // 2. 闪念保存
  btnSaveJot.addEventListener("click", async () => {
    const text = jotInput.value.trim();
    if (!text) return;

    try {
      btnSaveJot.innerText = "正在存入...";
      const res = await fetch(`${API_BASE}/api/quick_jot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text, tags: ["闪念", "浏览器速记"] })
      });

      if (res.ok) {
        jotInput.value = "";
        showMsg("✓ 已存入 Obsidian 今日日记！");
      } else {
        showMsg("保存失败", true);
      }
    } catch (err) {
      showMsg("网络错误，桌面服务未启动", true);
    } finally {
      btnSaveJot.innerText = "存入今日日记";
    }
  });

  // 3. 剪藏整篇网页
  btnClipFull.addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return;

    btnClipFull.innerText = "正在提取正文...";

    // 执行页面抓取
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        // 简单提取正文文本与标题
        const title = document.title;
        const url = window.location.href;
        
        // 尝试抓取主要文章内容容器
        const article = document.querySelector("article") || document.querySelector("main") || document.body;
        return {
          title: title,
          url: url,
          content: article.innerText.slice(0, 15000)
        };
      }
    }, async (results) => {
      if (results && results[0] && results[0].result) {
        const pageData = results[0].result;
        try {
          const res = await fetch(`${API_BASE}/api/clip/full`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              title: pageData.title,
              url: pageData.url,
              content: pageData.content,
              tags: ["文章剪藏"]
            })
          });

          if (res.ok) {
            showMsg("✓ 网页全文已存为独立卡片！");
          } else {
            showMsg("保存失败", true);
          }
        } catch (err) {
          showMsg("无法连接桌面服务", true);
        }
      }
      btnClipFull.innerText = "一键剪藏当前网页全文";
    });
  });

  // 4. 截取当前标签页
  btnScreenshot.addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return;

    btnScreenshot.innerText = "正在截图...";
    try {
      const dataUrl = await chrome.tabs.captureVisibleTab(null, { format: "png" });
      const res = await fetch(`${API_BASE}/api/clip/image`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_base64: dataUrl,
          url: tab.url,
          note: `网页快照: ${tab.title}`
        })
      });

      if (res.ok) {
        showMsg("✓ 截图已存入 Obsidian 附件与日记！");
      } else {
        showMsg("截图保存失败", true);
      }
    } catch (err) {
      showMsg("截图失败", true);
    } finally {
      btnScreenshot.innerText = "截取当前网页并存入";
    }
  });
});
