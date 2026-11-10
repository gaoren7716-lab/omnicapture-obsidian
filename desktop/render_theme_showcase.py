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
    d_glow.ellipse([850, 300, 1700, 1100], fill=(52, 199, 89, 25))
    d_glow.ellipse([500, -100, 1200, 450], fill=(191, 90, 242, 25))
    blurred = glow_layer.filter(ImageFilter.GaussianBlur(120))
    return Image.alpha_composite(base_img, blurred)

img = draw_glow(img)
draw = ImageDraw.Draw(img)

font_path_reg = "C:\\Windows\\Fonts\\msyh.ttc"
font_path_bold = "C:\\Windows\\Fonts\\msyhbd.ttc"

font_title = ImageFont.truetype(font_path_bold, 24)
font_card_title = ImageFont.truetype(font_path_bold, 14)
font_label_bold = ImageFont.truetype(font_path_bold, 12)
font_body = ImageFont.truetype(font_path_reg, 12)
font_body_bold = ImageFont.truetype(font_path_bold, 12)
font_hint = ImageFont.truetype(font_path_reg, 11)
font_traffic_sym = ImageFont.truetype(font_path_bold, 10)

def draw_squircle(d, bbox, r, fill, outline=None, width=1):
    d.rounded_rectangle(bbox, radius=r, fill=fill, outline=outline, width=width)

def draw_apple_traffic_lights(d, x, y, with_symbols=False):
    # 饱满的 14px 苹果原生大交通灯 (带细腻描边)
    r = 7
    dots = [
        (x+7, y+7, (255, 95, 86), (224, 68, 62), "✕", (77, 0, 0)),
        (x+31, y+7, (255, 189, 46), (222, 161, 35), "—", (92, 61, 0)),
        (x+55, y+7, (39, 201, 63), (26, 171, 41), "+", (0, 77, 17))
    ]
    for cx, cy, fill_c, outline_c, sym, sym_c in dots:
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill_c, outline=outline_c, width=1)
        if with_symbols:
            d.text((cx, cy), sym, font=font_traffic_sym, fill=sym_c, anchor="mm")

# 顶部全局大标题
draw.text((60, 32), "OmniCapture for Obsidian · Apple 原生圆角与高质感调色优化", font=font_title, fill=(255, 255, 255))
draw.text((60, 68), "① 物理级 24px 大圆角窗口与全组件胶囊药丸 (Pill)   ② 14px 饱满大号交通灯按键 (悬停微符清晰可见)   ③ 沉浸温暖石墨灰与银白晨露调色", font=font_body, fill=(185, 190, 210))

# =========================================================
# 左侧: 【深色暖石墨风格 (Apple Dark Slate)】
# =========================================================
dx, dy, dw, dh = 60, 115, 710, 790
# 真实 24px 大圆角主容器
draw_squircle(draw, [dx-1, dy-1, dx+dw+1, dy+dh+1], 24, fill=(54, 57, 72, 255), outline=(255, 255, 255, 45))
draw_squircle(draw, [dx, dy, dx+dw, dy+dh], 23, fill=(30, 32, 40, 255))

# 标牌胶囊 (Pill)
draw_squircle(draw, [dx+24, dy+16, dx+160, dy+44], 14, fill=(10, 132, 255, 40), outline=(10, 132, 255, 180))
draw.text((dx+36, dy+22), "深色暖石墨模式", font=font_label_bold, fill=(130, 195, 255))

# 1. 闪念速记卡片 (Dark)
j_x, j_y, j_w, j_h = dx+24, dy+58, dw-48, 225
draw_squircle(draw, [j_x, j_y, j_x+j_w, j_y+j_h], 18, fill=(39, 42, 54, 255), outline=(58, 61, 78, 255))
# 14px 交通灯
draw_apple_traffic_lights(draw, j_x+16, j_y+16, with_symbols=True)
draw.text((j_x+86, j_y+14), "闪念速记  →  直接存入 Obsidian (支持全屏自由拖动)", font=font_card_title, fill=(255, 255, 255))

