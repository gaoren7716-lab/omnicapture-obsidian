import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

w, h = 1600, 960
img = Image.new("RGBA", (w, h), (24, 25, 30, 255))
draw = ImageDraw.Draw(img)

def draw_glow(base_img):
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_glow = ImageDraw.Draw(glow_layer)
    d_glow.ellipse([-150, -150, 750, 600], fill=(10, 132, 255, 30))
    d_glow.ellipse([850, 300, 1700, 1100], fill=(48, 209, 88, 25))
    d_glow.ellipse([500, -100, 1200, 450], fill=(191, 90, 242, 25))
    blurred = glow_layer.filter(ImageFilter.GaussianBlur(120))
    return Image.alpha_composite(base_img, blurred)

img = draw_glow(img)
draw = ImageDraw.Draw(img)

font_path_reg = "C:\\Windows\\Fonts\\msyh.ttc"
font_path_bold = "C:\\Windows\\Fonts\\msyhbd.ttc"
font_emoji = "C:\\Windows\\Fonts\\seguiemj.ttf"

font_title = ImageFont.truetype(font_path_bold, 24)
font_card_title = ImageFont.truetype(font_path_bold, 14)
font_label_bold = ImageFont.truetype(font_path_bold, 12)
font_body = ImageFont.truetype(font_path_reg, 12)
font_body_bold = ImageFont.truetype(font_path_bold, 12)
font_hint = ImageFont.truetype(font_path_reg, 11)

def draw_squircle(d, bbox, r, fill, outline=None, width=1):
    d.rounded_rectangle(bbox, radius=r, fill=fill, outline=outline, width=width)

def draw_traffic_lights(d, x, y):
    d.ellipse([x, y, x+11, y+11], fill=(255, 95, 86))
    d.ellipse([x+18, y, x+29, y+11], fill=(255, 189, 46))
    d.ellipse([x+36, y, x+47, y+11], fill=(39, 201, 63))

# 顶部标题栏
draw.text((60, 35), "OmniCapture for Obsidian · 苹果双色系 UI 与可拖拽交互", font=font_title, fill=(255, 255, 255))
draw.text((60, 72), "① 深色石墨 (Dark) 与 白色系 (Light) 双风格一键无缝切换   ② 全弹窗支持鼠标按住标题栏自由平移拖拽   ③ 极高文字清晰度", font=font_body, fill=(180, 185, 205))

# =========================================================
# 左侧: 【深色石墨风格 (Dark Mode)】
# =========================================================
dx, dy, dw, dh = 60, 120, 710, 780
draw_squircle(draw, [dx-1, dy-1, dx+dw+1, dy+dh+1], 18, fill=(50, 52, 64, 255), outline=(255, 255, 255, 40))
draw_squircle(draw, [dx, dy, dx+dw, dy+dh], 17, fill=(26, 27, 34, 255))

draw_squircle(draw, [dx+20, dy+16, dx+160, dy+42], 12, fill=(10, 132, 255, 40), outline=(10, 132, 255, 160))
draw.text((dx+32, dy+21), "深色石墨模式", font=font_label_bold, fill=(120, 185, 255))

# 1. 闪念速记卡片 (Dark)
j_x, j_y, j_w, j_h = dx+20, dy+56, dw-40, 220
draw_squircle(draw, [j_x, j_y, j_x+j_w, j_y+j_h], 14, fill=(34, 36, 45, 255), outline=(54, 56, 71, 255))
draw_traffic_lights(draw, j_x+16, j_y+16)
draw.text((j_x+74, j_y+13), "闪念速记  →  直接存入 Obsidian (支持全屏自由拖动)", font=font_card_title, fill=(255, 255, 255))
draw_squircle(draw, [j_x+j_w-105, j_y+12, j_x+j_w-15, j_y+36], 10, fill=(46, 49, 62, 255), outline=(70, 73, 90, 255))
draw.text((j_x+j_w-95, j_y+16), "切换浅色模式", font=font_hint, fill=(226, 229, 242))

