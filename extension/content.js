// OmniCapture Content Script

let currentBubble = null;
let selectedText = "";
let selectedRange = null;

const API_BASE = "http://127.0.0.1:27123";

// 监听选区变化
document.addEventListener("mouseup", (e) => {
  // 如果点击的是我们自己的气泡内部，不销毁
  if (currentBubble && currentBubble.contains(e.target)) return;

  setTimeout(() => {
    const selection = window.getSelection();
    const text = selection.toString().trim();

    if (!text || text.length < 2) {
      removeBubble();
      return;
    }

    selectedText = text;
    selectedRange = selection.getRangeAt(0).cloneRange();
    const rect = selectedRange.getBoundingClientRect();

    showBubble(rect.left + window.scrollX, rect.bottom + window.scrollY + 6);
  }, 10);
});

// 点击空白区域移除气泡
document.addEventListener("mousedown", (e) => {
  if (currentBubble && !currentBubble.contains(e.target)) {
    removeBubble();
  }
});

function removeBubble() {
  if (currentBubble) {
    currentBubble.remove();
    currentBubble = null;
  }
}

function showBubble(x, y) {
  removeBubble();

  const bubble = document.createElement("div");
  bubble.className = "omni-capture-bubble";
  bubble.style.left = `${Math.max(10, x)}px`;
  bubble.style.top = `${y}px`;

  bubble.innerHTML = `
    <button class="omni-btn omni-btn-primary" id="omni-btn-quick-save">⚡ 存入Obsidian</button>
    <button class="omni-btn" id="omni-btn-annotate">💬 批注</button>
    <button class="omni-btn" id="omni-btn-ai">🤖 AI提炼</button>
    <button class="omni-btn" id="omni-btn-mark">🟡 高亮</button>
  `;

  document.body.appendChild(bubble);
  currentBubble = bubble;

  // 绑定事件
  bubble.querySelector("#omni-btn-quick-save").addEventListener("click", () => {
    sendClipToObsidian({ text: selectedText });
  });

  bubble.querySelector("#omni-btn-ai").addEventListener("click", () => {
    sendClipToObsidian({ text: selectedText, use_ai: true });
  });

  bubble.querySelector("#omni-btn-mark").addEventListener("click", () => {
    highlightSelection();
    removeBubble();
  });

  const annotateBtn = bubble.querySelector("#omni-btn-annotate");
  annotateBtn.addEventListener("click", () => {
    toggleAnnotationBox(bubble);
  });
}

function toggleAnnotationBox(bubble) {
  let box = bubble.querySelector(".omni-annotation-box");
  if (box) {
    box.remove();
    return;
  }

  box = document.createElement("div");
  box.className = "omni-annotation-box";
  box.innerHTML = `
    <textarea class="omni-annotation-input" placeholder="输入你的思考或批注... (Enter 存入)" rows="2"></textarea>
    <div style="display:flex; justify-content:flex-end; gap:6px;">
      <button class="omni-btn omni-btn-primary" id="omni-btn-submit-annot">确定存入</button>
    </div>
  `;

  bubble.appendChild(box);
  const input = box.querySelector(".omni-annotation-input");
  input.focus();

  const doSubmit = () => {
    const comment = input.value.trim();
    highlightSelection();
    sendClipToObsidian({ text: selectedText, comment: comment });
  };

  box.querySelector("#omni-btn-submit-annot").addEventListener("click", doSubmit);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || !e.shiftKey)) {
      e.preventDefault();
      doSubmit();
    }
  });
}

function highlightSelection() {
  if (!selectedRange) return;
  try {
    const mark = document.createElement("mark");
    mark.className = "omni-highlight";
    selectedRange.surroundContents(mark);
  } catch (err) {
    console.warn("无法直接包裹复杂 DOM 选区", err);
  }
}

async function sendClipToObsidian({ text, comment = "", use_ai = false }) {
  removeBubble();
  const payload = {
    text: text,
    comment: comment,
    url: window.location.href,
    title: document.title,
    tags: ["网页剪藏"],
    use_ai: use_ai
  };

  try {
    const res = await fetch(`${API_BASE}/api/clip/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      showToast("✓ 已成功存入 Obsidian 今日日记！");
    } else {
      showToast("⚠ 存入失败，请确认桌面服务已启动", true);
    }
  } catch (err) {
    showToast("⚠ 无法连接到本地 OmniCapture 桌面服务 (27123)", true);
  }
}

function showToast(message, isError = false) {
  const existing = document.querySelector(".omni-toast");
  if (existing) existing.remove();

  const toast = document.createElement("div");
  toast.className = "omni-toast";
  if (isError) {
    toast.style.borderColor = "#F38BA8";
    toast.style.color = "#F38BA8";
  }
  toast.innerText = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 2600);
}

// 接收来自 background 的通知
chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
  if (req.action === "quick_clip_selection") {
    const sel = window.getSelection().toString().trim();
    if (sel) {
      sendClipToObsidian({ text: sel });
    }
  } else if (req.action === "show_toast") {
    showToast(req.message, req.isError);
  }
});
