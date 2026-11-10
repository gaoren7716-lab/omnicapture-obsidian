import json
import re
import requests
from pathlib import Path

class AIService:
    def __init__(self, config_path=None):
        if config_path is None:
            self.config_path = Path(__file__).resolve().parent.parent / "config.json"
        else:
            self.config_path = Path(config_path)

    def _get_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return cfg.get("ai", {})
        except Exception:
            return {}

    def analyze_content(self, text: str, is_translation: bool = False):
        """
        AI 深度结构化提炼与总结：
        提取：1. 一句话核心观点  2. 核心价值要点  3. 智能标签  4. Obsidian 双链关联
        """
        if not text or not text.strip():
            return self._heuristic_fallback(text)

        ai_cfg = self._get_config()

        # 1. 尝试云端 API (Gemini / OpenAI 兼容接口)
        if ai_cfg.get("enabled", False) and ai_cfg.get("api_key"):
            api_key = ai_cfg["api_key"]
            model = ai_cfg.get("model", "gemini-1.5-flash")
            base_url = ai_cfg.get("base_url", "https://generativelanguage.googleapis.com/v1beta")

            prompt = f"""你是一位顶级知识管理专家与自媒体内容创作者。请对以下摘录内容进行深度分析与提炼，严格输出标准 JSON 格式：
{{
  "summary": "一句话精炼核心观点（不超过40字）",
  "key_points": [
    "提炼的核心价值点或论据1",
    "提炼的核心价值点或论据2"
  ],
  "tags": ["推荐标签1", "推荐标签2"],
  "wikilinks": ["推荐Obsidian双链主题1", "推荐Obsidian双链主题2"]
}}

内容如下：
{text[:2500]}
"""
            try:
                if "generativelanguage.googleapis.com" in base_url:
                    url = f"{base_url}/models/{model}:generateContent?key={api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"response_mime_type": "application/json"}
                    }
                    resp = requests.post(url, json=payload, timeout=8)
                    if resp.status_code == 200:
                        data = resp.json()
                        raw = data["candidates"][0]["content"]["parts"][0]["text"]
                        return json.loads(raw)
                else:
                    url = f"{base_url.rstrip('/')}/chat/completions"
                    headers = {"Authorization": f"Bearer {api_key}"}
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2
                    }
                    resp = requests.post(url, headers=headers, json=payload, timeout=8)
                    if resp.status_code == 200:
                        content = resp.json()["choices"][0]["message"]["content"]
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0].strip()
                        return json.loads(content)
            except Exception as e:
                print(f"[AI API Warning] {e}")

        # 2. 尝试本地 Ollama (如果已启动且能在3秒内响应)
        try:
            ollama_prompt = (
                "请对以下内容进行一句话总结与关键词提取，必须返回JSON格式：\n"
                '{"summary": "核心观点", "key_points": ["要点1", "要点2"], "tags": ["标签1", "标签2"], "wikilinks": ["主题1", "主题2"]}\n\n'
                f"内容：\n{text[:1000]}"
            )
            payload = {
                "model": "qwen3.5:9b",
                "prompt": ollama_prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.2, "num_predict": 180}
            }
            resp = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=4)
            if resp.status_code == 200:
                raw_out = resp.json().get("response", "").strip()
                if raw_out:
                    return json.loads(raw_out)
        except Exception:
            pass

        # 3. 毫秒级启发式智能提取（保证 0 延时永不落空）
        return self._heuristic_fallback(text, is_translation)

    def _heuristic_fallback(self, text: str, is_translation: bool = False):
        """免 API 的极速启发式要点提取器"""
        clean = text.strip()
        lines = [l.strip() for l in clean.split("\n") if l.strip()]
        first_line = lines[0] if lines else clean[:60]
        
        # 智能提取核心短句
        summary = first_line[:60] + ("..." if len(first_line) > 60 else "")

        key_points = []
        if len(lines) > 1:
            key_points = [l[:50] for l in lines[1:3]]
        else:
            key_points = [summary]

        tags = ["素材"]
        wikilinks = ["知识管理"]

        if is_translation or "翻译" in text or re.search(r"[a-zA-Z]{4,}", text):
            tags.extend(["外文素材", "截图翻译"])
            wikilinks.extend(["外语学习", "内容创作"])
        else:
            tags.extend(["闪念速记", "选题灵感"])
            wikilinks.extend(["自媒体素材", "思考随笔"])

        return {
            "summary": summary,
            "key_points": key_points[:2],
            "tags": list(dict.fromkeys(tags))[:3],
            "wikilinks": list(dict.fromkeys(wikilinks))[:3]
        }
