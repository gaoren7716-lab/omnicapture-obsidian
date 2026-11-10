# ⚡ OmniCapture for Obsidian

<p align="center">
  <strong>桌面与网页双轨协同的 AI 随手捕获与知识沉淀枢纽</strong><br>
  随时截图 · 快速复制 · 文字提取(OCR) · 截图翻译 · 网页划词批注 · 全局闪念速记 · 统一无缝入库 Obsidian
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6.svg?logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12-brightgreen.svg?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Extension-Chrome%20MV3-F1502F.svg?logo=googlechrome" alt="Chrome MV3">
  <img src="https://img.shields.io/badge/Obsidian-Native%20Compatible-7C3AED.svg?logo=obsidian" alt="Obsidian">
</p>

---

## 📖 项目愿景

在日常阅读网页、看视频、文献调研或自媒体创作时，我们常常需要：
1. **随时截图**，框选重点并随手做红框/箭头/马赛克标注；
2. **快速复制**，双击或按回车就能直接粘贴到微信/文档中；
3. **提取文字 (OCR)**，图片里的文字一键提取并自动复制到剪贴板；
4. **截图翻译**，遇上外文文献/报错信息，一键整句识别并地道翻译；
5. **网页划词批注**，读文章时选中文本弹出气泡，边读边留下自己的思考；
6. **闪念速记**，灵感闪现时按快捷键呼出小窗，写完即走；
7. **统一管理**，所有图片、双语对照、AI 提炼和思考，**全部无感落库至本地 Obsidian 知识库**，自动点亮全局知识图谱。

**OmniCapture** 就是为了彻底消灭信息收集的“切换摩擦力”而生的轻量开源利器。

---

## 🌟 核心功能特性

### 1. 📸 随时全屏截图标注 (`Alt + X`)
- **全局原生热键**：采用 Windows 内核级热键注册机制，0 冲突、不丢事件。
- **丰富标注工具**：矩形框、指示箭头、自由画笔、马赛克（保护隐私）、撤销操作。
- **多通道顺畅分支**：
  - **默认复制（顺手极速）**：选区内**双击鼠标**或敲击 **`Enter`**，直接复制带标注截图并退出，随时 `Ctrl+V` 粘贴；
  - **📝 提取文字 (OCR)**：基于工业级 PP-OCR v4 引擎，0.05 秒提取文字并自动入剪贴板；
  - **🌐 截图翻译**：智能段落与语法重构，彻底解决换行生硬断词问题，整句地道中英互译；
  - **💾 存入 Obsidian**：高清图片自动归档至 `attachments/`，并在今日日记中插入标准引用。

### 2. 🤖 AI 智能提炼与双链洞察
- 自动提取 **1句话核心观点** 与 **2-3条关键论据**；
- 自动生成 **#素材分类标签**；
- 自动推荐并挂载 **`[[Obsidian 双链主题]]`**；
- 在 Obsidian 中自动排版为标准的官方 **`[!quote]` 对照卡片** 与 **`[!tip]` 洞察卡片**。

### 3. 💡 全局闪念速记小窗 (`Alt + J`)
- 类似 Spotlight / Raycast 的极简暗黑毛玻璃小窗；
- 支持打字备忘、随手记录思考灵感；
- 支持直接 `Ctrl+V` 粘贴图片（自动保存为附件并引用）；
- 支持快捷标签芯片（`#灵感`、`#选题`、`#待办`、`#金句`）；
- 按 `Ctrl+Enter` 秒存入今日日记，按 `Esc` 退出。

### 4. 🔖 浏览器划词高亮与批注（Chrome / Edge 扩展）
- 在任何网页（微信公众号、知乎、技术文档、新闻）选中文本，立即在旁边浮现微型操作气泡：
  - **⚡ 存入Obsidian**：一秒打包原文、来源链接、文章标题与捕获时间；
  - **💬 写批注**：即时展开行内小窗记录你的灵感思考；
  - **🤖 AI 提炼**：自动调用大模型提炼核心要点；
  - **🟡 网页高亮**：在当前网页上做黄色色块持久标记。
- 支持一键整篇网页文章抓取（Clean Article Clip）。

---

## 🏗️ 架构设计：双端一枢纽

