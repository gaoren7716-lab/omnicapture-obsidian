import os
import json
import threading
from datetime import datetime
from pathlib import Path
from PIL import Image

_lock = threading.Lock()

class ObsidianWriter:
    def __init__(self, config_path=None):
        if config_path is None:
            self.config_path = Path(__file__).resolve().parent.parent / "config.json"
        else:
            self.config_path = Path(config_path)
        self.reload_config()

    def reload_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except Exception:
            self.config = {
                "obsidian_vault_path": os.path.expanduser("~/Documents/Obsidian Vault"),
                "daily_notes_folder": "每日闪记",
                "attachments_folder": "attachments",
                "inbox_folder": "收件箱",
                "save_mode": "daily_append"
            }
        self.vault_path = Path(self.config.get("obsidian_vault_path", ""))
        self.daily_folder = self.vault_path / self.config.get("daily_notes_folder", "每日闪记")
        self.attachments_folder = self.vault_path / self.config.get("attachments_folder", "attachments")
        self.inbox_folder = self.vault_path / self.config.get("inbox_folder", "收件箱")

        # Ensure folders exist
        for folder in [self.vault_path, self.daily_folder, self.attachments_folder, self.inbox_folder]:
            if folder and not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)

    def _get_today_daily_file(self):
        self.reload_config()
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_file = self.daily_folder / f"{today_str}.md"
        if not daily_file.exists():
            header = f"# 📅 {today_str} 随手记与素材捕获\n\n---\n\n"
            with open(daily_file, "w", encoding="utf-8") as f:
                f.write(header)
        return daily_file

    def _write_to_daily_file(self, content_block: str):
        """将内容块智能写入今日日记，支持锚点二级标题归档与普通追加"""
        daily_file = self._get_today_daily_file()
        anchor = self.config.get("daily_anchor_heading", "").strip()
        
        if not anchor:
            with open(daily_file, "a", encoding="utf-8") as f:
                f.write("\n" + content_block.strip() + "\n\n---\n")
            return daily_file

        with open(daily_file, "r", encoding="utf-8") as f:
            file_text = f.read()

        if anchor not in file_text:
            new_text = file_text.rstrip() + f"\n\n{anchor}\n\n" + content_block.strip() + "\n\n---\n"
        else:
            # 找到锚点标题后的位置，追加在该 section 末尾（在下一个一级/二级标题前）
            idx = file_text.find(anchor)
            after_heading = idx + len(anchor)
            lines = file_text[after_heading:].split("\n")
            insert_offset = len(file_text)
            curr_pos = after_heading

            for line in lines:
                s_line = line.strip()
                if (s_line.startswith("# ") or s_line.startswith("## ")) and not s_line.startswith(anchor):
                    insert_offset = curr_pos
                    break
                curr_pos += len(line) + 1

            prefix = file_text[:insert_offset].rstrip()
            suffix = file_text[insert_offset:].lstrip("\r\n")
            if suffix:
                new_text = prefix + "\n\n" + content_block.strip() + "\n\n" + suffix
            else:
                new_text = prefix + "\n\n" + content_block.strip() + "\n"

        with open(daily_file, "w", encoding="utf-8") as f:
            f.write(new_text)

        return daily_file

    def save_quick_jot(self, text: str, tags: list = None, images: list = None, quote: str = "", context: dict = None):
        """双轨自适应智能沉淀：支持思考、屏幕划词引用、截图附件与前台来源溯源"""
        with _lock:
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            tags = tags or []
            tag_str = " ".join([f"#{t.lstrip('#')}" for t in tags if t])
            
            clean_text = (text or "").strip()
            is_todo = clean_text.startswith("- [ ]") or clean_text.startswith("- [x]")

            if is_todo:
                title_line = f"### {time_str} 📋 待办闪记 {tag_str}".strip()
            elif quote:
                title_line = f"### {time_str} 💡 摘录与灵感思考 {tag_str}".strip()
            else:
                title_line = f"### {time_str} 💡 随手灵感 {tag_str}".strip()

            lines = [title_line]

            # 1. 思考内容
            if clean_text:
                if is_todo:
                    lines.append(clean_text)
                else:
                    lines.append(f"- **思考心流**：{clean_text}")

            # 2. 屏幕划词摘录 Callout
            if quote and quote.strip():
                quote_lines = quote.strip().split("\n")
                formatted_quote = "\n> ".join(quote_lines)
                lines.append(f"> [!quote] 选中文本摘录\n> {formatted_quote}")

            # 3. 附带图片
            if images:
                for img_rel in images:
                    lines.append(f"> 附带截图: ![[{img_rel}]]")

            # 4. 前台来源自动追溯 (乔木核心亮点)
            if context:
                app_name = context.get("app", "")
                src_title = context.get("title", "")
                src_url = context.get("url", "")
                
                if src_title or app_name or src_url:
                    if src_url and src_title:
                        src_str = f"[{src_title}]({src_url})"
                    elif src_title:
                        src_str = src_title
                    else:
                        src_str = src_url or app_name

                    app_str = f" (来自 {app_name})" if app_name and app_name not in src_str else ""
                    lines.append(f"- 来源出处: {src_str}{app_str}")

            content_block = "\n".join(lines)
            daily_file = self._write_to_daily_file(content_block)
            
            return {
                "status": "success",
                "file": str(daily_file),
                "time": time_str
            }

    def save_web_clip(self, text: str, comment: str = "", url: str = "", title: str = "", tags: list = None):
        """Save selected text and comment from a webpage."""
        with _lock:
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            tags = tags or ["素材", "网页剪藏"]
            tag_str = " ".join([f"#{t.lstrip('#')}" for t in tags if t])

            display_title = title.strip() or url or "未知网页"
            source_link = f"[{display_title}]({url})" if url else display_title

            lines = [f"\n### 🔖 {time_str} 网页标注 {tag_str}".strip()]
            lines.append(f"- **来源**: {source_link}")
            
            # Formatted quote
            quote_text = "\n> ".join(text.strip().split("\n"))
            lines.append(f"> {quote_text}")

            if comment and comment.strip():
                lines.append(f"\n**💭 我的批注**: {comment.strip()}")
            
            lines.append("\n---\n")
            content_to_append = "\n".join(lines)

            daily_file = self._get_today_daily_file()
            with open(daily_file, "a", encoding="utf-8") as f:
                f.write(content_to_append)

            return {
                "status": "success",
                "file": str(daily_file),
                "time": time_str
            }

    def save_screenshot(self, pil_image: Image.Image, note: str = "", source_url: str = "", tags: list = None):
        """Save a screenshot directly into attachments folder and reference in daily note."""
        with _lock:
            self.reload_config()
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            file_ts = now.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{file_ts}.png"
            
            abs_image_path = self.attachments_folder / filename
            pil_image.save(abs_image_path, format="PNG")

            # Relative path for Obsidian wikilink
            rel_folder = self.config.get("attachments_folder", "attachments").strip("/\\")
            wikilink_target = f"{rel_folder}/{filename}" if rel_folder else filename

            tags = tags or ["截图", "视觉素材"]
            tag_str = " ".join([f"#{t.lstrip('#')}" for t in tags if t])

            lines = [f"\n### 📸 {time_str} 屏幕截图 {tag_str}".strip()]
            if source_url:
                lines.append(f"- **来源**: {source_url}")
            
            lines.append(f"\n![[{wikilink_target}]]\n")

            if note and note.strip():
                lines.append(f"**📝 备注**: {note.strip()}\n")

            lines.append("---\n")
            content_to_append = "\n".join(lines)

            daily_file = self._get_today_daily_file()
            with open(daily_file, "a", encoding="utf-8") as f:
                f.write(content_to_append)

            return {
                "status": "success",
                "file": str(daily_file),
                "image": str(abs_image_path),
                "wikilink": f"![[{wikilink_target}]]"
            }

    def save_translation(self, pil_image: Image.Image, original_text: str, translated_text: str, ai_data: dict = None):
        """Save screenshot with OCR text, translation and structured AI insights directly to daily note."""
        with _lock:
            self.reload_config()
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            file_ts = now.strftime("%Y%m%d_%H%M%S")
            filename = f"trans_{file_ts}.png"
            
            abs_image_path = self.attachments_folder / filename
            pil_image.save(abs_image_path, format="PNG")

            rel_folder = self.config.get("attachments_folder", "attachments").strip("/\\")
            wikilink_target = f"{rel_folder}/{filename}" if rel_folder else filename

            # 聚合标签
            tags = ["截图翻译", "素材"]
            if ai_data and ai_data.get("tags"):
                tags.extend(ai_data["tags"])
            tag_str = " ".join([f"#{t.lstrip('#')}" for t in list(dict.fromkeys(tags)) if t])

            lines = [f"\n### 🌐 {time_str} 截图翻译与 AI 洞察 {tag_str}"]
            
            # Obsidian 专属 Callout 1：视觉快照与对照
            lines.append("> [!quote] 📸 视觉快照与中英对照")
            lines.append(f"> ![[{wikilink_target}]]")
            lines.append(">")
            
            orig_quote = "\n> ".join(original_text.strip().split("\n"))
            trans_quote = "\n> ".join(translated_text.strip().split("\n"))
            lines.append(f"> **📝 原文 (OCR)**:\n> {orig_quote}")
            lines.append(">")
            lines.append(f"> **🀄 中文译文**:\n> {trans_quote}")

            # Obsidian 专属 Callout 2：AI 深度提炼与双链管理
            if ai_data:
                lines.append("\n> [!tip] 🤖 AI 智能提炼与管理")
                if ai_data.get("summary"):
                    lines.append(f"> - **💡 核心观点**: {ai_data['summary']}")
                if ai_data.get("key_points"):
                    lines.append("> - **📌 价值提取**:")
                    for pt in ai_data["key_points"]:
                        lines.append(f">   - {pt}")
                if ai_data.get("wikilinks"):
                    links_str = " | ".join([f"[[{w.strip('[]')}]]" for w in ai_data["wikilinks"] if w])
                    lines.append(f"> - **🔗 双链主题**: {links_str}")

            lines.append("\n---\n")
            
            content_to_append = "\n".join(lines)
            daily_file = self._get_today_daily_file()
            with open(daily_file, "a", encoding="utf-8") as f:
                f.write(content_to_append)

            return {
                "status": "success",
                "file": str(daily_file),
                "image": str(abs_image_path)
            }

    def save_ocr_text(self, pil_image: Image.Image, text: str, tags: list = None):
        """Save OCR extracted text and screenshot directly to daily note."""
        with _lock:
            self.reload_config()
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            file_ts = now.strftime("%Y%m%d_%H%M%S")
            filename = f"ocr_{file_ts}.png"
            
            abs_image_path = self.attachments_folder / filename
            pil_image.save(abs_image_path, format="PNG")

            rel_folder = self.config.get("attachments_folder", "attachments").strip("/\\")
            wikilink_target = f"{rel_folder}/{filename}" if rel_folder else filename

            tags = tags or ["文字提取", "素材"]
            tag_str = " ".join([f"#{t.lstrip('#')}" for t in list(dict.fromkeys(tags)) if t])

            lines = [f"\n### 📝 {time_str} 截图提取文字 {tag_str}"]
            lines.append(f"\n![[{wikilink_target}]]\n")
            lines.append(text.strip())
            lines.append("\n\n---\n")

            content_to_append = "\n".join(lines)
            daily_file = self._get_today_daily_file()
            with open(daily_file, "a", encoding="utf-8") as f:
                f.write(content_to_append)

            return {
                "status": "success",
                "file": str(daily_file),
                "image": str(abs_image_path)
            }

    def save_full_article(self, title: str, url: str, markdown_content: str, author: str = "", tags: list = None):
        """Save full article clip as an individual card in Inbox."""
        with _lock:
            self.reload_config()
            now = datetime.now()
            file_date = now.strftime("%Y-%m-%d")
            
            # Clean filename
            safe_title = "".join(c for c in title if c not in r'\/:*?"<>|').strip() or "未命名剪藏"
            safe_title = safe_title[:60]
            filename = f"{file_date}_{safe_title}.md"
            target_file = self.inbox_folder / filename

            tags = tags or ["文章剪藏"]
            tag_list = "\n".join([f"  - {t.lstrip('#')}" for t in tags])
            clean_title = title.replace('"', '\\"')

            frontmatter = f"""---
title: "{clean_title}"
date: {now.strftime("%Y-%m-%d %H:%M:%S")}
source: "{url}"
author: "{author}"
tags:
{tag_list}
---

# {title}

- **原文链接**: [{url}]({url})
- **捕获时间**: {now.strftime("%Y-%m-%d %H:%M:%S")}

---

{markdown_content}
"""
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(frontmatter)

            return {
                "status": "success",
                "file": str(target_file)
            }
