import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

w, h = 1600, 960
img = Image.new("RGBA", (w, h), (24, 25, 30, 255))
draw = ImageDraw.Draw(img)

def draw_glow(base_img):
    glow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_glow = ImageDraw.Draw(glow_layer)
    d_glow.ellipse([-150, -150, 750, 600], fill=(10, 132, 255, 35))
    d_glow.ellipse([850, 300, 1700, 1100], fill=(52, 199, 89, 30))
    d_glow.ellipse([500, -100, 1200, 450], fill=(191, 90, 242, 30))
    blurred = glow_layer.filter(ImageFilter.GaussianBlur(120))
    return Image.alpha_composite(base_img, blurred)

img = draw_glow(img)
draw = ImageDraw.Draw(img)

font_path_reg = "C:\\Windows\\Fonts\\msyh.ttc"
font_path_bold = "C:\\Windows\\Fonts\\msyhbd.ttc"
font_code = "C:\\Windows\\Fonts\\consola.ttf"

font_title = ImageFont.truetype(font_path_bold, 24)
font_card_title = ImageFont.truetype(font_path_bold, 14)
font_label_bold = ImageFont.truetype(font_path_bold, 12)
font_body = ImageFont.truetype(font_path_reg, 12)
font_body_bold = ImageFont.truetype(font_path_bold, 12)
font_hint = ImageFont.truetype(font_path_reg, 11)
font_mono = ImageFont.truetype(font_code, 11)

def draw_squircle(d, bbox, r, fill, outline=None, width=1):
    d.rounded_rectangle(bbox, radius=r, fill=fill, outline=outline, width=width)

def draw_apple_traffic_lights(d, x, y):
    r = 7
    dots = [
        (x+7, y+7, (255, 95, 86), (224, 68, 62)),
        (x+31, y+7, (255, 189, 46), (222, 161, 35)),
        (x+55, y+7, (39, 201, 63), (26, 171, 41))
    ]
    for cx, cy, fill_c, outline_c in dots:
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill_c, outline=outline_c, width=1)

# 顶部标题栏
draw.text((60, 32), "OmniCapture × 乔木闪记 · 双轨自适应终极融合预演方案", font=font_title, fill=(255, 255, 255))
draw.text((60, 68), "输入时如乔木般轻盈无感（划词免复制直录 + 自动前台来源嗅探） · 沉淀时如知识图谱般结构严整（时间戳锚点 + 双链推荐 + 卡片排版）", font=font_body, fill=(185, 190, 210))

# =========================================================
# 左侧: 【输入交互态预演 (The Fluid Capture Interface)】
# =========================================================
lx, ly, lw, lh = 60, 115, 730, 790
draw_squircle(draw, [lx-1, ly-1, lx+lw+1, ly+lh+1], 24, fill=(54, 57, 72, 255), outline=(255, 255, 255, 45))
draw_squircle(draw, [lx, ly, lx+lw, ly+lh], 23, fill=(30, 32, 40, 255))

draw_squircle(draw, [lx+24, ly+16, lx+260, ly+44], 14, fill=(10, 132, 255, 40), outline=(10, 132, 255, 180))
draw.text((lx+36, ly+22), "左轨：极简心流输入面板 (用户视角)", font=font_label_bold, fill=(130, 195, 255))

# 场景 1: 【划词免复制直录 + 自动来源嗅探态 (有划词时)】
s1_x, s1_y, s1_w, s1_h = lx+24, ly+58, lw-48, 330
draw_squircle(draw, [s1_x, s1_y, s1_x+s1_w, s1_y+s1_h], 18, fill=(39, 42, 54, 255), outline=(58, 61, 78, 255))
draw_apple_traffic_lights(draw, s1_x+16, s1_y+16)
draw.text((s1_x+86, s1_y+14), "灵感闪记 · 划词直录态 (按住拖拽)", font=font_card_title, fill=(255, 255, 255))

# 前台来源自动嗅探芯片 (乔木杀手级亮点)
src_pill_w = 230
draw_squircle(draw, [s1_x+s1_w-src_pill_w-16, s1_y+12, s1_x+s1_w-16, s1_y+36], 12, fill=(46, 49, 64, 255), outline=(78, 82, 102, 255))
draw.text((s1_x+s1_w-src_pill_w-6, s1_y+16), "来源: Chrome - DeepSeek 报告...", font=font_hint, fill=(120, 185, 255))

