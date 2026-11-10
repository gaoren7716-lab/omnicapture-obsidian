import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 1. 基础画布设置 (Retina 级别 1400 x 920)
w, h = 1400, 920
img = Image.new("RGBA", (w, h), (18, 19, 24, 255))
draw = ImageDraw.Draw(img)

# 绘制 macOS Sequoia 风格的环境渐变弥散光斑 (Ambient Glow)
def draw_glow(base_img):
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_glow = ImageDraw.Draw(glow_layer)
    # 紫色与青蓝色柔光团
    d_glow.ellipse([-100, -100, 600, 500], fill=(124, 58, 237, 50))
    d_glow.ellipse([800, -150, 1500, 450], fill=(14, 165, 233, 40))
    d_glow.ellipse([300, 500, 1100, 1050], fill=(99, 102, 241, 35))
    blurred = glow_layer.filter(ImageFilter.GaussianBlur(110))
    return Image.alpha_composite(base_img, blurred)

img = draw_glow(img)
draw = ImageDraw.Draw(img)

# 字体配置
font_path_reg = "C:\\Windows\\Fonts\\msyh.ttc"
font_path_bold = "C:\\Windows\\Fonts\\msyhbd.ttc"
font_title = ImageFont.truetype(font_path_bold, 18)
font_sub = ImageFont.truetype(font_path_bold, 13)
font_text = ImageFont.truetype(font_path_reg, 13)
font_small = ImageFont.truetype(font_path_reg, 11)
font_code = ImageFont.truetype("C:\\Windows\\Fonts\\consola.ttf", 12)

def draw_squircle(d, bbox, r, fill, outline=None, width=1):
    d.rounded_rectangle(bbox, radius=r, fill=fill, outline=outline, width=width)

def draw_traffic_lights(d, x, y):
    # macOS 红黄绿三颗交通灯
    d.ellipse([x, y, x+12, y+12], fill=(255, 95, 86))
    d.ellipse([x+20, y, x+32, y+12], fill=(255, 189, 46))
    d.ellipse([x+40, y, x+52, y+12], fill=(39, 201, 63))

# ==========================================
# 顶部全局大标题
# ==========================================
draw.text((60, 35), "OmniCapture for Obsidian", font=ImageFont.truetype(font_path_bold, 28), fill=(255, 255, 255))
draw.text((60, 72), "Apple macOS Sequoia 设计语言重构方案 · 拟真毛玻璃质感 · 细致层级排版", font=font_text, fill=(160, 165, 185))

# ==========================================
# 左侧模块 1: 💡 闪念速记悬浮胶囊 (OmniJot Capsule)
# ==========================================
c1_x, c1_y, c1_w, c1_h = 60, 120, 580, 310
# 窗口阴影
draw_squircle(draw, [c1_x-2, c1_y-2, c1_x+c1_w+2, c1_y+c1_h+2], 20, fill=(35, 38, 50, 120), outline=(255, 255, 255, 35))
# 主窗口毛玻璃底色
draw_squircle(draw, [c1_x, c1_y, c1_x+c1_w, c1_y+c1_h], 18, fill=(28, 29, 36, 235), outline=(255, 255, 255, 22))

draw_traffic_lights(draw, c1_x+18, c1_y+18)
draw.text((c1_x+80, c1_y+15), "⚡ 闪念随手记 (Alt + J)", font=font_sub, fill=(230, 235, 245))

# 文本输入框
in_x, in_y, in_w, in_h = c1_x+16, c1_y+48, c1_w-32, 160
draw_squircle(draw, [in_x, in_y, in_x+in_w, in_y+in_h], 12, fill=(20, 21, 26, 240), outline=(255, 255, 255, 15))
sample_text_1 = "知识管理的核心体验是把「捕捉时的阻力降到0」。"
sample_text_2 = "看到好的想法先快速记下，由 AI 异步在后台提取核心观点、"
sample_text_3 = "打上标签并推荐关联双链，自动追加沉淀到 Obsidian 今日日记。"
draw.text((in_x+16, in_y+16), sample_text_1, font=font_text, fill=(245, 245, 250))
draw.text((in_x+16, in_y+42), sample_text_2, font=font_text, fill=(200, 205, 220))
draw.text((in_x+16, in_y+68), sample_text_3, font=font_text, fill=(200, 205, 220))

