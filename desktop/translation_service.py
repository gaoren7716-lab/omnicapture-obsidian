import numpy as np
import requests
import json
import re
from pathlib import Path
from PIL import Image

_rapid_ocr = None
try:
    from rapidocr_onnxruntime import RapidOCR
    _rapid_ocr = RapidOCR()
except Exception as e:
    print(f"[RapidOCR Init Warning] {e}")

class TranslationService:
    @staticmethod
    def _smart_reconstruct_text(lines: list) -> str:
        """
        智能段落重构算法（核心关键）：
        将 OCR 切碎的多行文字还原为符合人类语法逻辑的自然段落与整句。
        彻底解决因换行导致 'over' 被直译为 '结束'、'jumps' 被直译为 '跳跃' 的语境丢失问题。
        """
        if not lines:
            return ""

        merged_paragraphs = []
        current_para = ""

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                if current_para:
                    merged_paragraphs.append(current_para)
                    current_para = ""
                continue

            # 1. 处理连字符断行（如 'infor-' + 'mation' -> 'information'）
            if current_para.endswith("-") and len(current_para) > 1 and current_para[-2].isalpha():
                current_para = current_para[:-1] + line
            elif not current_para:
                current_para = line
            else:
                last_char = current_para[-1]
                # 2. 如果上一行以强句末标点结束，说明是独立句子或自然段
                if last_char in ".!?。！？:：":
                    # 判断是否为序号列表项（如 1. 2. - *）
                    if re.match(r"^(\d+[\.\)]|[-*•])\s+", line):
                        merged_paragraphs.append(current_para)
                        current_para = line
                    else:
                        current_para += " " + line if current_para.isascii() else line
                else:
                    # 3. 上一行未结束：西文加空格拼接，中文无缝平滑拼接
                    if re.search(r"[a-zA-Z0-9,'\"\)\]\}]$", current_para) and re.match(r"^[a-zA-Z0-9,'\"\(\[\{]", line):
                        current_para += " " + line
                    else:
                        current_para += line

        if current_para:
            merged_paragraphs.append(current_para)

        # 修复常见的 OCR 连词小瑕疵 (如 'thelazy' -> 'the lazy')
        result_text = "\n\n".join(merged_paragraphs)
        result_text = re.sub(r"\bthe([a-z]{3,})\b", r"the \1", result_text)
        return result_text.strip()

    @classmethod
    def ocr_image(cls, pil_image: Image.Image) -> str:
        """使用专业级 RapidOCR (PP-OCR v4) 提取文字并进行语境重构"""
        if _rapid_ocr is not None:
            try:
                img_np = np.array(pil_image.convert("RGB"))
                result, _ = _rapid_ocr(img_np)
                if result:
                    raw_lines = [item[1].strip() for item in result if item and len(item) > 1 and item[1].strip()]
                    # 经过自然语法重构后再返回
                    return cls._smart_reconstruct_text(raw_lines)
            except Exception as e:
                print(f"[RapidOCR Error] {e}")

        # 备用：Windows 原生 winocr
        try:
            import winocr
            res = winocr.recognize_pil_sync(pil_image, "zh-Hans-CN")
            if isinstance(res, dict):
                text = res.get("text", "").strip()
                if text:
                    lines = text.split("\n")
                    return cls._smart_reconstruct_text(lines)
        except Exception as e:
            print(f"[WinOCR Error] {e}")

        return ""

    @staticmethod
    def _translate_via_ollama(text: str, model: str = "qwen3.5:9b") -> str:
        """本地 RTX 4070 GPU 大模型翻译通道"""
        try:
            prompt = (
                "你是一位精通多语言的资深翻译专家。请将以下文本翻译为通顺、自然、地道的中文。"
                "要求：信息守恒，符合中文表达习惯，只返回最终翻译文本，不要任何附带说明或分析：\n\n"
                f"{text}"
            )
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            }
            resp = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=8)
            if resp.status_code == 200:
                out = resp.json().get("response", "").strip()
                if out:
                    return out
        except Exception as e:
            print(f"[Ollama Error] {e}")
        return ""

    @classmethod
    def translate_text(cls, text: str, target_lang: str = "zh-CN") -> str:
        """
        又快又准的高精度翻译引擎：
        1. 优先采用高速神经机器翻译 API（150ms 级秒回，整句准确率高）
        2. 如需更深层次润色，自动兼容本地 GPU Ollama (qwen3.5:9b)
        """
        if not text.strip():
            return ""

        # 1. 尝试极速高质神经机器翻译 (0.2s 级别)
        try:
            clean_text = text.strip()
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q=" + requests.utils.quote(clean_text)
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                translated = "".join([item[0] for item in data[0] if item and item[0]])
                if translated.strip():
                    return translated.strip()
        except Exception as e:
            print(f"[Fast Translate Error] {e}")

        # 2. 备用：调用本地 GPU Ollama
        ollama_res = cls._translate_via_ollama(text)
        if ollama_res:
            return ollama_res

        return "(网络连接超时且本地模型未就绪，请检查网络)"

    @classmethod
    def ocr_and_translate(cls, pil_image: Image.Image):
        """一键 OCR 识别与翻译接口"""
        original = cls.ocr_image(pil_image)
        if not original:
            return {
                "original": "(未能识别到清晰文本，请尝试框选字迹对比度更高、更密集的区域)",
                "translated": ""
            }

        translated = cls.translate_text(original)
        return {
            "original": original,
            "translated": translated
        }