# 自动包裹的选中文本引用区 (带柔和色块)
quote_x, quote_y, quote_w, quote_h = s1_x+16, s1_y+48, s1_w-32, 70
draw_squircle(draw, [quote_x, quote_y, quote_x+quote_w, quote_y+quote_h], 10, fill=(24, 26, 34, 255), outline=(52, 55, 70, 255))
draw_squircle(draw, [quote_x+4, quote_y+6, quote_x+7, quote_y+quote_h-6], 2, fill=(10, 132, 255))
draw.text((quote_x+16, quote_y+10), "已自动捕获屏幕选中文本：", font=font_hint, fill=(135, 140, 160))
draw.text((quote_x+16, quote_y+28), "“通过本地大模型与推理加速，个人知识库的检索摩擦力将被降低一个数量级...”", font=font_body, fill=(215, 218, 230))
draw.text((quote_x+16, quote_y+48), "来源: https://arxiv.org/abs/2412.xxxx (已自动附带出处)", font=font_hint, fill=(100, 150, 220))

# 用户即刻思考输入区 (光标直接定位此处)
in_x, in_y, in_w, in_h = s1_x+16, s1_y+126, s1_w-32, 100
draw_squircle(draw, [in_x, in_y, in_x+in_w, in_y+in_h], 10, fill=(20, 21, 28, 255), outline=(52, 55, 70, 255))
draw.text((in_x+14, in_y+12), "这个思路很启发我！自媒体内容库的构建也可以借鉴这个本地推理管道，", font=font_body, fill=(255, 255, 255))
draw.text((in_x+14, in_y+34), "把每天在各平台阅读的高价值短句聚合成统一的 Obsidian 双链资产。", font=font_body, fill=(235, 238, 248))

# 自动嗅探剪贴板附着条
draw_squircle(draw, [in_x+12, in_y+66, in_x+250, in_y+90], 12, fill=(46, 50, 68, 255), outline=(10, 132, 255, 120))
draw.text((in_x+24, in_y+71), "[附件] 已自动附带剪贴板截图 (将存入附件)", font=font_hint, fill=(120, 190, 255))

# 胶囊标签栏与底部存入
tx = s1_x+16
tags = [("#自媒体素材", 94), ("#灵感", 66), ("#深度学习", 80), ("#认知", 66)]
for i, (tag, tw) in enumerate(tags):
    bg_col = (10, 132, 255) if i == 0 else (46, 49, 64)
    fg_col = (255, 255, 255) if i == 0 else (136, 188, 255)
    draw_squircle(draw, [tx, s1_y+238, tx+tw, s1_y+264], 13, fill=bg_col)
    draw.text((tx+12, s1_y+243), tag, font=font_hint, fill=fg_col)
    tx += tw + 8

draw.text((s1_x+16, s1_y+292), "快捷键: [Ctrl+Enter / Enter] 秒存退出  |  [Esc] 退出", font=font_hint, fill=(135, 139, 158))
draw_squircle(draw, [s1_x+s1_w-150, s1_y+284, s1_x+s1_w-16, s1_y+316], 16, fill=(52, 199, 89))
draw.text((s1_x+s1_w-134, s1_y+291), "存入 Obsidian", font=font_label_bold, fill=(255, 255, 255))

# 场景 2: 【纯灵感即兴敲字态 (无划词时，超轻量 Raycast 风格)】
s2_x, s2_y, s2_w, s2_h = lx+24, ly+405, lw-48, 200
draw_squircle(draw, [s2_x, s2_y, s2_x+s2_w, s2_y+s2_h], 18, fill=(39, 42, 54, 255), outline=(58, 61, 78, 255))
draw_apple_traffic_lights(draw, s2_x+16, s2_y+16)
draw.text((s2_x+86, s2_y+14), "灵感闪记 · 极简打字态 (无划词时)", font=font_card_title, fill=(255, 255, 255))

# 单纯输入凹槽
s2_in_x, s2_in_y, s2_in_w, s2_in_h = s2_x+16, s2_y+48, s2_w-32, 95
draw_squircle(draw, [s2_in_x, s2_in_y, s2_in_x+s2_in_w, s2_in_y+s2_in_h], 12, fill=(20, 21, 28, 255), outline=(52, 55, 70, 255))
draw.text((s2_in_x+14, s2_in_y+14), "- [ ] 明天上午 10 点复盘自媒体选题矩阵并更新工作流...", font=font_body, fill=(255, 255, 255))
draw.text((s2_in_x+14, s2_in_y+38), "支持输入 `- [ ]` 自动识别为 Obsidian 待办任务！", font=font_hint, fill=(52, 199, 89))