in_x, in_y, in_w, in_h = j_x+16, j_y+46, j_w-32, 85
draw_squircle(draw, [in_x, in_y, in_x+in_w, in_y+in_h], 8, fill=(20, 21, 26, 255), outline=(46, 48, 60, 255))
draw.text((in_x+12, in_y+12), "今天测试了深度学习 ONNX 加速与快速截图翻译工作流，", font=font_body, fill=(255, 255, 255))
draw.text((in_x+12, in_y+36), "将平时碎片时间看到的关键图文沉淀到 Obsidian 知识库中...", font=font_body, fill=(225, 228, 240))

tags = ["#灵感", "#待办", "#自媒体素材", "#金句", "#认知"]
tx = j_x+16
for i, tag in enumerate(tags):
    bg_col = (10, 132, 255) if i == 0 else (42, 44, 56)
    fg_col = (255, 255, 255) if i == 0 else (127, 183, 255)
    tw = 68 if len(tag) > 3 else 52
    draw_squircle(draw, [tx, j_y+142, tx+tw, j_y+168], 12, fill=bg_col)
    draw.text((tx+10, j_y+147), tag, font=font_hint, fill=fg_col)
    tx += tw + 8

draw.text((j_x+16, j_y+186), "快捷键: [Ctrl+Enter] 保存  |  [Esc] 退出", font=font_hint, fill=(130, 134, 154))
draw_squircle(draw, [j_x+j_w-140, j_y+180, j_x+j_w-16, j_y+208], 12, fill=(48, 209, 88), outline=None)
draw.text((j_x+j_w-126, j_y+185), "存入 Obsidian", font=font_label_bold, fill=(14, 28, 18))

# 2. 翻译与 AI 深度管理卡片 (Dark)
t_x, t_y, t_w, t_h = dx+20, dy+290, dw-40, 465
draw_squircle(draw, [t_x, t_y, t_x+t_w, t_y+t_h], 14, fill=(34, 36, 45, 255), outline=(54, 56, 71, 255))
draw_traffic_lights(draw, t_x+16, t_y+16)
draw.text((t_x+74, t_y+13), "截图识别、翻译与 AI 深度洞察 (支持全屏自由拖动)", font=font_card_title, fill=(255, 255, 255))

draw.text((t_x+16, t_y+46), "【原文内容 (OCR)】:", font=font_label_bold, fill=(120, 185, 255))
draw_squircle(draw, [t_x+16, t_y+66, t_x+t_w-16, t_y+128], 8, fill=(20, 21, 26, 255), outline=(46, 48, 60, 255))
draw.text((t_x+26, t_y+76), "\"The quick brown fox jumps over the lazy dog.\"", font=font_body, fill=(240, 242, 250))
draw.text((t_x+26, t_y+98), "Ultra-fast neural translation pipeline powered by RapidOCR ONNX.", font=font_hint, fill=(160, 165, 185))

draw.text((t_x+16, t_y+140), "【中文译文 (快速双语对照)】:", font=font_label_bold, fill=(48, 209, 88))
draw_squircle(draw, [t_x+16, t_y+160, t_x+t_w-16, t_y+222], 8, fill=(20, 21, 26, 255), outline=(46, 48, 60, 255))
draw.text((t_x+26, t_y+170), "“敏捷的棕色狐狸跃过了那只懒狗。”", font=font_body_bold, fill=(255, 255, 255))
draw.text((t_x+26, t_y+194), "基于 RapidOCR ONNX 深度学习引擎驱动的超快神经翻译流水线。", font=font_hint, fill=(180, 235, 195))