# 模式切换胶囊
draw_squircle(draw, [j_x+j_w-115, j_y+12, j_x+j_w-16, j_y+38], 13, fill=(46, 49, 64, 255), outline=(68, 72, 92, 255))
draw.text((j_x+j_w-100, j_y+17), "切换浅色模式", font=font_hint, fill=(232, 234, 245))

# 输入凹槽卡片
in_x, in_y, in_w, in_h = j_x+16, j_y+48, j_w-32, 85
draw_squircle(draw, [in_x, in_y, in_x+in_w, in_y+in_h], 12, fill=(24, 25, 32, 255), outline=(52, 55, 70, 255))
draw.text((in_x+14, in_y+14), "今天测试了深度学习 ONNX 加速与快速截图翻译工作流，", font=font_body, fill=(255, 255, 255))
draw.text((in_x+14, in_y+38), "将平时碎片时间看到的关键图文沉淀到 Obsidian 知识库中...", font=font_body, fill=(235, 238, 248))

# 药丸标签 (真正的 Pill 胶囊)
tags = [("#灵感", 66), ("#待办", 66), ("#自媒体素材", 94), ("#金句", 66), ("#认知", 66)]
tx = j_x+16
for i, (tag, tw) in enumerate(tags):
    bg_col = (10, 132, 255) if i == 0 else (46, 49, 64)
    fg_col = (255, 255, 255) if i == 0 else (136, 188, 255)
    draw_squircle(draw, [tx, j_y+145, tx+tw, j_y+171], 13, fill=bg_col)
    draw.text((tx+12, j_y+150), tag, font=font_hint, fill=fg_col)
    tx += tw + 8

# 底部按钮与提示
draw.text((j_x+16, j_y+190), "快捷键: [Ctrl+Enter] 保存  |  [Esc] 退出", font=font_hint, fill=(135, 139, 158))
# 苹果精炼翡翠绿药丸按钮
draw_squircle(draw, [j_x+j_w-146, j_y+182, j_x+j_w-16, j_y+214], 16, fill=(52, 199, 89), outline=None)
draw.text((j_x+j_w-132, j_y+189), "存入 Obsidian ↵", font=font_label_bold, fill=(255, 255, 255))

# 2. 翻译与 AI 深度管理卡片 (Dark)
t_x, t_y, t_w, t_h = dx+24, dy+298, dw-48, 470
draw_squircle(draw, [t_x, t_y, t_x+t_w, t_y+t_h], 18, fill=(39, 42, 54, 255), outline=(58, 61, 78, 255))
draw_apple_traffic_lights(draw, t_x+16, t_y+16, with_symbols=False)
draw.text((t_x+86, t_y+14), "截图识别、翻译与 AI 深度洞察 (支持全屏自由拖动)", font=font_card_title, fill=(255, 255, 255))

draw.text((t_x+16, t_y+46), "【原文内容 (OCR)】:", font=font_label_bold, fill=(130, 195, 255))
draw_squircle(draw, [t_x+16, t_y+66, t_x+t_w-16, t_y+128], 10, fill=(24, 25, 32, 255), outline=(52, 55, 70, 255))
draw.text((t_x+26, t_y+76), "\"The quick brown fox jumps over the lazy dog.\"", font=font_body, fill=(242, 244, 252))
draw.text((t_x+26, t_y+98), "Ultra-fast neural translation pipeline powered by RapidOCR ONNX.", font=font_hint, fill=(166, 172, 192))

draw.text((t_x+16, t_y+140), "【中文译文 (快速双语对照)】:", font=font_label_bold, fill=(52, 199, 89))
draw_squircle(draw, [t_x+16, t_y+160, t_x+t_w-16, t_y+222], 10, fill=(24, 25, 32, 255), outline=(52, 55, 70, 255))
draw.text((t_x+26, t_y+170), "“敏捷的棕色狐狸跃过了那只懒狗。”", font=font_body_bold, fill=(255, 255, 255))
draw.text((t_x+26, t_y+194), "基于 RapidOCR ONNX 深度学习引擎驱动的超快神经翻译流水线。", font=font_hint, fill=(185, 240, 200))

