import io
import json
import base64
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from PIL import Image

from obsidian_writer import ObsidianWriter
from ai_service import AIService

app = FastAPI(title="OmniCapture Local API Hub", version="1.0.0")

# Enable CORS for browser extensions and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

writer = ObsidianWriter()
ai = AIService()

class ClipTextRequest(BaseModel):
    text: str
    comment: Optional[str] = ""
    url: Optional[str] = ""
    title: Optional[str] = ""
    tags: Optional[List[str]] = None
    use_ai: Optional[bool] = False

class ClipImageRequest(BaseModel):
    image_base64: str
    note: Optional[str] = ""
    url: Optional[str] = ""
    tags: Optional[List[str]] = None

class FullArticleRequest(BaseModel):
    title: str
    url: str
    content: str
    author: Optional[str] = ""
    tags: Optional[List[str]] = None

class QuickJotRequest(BaseModel):
    text: str
    tags: Optional[List[str]] = None

@app.get("/api/health")
def health():
    writer.reload_config()
    return {
        "status": "online",
        "service": "OmniCapture Hub",
        "vault_path": str(writer.vault_path),
        "vault_exists": writer.vault_path.exists(),
        "daily_folder": str(writer.daily_folder)
    }

@app.get("/api/config")
def get_config():
    writer.reload_config()
    return writer.config

@app.post("/api/config")
def update_config(new_config: dict):
    try:
        with open(writer.config_path, "w", encoding="utf-8") as f:
            json.dump(new_config, f, ensure_ascii=False, indent=2)
        writer.reload_config()
        return {"status": "success", "message": "配置更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clip/text")
def clip_text(req: ClipTextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="内容不能为空")

    tags = req.tags or []
    if req.use_ai:
        ai_res = ai.analyze_content(req.text)
        if ai_res.get("tags"):
            tags.extend(ai_res["tags"])
        ai_parts = []
        if ai_res.get("summary"):
            ai_parts.append(f"💡 核心要点: {ai_res['summary']}")
        if ai_res.get("key_points"):
            for pt in ai_res["key_points"]:
                ai_parts.append(f"• {pt}")
        if ai_res.get("wikilinks"):
            links_str = " | ".join([f"[[{w}]]" for w in ai_res["wikilinks"] if w])
            ai_parts.append(f"🔗 双链: {links_str}")
        if ai_parts:
            req.comment = (req.comment + "\n\n" if req.comment else "") + "\n".join(ai_parts)

    result = writer.save_web_clip(
        text=req.text,
        comment=req.comment or "",
        url=req.url or "",
        title=req.title or "",
        tags=tags
    )
    return result

@app.post("/api/clip/image")
def clip_image(req: ClipImageRequest):
    try:
        raw_b64 = req.image_base64
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",")[1]
        img_bytes = base64.b64decode(raw_b64)
        image = Image.open(io.BytesIO(img_bytes))

        result = writer.save_screenshot(
            pil_image=image,
            note=req.note or "",
            source_url=req.url or "",
            tags=req.tags or ["网页截图"]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片解析或保存失败: {str(e)}")

@app.post("/api/clip/full")
def clip_full_article(req: FullArticleRequest):
    result = writer.save_full_article(
        title=req.title,
        url=req.url,
        markdown_content=req.content,
        author=req.author or "",
        tags=req.tags or ["文章剪藏"]
    )
    return result

@app.post("/api/quick_jot")
def quick_jot(req: QuickJotRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="内容不能为空")
    result = writer.save_quick_jot(
        text=req.text,
        tags=req.tags or ["闪念"]
    )
    return result