draw.text((t_x+16, t_y+234), "【AI 核心洞察与双链知识图谱】:", font=font_label_bold, fill=(255, 159, 10))
draw_squircle(draw, [t_x+16, t_y+254, t_x+t_w-16, t_y+390], 8, fill=(20, 21, 26, 255), outline=(46, 48, 60, 255))
ai_lines = [
    "• 核心要点：利用本地加速推理实现毫秒级捕获，大幅减少认知切换成本。",
    "• 价值提炼：",
    "   - 架构设计：双通道流水线，0.2秒优先返回翻译，异步生成洞察总结",
    "   - 数据存储：原生支持 Obsidian Callout 引用、wikilink 双链、分类标签",
    "• 推荐双链与标签：[[深度学习推理]]  [[Obsidian工作流]]  #自媒体素材 #认知"
]
ay = t_y + 266
for line in ai_lines:
    draw.text((t_x+26, ay), line, font=font_body, fill=(240, 242, 250))
    ay += 24

draw.text((t_x+16, t_y+415), "✓ 翻译与 AI 洞察分析全部就绪", font=font_hint, fill=(48, 209, 88))
draw_squircle(draw, [t_x+t_w-220, t_y+408, t_x+t_w-120, t_y+438], 10, fill=(10, 132, 255))
draw.text((t_x+t_w-208, t_y+414), "复制译文", font=font_label_bold, fill=(255, 255, 255))
draw_squircle(draw, [t_x+t_w-110, t_y+408, t_x+t_w-16, t_y+438], 10, fill=(48, 209, 88))
draw.text((t_x+t_w-98, t_y+414), "结构化存入", font=font_label_bold, fill=(14, 28, 18))


# =========================================================
# 右侧: 【白色系 / 银白晨露风格 (Light Mode)】
# =========================================================
lx, ly, lw, lh = 830, 120, 710, 780
draw_squircle(draw, [lx-1, ly-1, lx+lw+1, ly+lh+1], 18, fill=(209, 209, 214, 255), outline=(255, 255, 255, 180))
draw_squircle(draw, [lx, ly, lx+lw, ly+lh], 17, fill=(242, 242, 247, 255))

draw_squircle(draw, [lx+20, ly+16, lx+160, ly+42], 12, fill=(0, 122, 255, 25), outline=(0, 122, 255, 120))
draw.text((lx+32, ly+21), "纯净白色模式", font=font_label_bold, fill=(0, 102, 204))

# 1. 闪念速记卡片 (Light)
lj_x, lj_y, lj_w, lj_h = lx+20, ly+56, lw-40, 220
draw_squircle(draw, [lj_x, lj_y, lj_x+lj_w, lj_y+lj_h], 14, fill=(255, 255, 255, 255), outline=(229, 229, 234, 255))
draw_traffic_lights(draw, lj_x+16, lj_y+16)
draw.text((lj_x+74, lj_y+13), "闪念速记  →  直接存入 Obsidian (支持全屏自由拖动)", font=font_card_title, fill=(17, 17, 19))
draw_squircle(draw, [lj_x+lj_w-105, lj_y+12, lj_x+lj_w-15, lj_y+36], 10, fill=(235, 235, 240, 255), outline=(215, 215, 220, 255))
draw.text((lj_x+lj_w-95, lj_y+16), "切换深色模式", font=font_hint, fill=(28, 28, 30))

lin_x, lin_y, lin_w, lin_h = lj_x+16, lj_y+46, lj_w-32, 85
draw_squircle(draw, [lin_x, lin_y, lin_x+lin_w, lin_y+lin_h], 8, fill=(250, 250, 252, 255), outline=(225, 225, 230, 255))
draw.text((lin_x+12, lin_y+12), "今天测试了深度学习 ONNX 加速与快速截图翻译工作流，", font=font_body, fill=(17, 17, 19))
draw.text((lin_x+12, lin_y+36), "将平时碎片时间看到的关键图文沉淀到 Obsidian 知识库中...", font=font_body, fill=(45, 45, 48))

tx = lj_x+16
for i, tag in enumerate(tags):
    bg_col = (0, 122, 255) if i == 0 else (235, 235, 240)
    fg_col = (255, 255, 255) if i == 0 else (0, 102, 204)
    tw = 68 if len(tag) > 3 else 52
    draw_squircle(draw, [tx, lj_y+142, tx+tw, lj_y+168], 12, fill=bg_col)
    draw.text((tx+10, lj_y+147), tag, font=font_hint, fill=fg_col)
    tx += tw + 8