draw.text((t_x+16, t_y+234), "【AI 核心洞察与双链知识图谱】:", font=font_label_bold, fill=(255, 159, 10))
draw_squircle(draw, [t_x+16, t_y+254, t_x+t_w-16, t_y+395], 10, fill=(24, 25, 32, 255), outline=(52, 55, 70, 255))
ai_lines = [
    "• 核心要点：利用本地加速推理实现毫秒级捕获，大幅减少认知切换成本。",
    "• 价值提炼：",
    "   - 架构设计：双通道流水线，0.2秒优先返回翻译，异步生成洞察总结",
    "   - 数据存储：原生支持 Obsidian Callout 引用、wikilink 双链、分类标签",
    "• 推荐双链与标签：[[深度学习推理]]  [[Obsidian工作流]]  #自媒体素材 #认知"
]
ay = t_y + 268
for line in ai_lines:
    draw.text((t_x+26, ay), line, font=font_body, fill=(242, 244, 252))
    ay += 24

draw.text((t_x+16, t_y+422), "✓ 翻译与 AI 洞察分析全部就绪", font=font_hint, fill=(52, 199, 89))
# 底部胶囊药丸操作按钮
draw_squircle(draw, [t_x+t_w-235, t_y+414, t_x+t_w-135, t_y+446], 16, fill=(10, 132, 255))
draw.text((t_x+t_w-215, t_y+422), "复制译文", font=font_label_bold, fill=(255, 255, 255))

draw_squircle(draw, [t_x+t_w-125, t_y+414, t_x+t_w-16, t_y+446], 16, fill=(52, 199, 89))
draw.text((t_x+t_w-110, t_y+422), "结构化存入", font=font_label_bold, fill=(255, 255, 255))


# =========================================================
# 右侧: 【纯净白色系风格 (Apple Light Silver)】
# =========================================================
lx, ly, lw, lh = 830, 115, 710, 790
draw_squircle(draw, [lx-1, ly-1, lx+lw+1, ly+lh+1], 24, fill=(209, 209, 214, 255), outline=(255, 255, 255, 200))
draw_squircle(draw, [lx, ly, lx+lw, ly+lh], 23, fill=(242, 242, 247, 255))

draw_squircle(draw, [lx+24, ly+16, lx+160, ly+44], 14, fill=(0, 122, 255, 25), outline=(0, 122, 255, 120))
draw.text((lx+36, ly+22), "纯净白色模式", font=font_label_bold, fill=(0, 102, 204))

# 1. 闪念速记卡片 (Light)
lj_x, lj_y, lj_w, lj_h = lx+24, ly+58, lw-48, 225
draw_squircle(draw, [lj_x, lj_y, lj_x+lj_w, lj_y+lj_h], 18, fill=(255, 255, 255, 255), outline=(229, 229, 234, 255))
draw_apple_traffic_lights(draw, lj_x+16, lj_y+16, with_symbols=True)
draw.text((lj_x+86, lj_y+14), "闪念速记  →  直接存入 Obsidian (支持全屏自由拖动)", font=font_card_title, fill=(17, 17, 19))

draw_squircle(draw, [lj_x+lj_w-115, lj_y+12, lj_x+lj_w-16, lj_y+38], 13, fill=(235, 235, 240, 255), outline=(218, 218, 224, 255))
draw.text((lj_x+lj_w-100, lj_y+17), "切换深色模式", font=font_hint, fill=(29, 29, 31))

lin_x, lin_y, lin_w, lin_h = lj_x+16, lj_y+48, lj_w-32, 85
draw_squircle(draw, [lin_x, lin_y, lin_x+lin_w, lin_y+lin_h], 12, fill=(250, 250, 252, 255), outline=(228, 228, 234, 255))
draw.text((lin_x+14, lin_y+14), "今天测试了深度学习 ONNX 加速与快速截图翻译工作流，", font=font_body, fill=(17, 17, 19))
draw.text((lin_x+14, lin_y+38), "将平时碎片时间看到的关键图文沉淀到 Obsidian 知识库中...", font=font_body, fill=(48, 48, 52))

tx = lj_x+16
for i, (tag, tw) in enumerate(tags):
    bg_col = (0, 122, 255) if i == 0 else (235, 235, 240)
    fg_col = (255, 255, 255) if i == 0 else (0, 102, 204)
    draw_squircle(draw, [tx, lj_y+145, tx+tw, lj_y+171], 13, fill=bg_col)
    draw.text((tx+12, lj_y+150), tag, font=font_hint, fill=fg_col)
    tx += tw + 8