```
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│     网页扩展 (Chrome/Edge MV3)    │         │      桌面宿主 (Python/Tkinter)   │
│  - 划词高亮 (Highlight)         │         │  - 全局闪念小窗 (Alt+J)         │
│  - 行内批注 (Annotation)        │         │  - 截图标注/文字提取 (Alt+X)    │
│  - 页面一键剪藏 (Full Clip)     │         │  - 截图翻译与 AI 深度分析       │
└────────────────┬────────────────┘         └────────────────┬────────────────┘
                 │                                           │
                 │ HTTP POST (http://127.0.0.1:27123)        │ 内部事件线程安全队列
                 └─────────────────────┬─────────────────────┘
                                       ▼
                   ┌──────────────────────────────────────┐
                   │   本地核心守护枢纽 (FastAPI Hub)     │
                   │  - 仅监听本机 127.0.0.1:27123        │
                   │  - RapidOCR + 神经翻译管道           │
                   │  - AI 摘要与双链自动生成引擎         │
                   └───────────────────┬──────────────────┘
                                       ▼
                   ┌──────────────────────────────────────┐
                   │         Obsidian 本地知识库          │
                   │  - 今日日记追加: 每日闪记/YYYY-MM-DD.md│
                   │  - 附件图片存储: attachments/        │
                   │  - 原生 Callout 卡片 + 图谱双链支持  │
                   └──────────────────────────────────────┘
```

---

## 🚀 快速上手与运行

### 1. 环境准备与依赖安装
确保电脑已安装 Python 3.11 或 3.12：
```bash
git clone https://github.com/gaoren7716-lab/omnicapture-obsidian.git
cd omnicapture-obsidian
pip install -r requirements.txt
```

### 2. 启动桌面端后台服务
双击运行根目录下的：
```bash
run_desktop.bat
```
- 程序自动常驻在右下角任务栏系统托盘（紫色闪电图标）；
- 本地端口 `http://127.0.0.1:27123` 自动就绪；
- 全局快捷键 `Alt+J` 与 `Alt+X` 实时生效。

### 3. 安装浏览器扩展（Chrome / Edge）
1. 打开浏览器扩展管理页：
   - Chrome：地址栏访问 `chrome://extensions/`
   - Edge：地址栏访问 `edge://extensions/`
2. 开启右上角的 **“开发者模式” (Developer mode)**；
3. 点击 **“加载已解压的扩展程序” (Load unpacked)**；
4. 选择本项目中的 `extension` 文件夹即可完成安装！

---

## ⚙️ 配置文件说明 (`config.json`)

系统配置文件位于根目录 `config.json`：
```json
{
  "obsidian_vault_path": "F:/1 内容创作/5 自媒体Obsidian库",
  "daily_notes_folder": "自媒体素材/每日闪记",
  "attachments_folder": "自媒体素材/attachments",
  "inbox_folder": "自媒体素材/收件箱",
  "save_mode": "daily_append",
  "hotkeys": {
    "quick_jot": "<alt>+j",
    "screen_capture": "<alt>+x"
  },
  "ai": {
    "enabled": false,
    "provider": "gemini",
    "api_key": "",
    "base_url": "https://generativelanguage.googleapis.com/v1beta",
    "model": "gemini-1.5-flash"
  }
}
```

- **Obsidian 路径**：修改 `obsidian_vault_path` 指向你电脑上的任意 Obsidian 库；
- **AI 增强（可选）**：支持配置 Gemini、OpenAI 兼容端点或本地 Ollama 模型，开启后将由大模型进行深度解读与标签预测。

---

## ⌨️ 快捷键速查表

| 按键 | 功能 | 说明 |
| :--- | :--- | :--- |
| **`Alt + J`** | **💡 闪念速记** | 呼出输入框随手记想法、贴图片；`Ctrl+Enter` 存入，`Esc` 退出 |
| **`Alt + X`** | **📸 全屏截图** | 框选区域后：<br>• **双击选区 / 回车**：默认复制截图到剪贴板<br>• **点击 [📝 提取文字]**：提取文字并自动进剪贴板<br>• **点击 [🌐 翻译]**：智能翻译 + AI 提炼<br>• **点击 [💾 存入Obsidian]**：原图与引用入库 |
| **网页划词** | **🔖 划词工具条** | 选中文本自动浮现气泡，支持一键入库、行内批注与高亮标记 |

---

## 📄 开源许可证

本项目基于 [MIT License](LICENSE) 开源。欢迎提 Issue、PR 或 Fork 共同改进！