draw.text((s2_x+16, s2_y+160), "当前前台: Windows Terminal (已自动就绪)", font=font_hint, fill=(135, 139, 158))
draw_squircle(draw, [s2_x+s2_w-150, s2_y+152, s2_x+s2_w-16, s2_y+184], 16, fill=(52, 199, 89))
draw.text((s2_x+s2_w-134, s2_y+159), "存入 Obsidian ↵", font=font_label_bold, fill=(255, 255, 255))

# 底部优势提炼
draw_squircle(draw, [lx+24, ly+620, lx+lw-24, ly+765], 14, fill=(24, 26, 34, 255), outline=(45, 48, 62, 255))
draw.text((lx+40, ly+635), "★ 输入端融合核心设计原则：", font=font_label_bold, fill=(255, 214, 10))
draw.text((lx+40, ly+660), "1. 零打断：鼠标划词后按 Alt+J，无需先 Ctrl+C，选中文本直接成为引用！", font=font_body, fill=(225, 230, 245))
draw.text((lx+40, ly+685), "2. 自动溯源：自动探测 Windows 前台活跃窗口，自动提取网页 Title 与完整 URL。", font=font_body, fill=(225, 230, 245))
draw.text((lx+40, ly+710), "3. 嗅探剪贴板：刚复制的截图自动作为附件挂载，敲回车连图带文一秒入库！", font=font_body, fill=(225, 230, 245))
draw.text((lx+40, ly+735), "4. 智能识别待办：输入框若以 `- [ ]` 开头，自动识别为可交互任务流。", font=font_body, fill=(225, 230, 245))


# =========================================================
# 右侧: 【Obsidian 今日日记落地排版 (Daily Notes Output)】
# =========================================================
rx, ry, rw, rh = 810, 115, 730, 790
draw_squircle(draw, [rx-1, ry-1, rx+rw+1, ry+rh+1], 24, fill=(54, 57, 72, 255), outline=(255, 255, 255, 45))
draw_squircle(draw, [rx, ry, rx+rw, ry+rh], 23, fill=(25, 27, 34, 255))

draw_squircle(draw, [rx+24, ry+16, rx+290, ry+44], 14, fill=(52, 199, 89, 35), outline=(52, 199, 89, 180))
draw.text((rx+36, ry+22), "右轨：Obsidian 知识库精细落库形态", font=font_label_bold, fill=(80, 230, 120))

# 模拟 Obsidian 编辑器内页
ob_x, ob_y, ob_w, ob_h = rx+24, ry+58, rw-48, 705
draw_squircle(draw, [ob_x, ob_y, ob_x+ob_w, ob_y+ob_h], 18, fill=(30, 32, 42, 255), outline=(48, 51, 68, 255))

# Obsidian 顶部标题
draw.text((ob_x+24, ob_y+20), "2026-11-11 每日日记.md", font=font_card_title, fill=(255, 255, 255))
draw.text((ob_x+24, ob_y+42), "库路径: F:/1 内容创作/5 自媒体Obsidian库/自媒体素材/每日闪记", font=font_hint, fill=(120, 125, 145))
draw.line([ob_x+24, ob_y+62, ob_x+ob_w-24, ob_y+62], fill=(48, 51, 68, 255), width=1)

# 核心亮点：精准挂载到指定锚点二级标题下方
draw.text((ob_x+24, ob_y+75), "## 每日闪念与素材捕捉 (自动锚点挂载区)", font=font_label_bold, fill=(10, 132, 255))

# 记录 1：带划词引用、时间戳、思考与出处的精致卡片
rec1_x, rec1_y, rec1_w, rec1_h = ob_x+24, ob_y+105, ob_w-48, 260
draw_squircle(draw, [rec1_x, rec1_y, rec1_x+rec1_w, rec1_y+rec1_h], 12, fill=(22, 24, 32, 255), outline=(45, 48, 64, 255))

draw.text((rec1_x+16, rec1_y+14), "### 11:28 自媒体素材与思考", font=font_label_bold, fill=(255, 255, 255))
draw_squircle(draw, [rec1_x+rec1_w-85, rec1_y+12, rec1_x+rec1_w-14, rec1_y+34], 10, fill=(46, 49, 64, 255))
draw.text((rec1_x+rec1_w-75, rec1_y+16), "11:28:45", font=font_mono, fill=(140, 180, 240))

draw.text((rec1_x+16, rec1_y+42), "• 思考心流：", font=font_label_bold, fill=(52, 199, 89))
draw.text((rec1_x+30, rec1_y+62), "这个思路很启发我！自媒体内容库的构建也可以借鉴这个本地推理管道，", font=font_body, fill=(240, 242, 252))
draw.text((rec1_x+30, rec1_y+84), "把每天在各平台阅读的高价值短句聚合成统一的 Obsidian 双链资产。", font=font_body, fill=(240, 242, 252))