# 胶囊标签栏 (Pill Tags)
tag_y = c1_y + 222
tags = [("灵感", True), ("自媒体素材", True), ("选题", False), ("金句", False)]
cur_tag_x = in_x
draw.text((cur_tag_x, tag_y+4), "标签:", font=font_small, fill=(130, 135, 150))
cur_tag_x += 42
for tag_name, is_sel in tags:
    tw = len(tag_name) * 13 + 20
    if is_sel:
        draw_squircle(draw, [cur_tag_x, tag_y, cur_tag_x+tw, tag_y+24], 12, fill=(10, 132, 255, 220))
        draw.text((cur_tag_x+10, tag_y+3), f"#{tag_name}", font=font_small, fill=(255, 255, 255))
    else:
        draw_squircle(draw, [cur_tag_x, tag_y, cur_tag_x+tw, tag_y+24], 12, fill=(45, 47, 56, 180), outline=(255, 255, 255, 15))
        draw.text((cur_tag_x+10, tag_y+3), f"#{tag_name}", font=font_small, fill=(160, 165, 180))
    cur_tag_x += tw + 8

# 底部操作栏
draw.line([(c1_x+16, c1_y+260), (c1_x+c1_w-16, c1_y+260)], fill=(255, 255, 255, 15), width=1)
draw.text((c1_x+20, c1_y+275), "按 [Ctrl+Enter] 立即保存  ·  [Esc] 退出", font=font_small, fill=(120, 125, 140))
# 保存按钮
btn_w = 145
draw_squircle(draw, [c1_x+c1_w-btn_w-16, c1_y+268, c1_x+c1_w-16, c1_y+296], 14, fill=(52, 199, 89, 230))
draw.text((c1_x+c1_w-btn_w-3, c1_y+275), "存入 Obsidian ↵", font=font_sub, fill=(10, 30, 15))

# ==========================================
# 左侧模块 2: 📸 截图标注液态灵动岛 (Floating Island Toolbar)
# ==========================================
t_x, t_y, t_w, t_h = 60, 465, 580, 56
draw_squircle(draw, [t_x, t_y, t_x+t_w, t_y+t_h], 28, fill=(25, 26, 33, 245), outline=(255, 255, 255, 30), width=1)

# 工具项
items = [
    ("🟥 矩形", False),
    ("➡️ 箭头", False),
    ("✏️ 画笔", False),
    ("🔲 马赛克", False),
    ("📝 提字", True),  # 高亮
    ("🌐 翻译", False),
]

btn_cur_x = t_x + 14
for label, active in items:
    bw = 64
    if active:
        draw_squircle(draw, [btn_cur_x, t_y+10, btn_cur_x+bw, t_y+46], 18, fill=(10, 132, 255, 230))
        draw.text((btn_cur_x+9, t_y+18), label, font=font_small, fill=(255, 255, 255))
    else:
        draw_squircle(draw, [btn_cur_x, t_y+10, btn_cur_x+bw, t_y+46], 18, fill=(38, 40, 48, 160))
        draw.text((btn_cur_x+9, t_y+18), label, font=font_small, fill=(210, 215, 230))
    btn_cur_x += bw + 6

# 分割线
draw.line([(btn_cur_x+2, t_y+16), (btn_cur_x+2, t_y+40)], fill=(255, 255, 255, 25), width=1)
btn_cur_x += 10

# 复制按钮
draw_squircle(draw, [btn_cur_x, t_y+10, btn_cur_x+68, t_y+46], 18, fill=(10, 132, 255, 220))
draw.text((btn_cur_x+10, t_y+18), "📋 复制", font=font_sub, fill=(255, 255, 255))
btn_cur_x += 74

# 存库按钮
draw_squircle(draw, [btn_cur_x, t_y+10, btn_cur_x+74, t_y+46], 18, fill=(52, 199, 89, 230))
draw.text((btn_cur_x+12, t_y+18), "💾 存入", font=font_sub, fill=(10, 35, 15))

# 说明文本
draw.text((60, 535), "灵动岛工具栏：圆润胶囊形态 · SF 语义图标 · 选区内双击/回车默认快速复制", font=font_small, fill=(140, 145, 165))

# ==========================================
# 右侧模块 3: 🌐 截图翻译与 AI 深度管理面板 (Translation & AI Inspector)
# ==========================================
p_x, p_y, p_w, p_h = 670, 120, 670, 750
# 窗口阴影与毛玻璃背景
draw_squircle(draw, [p_x-2, p_y-2, p_x+p_w+2, p_y+p_h+2], 22, fill=(35, 38, 50, 120), outline=(255, 255, 255, 35))
draw_squircle(draw, [p_x, p_y, p_x+p_w, p_y+p_h], 20, fill=(26, 27, 34, 245), outline=(255, 255, 255, 22))

draw_traffic_lights(draw, p_x+20, p_y+20)
draw.text((p_x+85, p_y+18), "截图识别、翻译与 AI 深度管理", font=font_title, fill=(245, 245, 255))