draw.text((lj_x+16, lj_y+186), "快捷键: [Ctrl+Enter] 保存  |  [Esc] 退出", font=font_hint, fill=(120, 120, 128))
draw_squircle(draw, [lj_x+lj_w-140, lj_y+180, lj_x+lj_w-16, lj_y+208], 12, fill=(52, 199, 89), outline=None)
draw.text((lj_x+lj_w-126, lj_y+185), "存入 Obsidian", font=font_label_bold, fill=(255, 255, 255))

# 2. 翻译与 AI 深度管理卡片 (Light)
lt_x, lt_y, lt_w, lt_h = lx+20, ly+290, lw-40, 465
draw_squircle(draw, [lt_x, lt_y, lt_x+lt_w, lt_y+lt_h], 14, fill=(255, 255, 255, 255), outline=(229, 229, 234, 255))
draw_traffic_lights(draw, lt_x+16, lt_y+16)
draw.text((lt_x+74, lt_y+13), "截图识别、翻译与 AI 深度洞察 (支持全屏自由拖动)", font=font_card_title, fill=(17, 17, 19))

draw.text((lt_x+16, lt_y+46), "【原文内容 (OCR)】:", font=font_label_bold, fill=(0, 122, 255))
draw_squircle(draw, [lt_x+16, lt_y+66, lt_x+lt_w-16, lt_y+128], 8, fill=(250, 250, 252, 255), outline=(225, 225, 230, 255))
draw.text((lt_x+26, lt_y+76), "\"The quick brown fox jumps over the lazy dog.\"", font=font_body, fill=(17, 17, 19))
draw.text((lt_x+26, lt_y+98), "Ultra-fast neural translation pipeline powered by RapidOCR ONNX.", font=font_hint, fill=(72, 72, 74))

draw.text((lt_x+16, lt_y+140), "【中文译文 (快速双语对照)】:", font=font_label_bold, fill=(35, 160, 65))
draw_squircle(draw, [lt_x+16, lt_y+160, lt_x+lt_w-16, lt_y+222], 8, fill=(250, 250, 252, 255), outline=(225, 225, 230, 255))
draw.text((lt_x+26, lt_y+170), "“敏捷的棕色狐狸跃过了那只懒狗。”", font=font_body_bold, fill=(17, 17, 19))
draw.text((lt_x+26, lt_y+194), "基于 RapidOCR ONNX 深度学习引擎驱动的超快神经翻译流水线。", font=font_hint, fill=(45, 120, 55))

draw.text((lt_x+16, lt_y+234), "【AI 核心洞察与双链知识图谱】:", font=font_label_bold, fill=(255, 149, 0))
draw_squircle(draw, [lt_x+16, lt_y+254, lt_x+lt_w-16, lt_y+390], 8, fill=(250, 250, 252, 255), outline=(225, 225, 230, 255))
ay = lt_y + 266
for line in ai_lines:
    draw.text((lt_x+26, ay), line, font=font_body, fill=(29, 29, 31))
    ay += 24

draw.text((lt_x+16, lt_y+415), "✓ 翻译与 AI 洞察分析全部就绪", font=font_hint, fill=(35, 160, 65))
draw_squircle(draw, [lt_x+lt_w-220, lt_y+408, lt_x+lt_w-120, lt_y+438], 10, fill=(0, 122, 255))
draw.text((lt_x+lt_w-208, lt_y+414), "复制译文", font=font_label_bold, fill=(255, 255, 255))
draw_squircle(draw, [lt_x+lt_w-110, lt_y+408, lt_x+lt_w-16, lt_y+438], 10, fill=(52, 199, 89))
draw.text((lt_x+lt_w-98, lt_y+414), "结构化存入", font=font_label_bold, fill=(255, 255, 255))

out_path = Path("F:/AI 模型/google AI/omnicapture/apple_style_dual_theme_preview.png")
img.save(out_path, "PNG")
print(f"Preview saved to: {out_path}")