# 引用 Callout
draw_squircle(draw, [rec1_x+28, rec1_y+110, rec1_x+rec1_w-28, rec1_y+180], 8, fill=(28, 30, 42, 255), outline=(10, 132, 255, 100))
draw_squircle(draw, [rec1_x+28, rec1_y+110, rec1_x+32, rec1_y+180], 2, fill=(10, 132, 255))
draw.text((rec1_x+42, rec1_y+118), "> [!quote] 选中文本摘录", font=font_label_bold, fill=(120, 185, 255))
draw.text((rec1_x+42, rec1_y+138), "> “通过本地大模型与推理加速，个人知识库的检索摩擦力将被降低一个数量级...”", font=font_body, fill=(210, 215, 230))
draw.text((rec1_x+42, rec1_y+158), "> 附带截图: ![[Pasted-Image-20261111-112845.png|450]]", font=font_hint, fill=(140, 145, 165))

# 来源追踪与分类标签
draw.text((rec1_x+16, rec1_y+195), "来源溯源: [DeepSeek 官方最新技术报告](https://arxiv.org/abs/2412.xxxx) (来自 Google Chrome)", font=font_hint, fill=(120, 185, 255))
draw.text((rec1_x+16, rec1_y+220), "标签与双链: #自媒体素材 #灵感 #深度学习  |  推荐双链: [[本地模型推理]] [[Obsidian工作流]]", font=font_hint, fill=(255, 180, 50))


# 记录 2：待办事项转化排版 (与 Tasks 插件完美联动)
rec2_x, rec2_y, rec2_w, rec2_h = ob_x+24, ob_y+380, ob_w-48, 120
draw_squircle(draw, [rec2_x, rec2_y, rec2_x+rec2_w, rec2_y+rec2_h], 12, fill=(22, 24, 32, 255), outline=(45, 48, 64, 255))

draw.text((rec2_x+16, rec2_y+14), "### 10:42 闪记待办任务", font=font_label_bold, fill=(255, 255, 255))
draw.text((rec2_x+16, rec2_y+45), "- [ ] 明天上午 10 点复盘自媒体选题矩阵并更新工作流 [截止: 2026-11-12] #待办", font=font_body_bold, fill=(255, 214, 10))
draw.text((rec2_x+16, rec2_y+72), "• 触发来源: Windows Terminal | 终端调试中突发灵感", font=font_hint, fill=(130, 135, 155))
draw.text((rec2_x+16, rec2_y+94), "• 状态: 待完成 (可在 Obsidian Tasks 视图中统一聚合)", font=font_hint, fill=(52, 199, 89))

# 记录 3：截图与 AI 深度洞察联动 (我们原有的独家护城河)
rec3_x, rec3_y, rec3_w, rec3_h = ob_x+24, ob_y+515, ob_w-48, 170
draw_squircle(draw, [rec3_x, rec3_y, rec3_x+rec3_w, rec3_y+rec3_h], 12, fill=(22, 24, 32, 255), outline=(45, 48, 64, 255))

draw.text((rec3_x+16, rec3_y+14), "### 09:15 截图翻译与 AI 洞察归档", font=font_label_bold, fill=(255, 255, 255))
draw.text((rec3_x+16, rec3_y+42), "• 截图标注: ![[Pasted-Image-20261111-091512.png|300]]", font=font_hint, fill=(140, 145, 165))
draw.text((rec3_x+16, rec3_y+68), "• 原文/译文: \"Ultra-fast neural translation pipeline\" -> “超快神经翻译流水线”", font=font_body, fill=(240, 242, 252))
draw.text((rec3_x+16, rec3_y+94), "• AI 总结: 离线推理带来毫秒级响应，显著降低认知摩擦。", font=font_hint, fill=(52, 199, 89))
draw.text((rec3_x+16, rec3_y+120), "• 关联图谱: [[知识沉淀系统]] [[认知心理学]] #认知 #精选", font=font_hint, fill=(255, 180, 50))
draw.text((rec3_x+16, rec3_y+142), "✓ 完美保持时间线顺流追加，不覆盖原有日记架构", font=font_hint, fill=(10, 132, 255))

out_path = Path("F:/AI 模型/google AI/omnicapture/qiaomu_omnicapture_fusion_preview.png")
img.save(out_path, "PNG")
print(f"Fusion preview generated at: {out_path}")