# 卡片 1: 原文内容 (OCR)
k1_x, k1_y, k1_w, k1_h = p_x+20, p_y+60, p_w-40, 125
draw_squircle(draw, [k1_x, k1_y, k1_x+k1_w, k1_y+k1_h], 14, fill=(20, 21, 26, 230), outline=(255, 255, 255, 15))
draw.text((k1_x+14, k1_y+12), "📝 原文内容 (OCR 识别)", font=font_sub, fill=(10, 132, 255))
ocr_text = "The quick brown fox jumps over the lazy dog."
draw.text((k1_x+14, k1_y+40), ocr_text, font=font_text, fill=(230, 235, 245))
draw.text((k1_x+14, k1_y+70), "引擎: PP-OCR v4 (离线高速)  ·  已自动去除折行断词瑕疵", font=font_small, fill=(120, 125, 140))

# 卡片 2: 中文译文
k2_x, k2_y, k2_w, k2_h = p_x+20, p_y+200, p_w-40, 125
draw_squircle(draw, [k2_x, k2_y, k2_x+k2_w, k2_y+k2_h], 14, fill=(20, 21, 26, 230), outline=(255, 255, 255, 15))
draw.text((k2_x+14, k2_y+12), "🀄 中文译文 (自然语境整句翻译)", font=font_sub, fill=(52, 199, 89))
trans_text = "“敏捷的棕色狐狸跃过了那只懒狗。”"
draw.text((k2_x+14, k2_y+40), trans_text, font=ImageFont.truetype(font_path_bold, 15), fill=(245, 250, 245))
draw.text((k2_x+14, k2_y+70), "耗时: 0.18s  ·  整句语义连贯 · 消除词汇逐行割裂", font=font_small, fill=(120, 125, 140))

# 卡片 3: Apple Intelligence 风格渐变卡片 (AI 提炼与双链洞察)
k3_x, k3_y, k3_w, k3_h = p_x+20, p_y+340, p_w-40, 280
# 渐变微光外边框
draw_squircle(draw, [k3_x-1, k3_y-1, k3_x+k3_w+1, k3_y+k3_h+1], 15, fill=(124, 58, 237, 100), outline=(147, 51, 234, 180), width=1)
draw_squircle(draw, [k3_x, k3_y, k3_x+k3_w, k3_y+k3_h], 14, fill=(22, 23, 30, 240))

# 头部彩色标识
draw.text((k3_x+16, k3_y+16), "🤖 AI 核心提炼与 Obsidian 知识网络洞察", font=font_sub, fill=(192, 132, 252))

# 核心要点
draw.text((k3_x+16, k3_y+48), "💡 核心观点提炼:", font=font_sub, fill=(255, 214, 10))
draw.text((k3_x+16, k3_y+72), "该句为英文著名的全字母句（Pangram），包含了所有26个字母，", font=font_text, fill=(220, 225, 235))
draw.text((k3_x+16, k3_y+94), "兼具排版测试工具性与文案设计的代表性价值。", font=font_text, fill=(220, 225, 235))

# 价值提取
draw.text((k3_x+16, k3_y+128), "📌 价值提炼与自媒体启发:", font=font_sub, fill=(10, 132, 255))
draw.text((k3_x+16, k3_y+152), "• 适用于字体库展示、打字动效设计与键盘手感测评的标准素材", font=font_text, fill=(190, 195, 210))
draw.text((k3_x+16, k3_y+174), "• 英文排版对齐与视觉占位符的黄金测试样例文本", font=font_text, fill=(190, 195, 210))

# 双链与标签
draw.text((k3_x+16, k3_y+208), "🔗 建议关联的 Obsidian 双链主题:", font=font_sub, fill=(52, 199, 89))
links_text = "[[排版设计]]   [[自媒体素材]]   [[英语学习]]   [[字体视觉]]"
draw.text((k3_x+16, k3_y+234), links_text, font=ImageFont.truetype(font_path_bold, 13), fill=(80, 220, 130))

# 底部操作按钮
draw.line([(p_x+20, p_y+645), (p_x+p_w-20, p_y+645)], fill=(255, 255, 255, 15), width=1)
draw.text((p_x+24, p_y+665), "✓ 翻译与 AI 分析全部就绪", font=font_small, fill=(52, 199, 89))

btn_copy_all = 120
draw_squircle(draw, [p_x+p_w-btn_copy_all-190, p_y+655, p_x+p_w-190, p_y+690], 16, fill=(45, 47, 56, 200), outline=(255, 255, 255, 20))
draw.text((p_x+p_w-btn_copy_all-175, p_y+664), "📋 复制译文", font=font_sub, fill=(230, 235, 245))

btn_save_obs = 175
draw_squircle(draw, [p_x+p_w-btn_save_obs-10, p_y+655, p_x+p_w-10, p_y+690], 16, fill=(52, 199, 89, 230))
draw.text((p_x+p_w-btn_save_obs+8, p_y+664), "💾 结构化存入 Obsidian", font=font_sub, fill=(10, 35, 15))

# 保存生成的预览图
preview_out = "F:\\AI 模型\\google AI\\omnicapture\\apple_style_design_preview.png"
img.save(preview_out, "PNG")
print("Rendered successfully:", preview_out)