draw.text((lj_x+16, lj_y+190), "快捷键: [Ctrl+Enter] 保存  |  [Esc] 退出", font=font_hint, fill=(125, 125, 132))
draw_squircle(draw, [lj_x+lj_w-146, lj_y+182, lj_x+lj_w-16, lj_y+214], 16, fill=(52, 199, 89), outline=None)
draw.text((lj_x+lj_w-132, lj_y+189), "存入 Obsidian ↵", font=font_label_bold, fill=(255, 255, 255))

# 2. 翻译与 AI 深度管理卡片 (Light)
lt_x, lt_y, lt_w, lt_h = lx+24, dy+298, lw-48, 470
draw_squircle(draw, [lt_x, lt_y, lt_x+lt_w, lt_y+lt_h], 18, fill=(255, 255, 255, 255), outline=(229, 229, 234, 255))
draw_apple_traffic_lights(draw, lt_x+16, lt_y+16, with_symbols=False)
draw.text((lt_x+86, lt_y+14), "截图识别、翻译与 AI 深度洞察 (支持全屏自由拖动)", font=font_card_title, fill=(17, 17, 19))

draw.text((lt_x+16, lt_y+46), "【原文内容 (OCR)】:", font=font_label_bold, fill=(0, 122, 255))
draw_squircle(draw, [lt_x+16, lt_y+66, lt_x+lt_w-16, lt_y+128], 10, fill=(250, 250, 252, 255), outline=(228, 228, 234, 255))
draw.text((lt_x+26, lt_y+76), "\"The quick brown fox jumps over the lazy dog.\"", font=font_body, fill=(17, 17, 19))
draw.text((lt_x+26, lt_y+98), "Ultra-fast neural translation pipeline powered by RapidOCR ONNX.", font=font_hint, fill=(78, 78, 82))

draw.text((lt_x+16, lt_y+140), "【中文译文 (快速双语对照)】:", font=font_label_bold, fill=(35, 160, 65))
draw_squircle(draw, [lt_x+16, lt_y+160, lt_x+lt_w-16, lt_y+222], 10, fill=(250, 250, 252, 255), outline=(228, 228, 234, 255))
draw.text((lt_x+26, lt_y+170), "“敏捷的棕色狐狸跃过了那只懒狗。”", font=font_body_bold, fill=(17, 17, 19))
draw.text((lt_x+26, lt_y+194), "基于 RapidOCR ONNX 深度学习引擎驱动的超快神经翻译流水线。", font=font_hint, fill=(45, 120, 55))

draw.text((lt_x+16, lt_y+234), "【AI 核心洞察与双链知识图谱】:", font=font_label_bold, fill=(255, 149, 0))
draw_squircle(draw, [lt_x+16, lt_y+254, lt_x+lt_w-16, lt_y+395], 10, fill=(250, 250, 252, 255), outline=(228, 228, 234, 255))
ay = lt_y + 268
for line in ai_lines:
    draw.text((lt_x+26, ay), line, font=font_body, fill=(29, 29, 31))
    ay += 24

draw.text((lt_x+16, lt_y+422), "✓ 翻译与 AI 洞察分析全部就绪", font=font_hint, fill=(35, 160, 65))
draw_squircle(draw, [lt_x+lt_w-235, lt_y+414, lt_x+lt_w-135, lt_y+446], 16, fill=(0, 122, 255))
draw.text((lt_x+lt_w-215, lt_y+422), "复制译文", font=font_label_bold, fill=(255, 255, 255))

draw_squircle(draw, [lt_x+lt_w-125, lt_y+414, lt_x+lt_w-16, lt_y+446], 16, fill=(52, 199, 89))
draw.text((lt_x+lt_w-110, lt_y+422), "结构化存入", font=font_label_bold, fill=(255, 255, 255))

out_path = Path("F:/AI 模型/google AI/omnicapture/apple_style_dual_theme_preview.png")
img.save(out_path, "PNG")
print(f"Preview updated to: {out_path}")
