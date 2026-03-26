#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parents[2]
OUTPUT_PNG = ROOT / "courseware_review_assistant_poster.png"
OUTPUT_PDF = PROJECT_ROOT / "output" / "pdf" / "courseware_review_assistant_poster.pdf"
REVIEW_DIR = ROOT / "review"

ASSETS = {
    "ui": PROJECT_ROOT / "tmp" / "current_ui_rewrite_loaded.png",
    "desktop_mock": PROJECT_ROOT / "designs" / "exports" / "r0GqG.png",
    "mobile_mock": PROJECT_ROOT / "designs" / "exports" / "Z2wV6.png",
}

W, H = 4961, 7016  # A2 portrait at ~300 DPI
M = 180
GUTTER = 70

BG = "#F6F8FB"
PANEL = "#FFFFFF"
PANEL_SOFT = "#EEF3F7"
INK = "#102131"
SUB = "#5E6D7C"
LINE = "#D8E0E8"
BLUE = "#21425F"
BLUE_2 = "#325979"
BLUE_SOFT = "#E8F0F7"
COPPER = "#9A6C48"
COPPER_SOFT = "#F4ECE5"
GREEN_SOFT = "#E8F1EB"
WHITE = "#FFFFFF"

TITLE_FONT = "/System/Library/Fonts/Supplemental/Songti.ttc"
BODY_FONT = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc"
HEAVY_FONT = "/System/Library/Fonts/STHeiti Medium.ttc"


@dataclass
class Fonts:
    title_xl: ImageFont.FreeTypeFont
    title_l: ImageFont.FreeTypeFont
    title_m: ImageFont.FreeTypeFont
    body_l: ImageFont.FreeTypeFont
    body_m: ImageFont.FreeTypeFont
    body_s: ImageFont.FreeTypeFont
    caption: ImageFont.FreeTypeFont


def load_fonts() -> Fonts:
    return Fonts(
        title_xl=ImageFont.truetype(TITLE_FONT, 126, index=0),
        title_l=ImageFont.truetype(TITLE_FONT, 76, index=0),
        title_m=ImageFont.truetype(HEAVY_FONT, 48, index=0),
        body_l=ImageFont.truetype(BODY_FONT, 42, index=1),
        body_m=ImageFont.truetype(BODY_FONT, 32, index=1),
        body_s=ImageFont.truetype(BODY_FONT, 26, index=1),
        caption=ImageFont.truetype(BODY_FONT, 20, index=1),
    )


def rounded(draw: ImageDraw.ImageDraw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def text_width(font: ImageFont.FreeTypeFont, text: str) -> float:
    return font.getlength(text)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        current = ""
        for ch in paragraph:
            trial = current + ch
            if current and text_width(font, trial) > max_width:
                lines.append(current.rstrip())
                current = ch
            else:
                current = trial
        if current:
            lines.append(current.rstrip())
    return lines


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    line_gap: int,
) -> int:
    lines = wrap_text(text, font, w)
    cursor = y
    for line in lines:
        draw.text((x, cursor), line, font=font, fill=fill)
        cursor += font.size + line_gap
    return cursor


def draw_bullets(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    items: list[str],
    font: ImageFont.FreeTypeFont,
    fill: str,
    bullet_fill: str,
    gap_y: int = 18,
) -> int:
    cursor = y
    bullet_size = 14
    for item in items:
        lines = wrap_text(item, font, w - 42)
        draw.ellipse((x, cursor + 12, x + bullet_size, cursor + 12 + bullet_size), fill=bullet_fill)
        for idx, line in enumerate(lines):
            draw.text((x + 28, cursor + idx * (font.size + 8)), line, font=font, fill=fill)
        cursor += len(lines) * (font.size + 8) + gap_y
    return cursor


def paste_contain(canvas: Image.Image, image_path: Path, box: tuple[int, int, int, int], radius: int | None = None):
    x, y, w, h = box
    img = Image.open(image_path).convert("RGB")
    img.thumbnail((w, h))
    px = x + (w - img.width) // 2
    py = y + (h - img.height) // 2
    if radius:
        mask = Image.new("L", (img.width, img.height), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, img.width, img.height), radius=radius, fill=255)
        canvas.paste(img, (px, py), mask)
    else:
        canvas.paste(img, (px, py))


def draw_tag(draw, x, y, text, font, fill, text_fill):
    tw = int(text_width(font, text)) + 70
    rounded(draw, (x, y, x + tw, y + 62), 24, fill, outline=fill)
    bbox = draw.textbbox((0, 0), text, font=font)
    th = bbox[3] - bbox[1]
    draw.text((x + (tw - (bbox[2] - bbox[0])) / 2, y + (62 - th) / 2 - 2), text, font=font, fill=text_fill)
    return tw


def build_poster() -> None:
    fonts = load_fonts()
    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)

    # Top header
    rounded(draw, (M, M, W - M, 1220), 54, BLUE, outline=BLUE)
    draw.rectangle((M, 970, W - M, 1010), fill=BLUE_2)
    draw.text((M + 110, M + 90), "课件智能知识点复习助手", font=fonts.title_xl, fill=WHITE)
    draw.text((M + 120, M + 255), "Courseware Review Desk", font=fonts.body_m, fill="#D4E0EB")
    draw_text_block(
        draw,
        M + 120,
        M + 375,
        1850,
        "上传课程 PPT / PDF 后，自动生成学习笔记、Learning Board、研究对话区与测试环境，帮助学生形成从理解到练习再到检验的完整复习闭环。",
        fonts.body_l,
        "#E8EEF4",
        12,
    )
    tag_x = M + 120
    tag_y = 1040
    for fill, txt_fill, label in [
        (WHITE, BLUE, "PPTX / PDF"),
        (COPPER, WHITE, "智能笔记"),
        ("#3E5F7B", WHITE, "对话问答"),
        ("#567165", WHITE, "计算题测试"),
    ]:
        used = draw_tag(draw, tag_x, tag_y, label, fonts.body_s, fill, txt_fill)
        tag_x += used + 26

    rounded(draw, (W - 1780, M + 80, W - M - 40, 1080), 42, WHITE, outline="#D0DBE5", width=3)
    paste_contain(canvas, ASSETS["desktop_mock"], (W - 1720, M + 130, 1500, 860), radius=28)
    draw.text((W - 770, 1100), "项目主工作台示意", font=fonts.caption, fill="#D4E0EB")

    # Background + objective
    top_y = 1320
    left_col = M
    right_col = W // 2 + 20
    col_w = (W - M * 2 - GUTTER) // 2

    rounded(draw, (left_col, top_y, left_col + col_w, top_y + 980), 42, PANEL, outline=LINE, width=2)
    draw.text((left_col + 70, top_y + 60), "项目背景与目标", font=fonts.title_l, fill=INK)
    draw_text_block(
        draw,
        left_col + 70,
        top_y + 170,
        col_w - 140,
        "传统课件复习经常存在四个痛点：内容长、重点散、缺少互动，以及练习准备成本高。本项目的目标，是把静态课件升级成可复习、可追问、可测试的学习工作台。",
        fonts.body_m,
        SUB,
        10,
    )
    draw_bullets(
        draw,
        left_col + 78,
        top_y + 430,
        col_w - 156,
        [
            "输入端统一支持 PPTX 与文本型 PDF，降低使用门槛。",
            "输出端统一提供学习笔记、任务台、测试环境与导出结果。",
            "把“看课件”升级为“理解、提问、练习、检验”的完整流程。",
        ],
        fonts.body_m,
        INK,
        COPPER,
        24,
    )

    rounded(draw, (right_col, top_y, right_col + col_w, top_y + 980), 42, PANEL_SOFT, outline=LINE, width=2)
    draw.text((right_col + 70, top_y + 60), "系统工作流", font=fonts.title_l, fill=INK)
    workflow = [
        "上传课件",
        "文本解析与章节切分",
        "学习笔记生成",
        "Learning Board",
        "研究对话区",
        "测试环境",
        "导出复习记录",
    ]
    node_y = top_y + 190
    node_w = col_w - 160
    for idx, node in enumerate(workflow):
        node_h = 76
        rounded(draw, (right_col + 80, node_y, right_col + 80 + node_w, node_y + node_h), 24, WHITE, outline=BLUE, width=3)
        bbox = draw.textbbox((0, 0), node, font=fonts.body_m)
        draw.text((right_col + 80 + (node_w - (bbox[2] - bbox[0])) / 2, node_y + 18), node, font=fonts.body_m, fill=INK)
        node_y += 118
        if idx < len(workflow) - 1:
            draw.line((right_col + col_w // 2, node_y - 42, right_col + col_w // 2, node_y - 10), fill=COPPER, width=8)
            draw.polygon(
                [
                    (right_col + col_w // 2, node_y - 2),
                    (right_col + col_w // 2 - 18, node_y - 28),
                    (right_col + col_w // 2 + 18, node_y - 28),
                ],
                fill=COPPER,
            )

    # Feature highlight strip
    strip_y = 2390
    rounded(draw, (M, strip_y, W - M, strip_y + 740), 42, PANEL, outline=LINE, width=2)
    draw.text((M + 70, strip_y + 50), "核心功能亮点", font=fonts.title_l, fill=INK)
    cards = [
        ("课件解析与章节组织", ["支持 PPTX / PDF", "目录去噪与标题识别", "自动章节聚合"]),
        ("智能学习笔记生成", ["章节概述与详细讲解", "关键知识点", "公式与例题整理"]),
        ("研究对话区", ["围绕课件 + 笔记提问", "多轮上下文承接", "练习题继续追问"]),
        ("学习任务与测试环境", ["摘要 / 概念 / 练习 / 路径", "选择题 / 填空题 / 计算题", "交卷后显示解析"]),
    ]
    card_w = (W - M * 2 - 70 * 3 - 140) // 4
    card_x = M + 70
    for title, items in cards:
        rounded(draw, (card_x, strip_y + 160, card_x + card_w, strip_y + 610), 34, BLUE_SOFT, outline=LINE, width=2)
        draw.text((card_x + 32, strip_y + 190), title, font=fonts.title_m, fill=BLUE)
        draw_bullets(draw, card_x + 34, strip_y + 270, card_w - 68, items, fonts.body_s, INK, BLUE, 16)
        card_x += card_w + 70

    # Technical innovation + product highlights
    innovation_y = 3230
    rounded(draw, (M, innovation_y, left_col + col_w, innovation_y + 1170), 42, PANEL_SOFT, outline=LINE, width=2)
    draw.text((M + 70, innovation_y + 55), "技术创新点", font=fonts.title_l, fill=INK)
    draw_bullets(
        draw,
        M + 78,
        innovation_y + 190,
        col_w - 156,
        [
            "PDF 去噪与真实标题识别，解决目录噪声导致的章节切分失败。",
            "数学课件支持公式与例题的结构化整理，不再只是摘要。",
            "测试区支持计算题，不再局限于概念问答。",
            "研究对话区具备问题类型识别与多轮上下文承接能力。",
        ],
        fonts.body_m,
        INK,
        COPPER,
        26,
    )

    rounded(draw, (right_col, innovation_y, right_col + col_w, innovation_y + 1170), 42, PANEL, outline=LINE, width=2)
    draw.text((right_col + 70, innovation_y + 55), "项目亮点浓缩区", font=fonts.title_l, fill=INK)
    draw_text_block(
        draw,
        right_col + 70,
        innovation_y + 180,
        col_w - 140,
        "海报不展示真实实验结果，而是聚焦项目本身的能力闭环与设计亮点。",
        fonts.body_m,
        SUB,
        10,
    )
    tag_specs = [
        ("支持课件解析", BLUE_SOFT, BLUE),
        ("支持公式整理", COPPER_SOFT, COPPER),
        ("支持多轮问答", GREEN_SOFT, BLUE),
        ("支持测试导出", PANEL_SOFT, BLUE_2),
        ("支持计算题", COPPER_SOFT, COPPER),
        ("支持本地运行", BLUE_SOFT, BLUE),
    ]
    tx, ty = right_col + 70, innovation_y + 350
    for label, fill, text_fill in tag_specs:
        width = draw_tag(draw, tx, ty, label, fonts.body_s, fill, text_fill)
        tx += width + 24
        if tx > right_col + col_w - 460:
            tx = right_col + 70
            ty += 92
    rounded(draw, (right_col + 70, innovation_y + 720, right_col + col_w - 70, innovation_y + 1040), 32, BLUE, outline=BLUE)
    draw.text((right_col + 104, innovation_y + 760), "一句话价值总结", font=fonts.title_m, fill=WHITE)
    draw_text_block(
        draw,
        right_col + 104,
        innovation_y + 840,
        col_w - 208,
        "把静态课件升级成结构化复习工具，让学生能够围绕“课件 + 笔记”持续理解、练习与检验。",
        fonts.body_m,
        "#E5EDF4",
        10,
    )

    # UI showcase
    ui_y = 4540
    rounded(draw, (M, ui_y, W - M, ui_y + 1500), 42, PANEL, outline=LINE, width=2)
    draw.text((M + 70, ui_y + 55), "界面展示区", font=fonts.title_l, fill=INK)
    paste_contain(canvas, ASSETS["ui"], (M + 70, ui_y + 170, 2520, 1220), radius=30)
    rounded(draw, (M + 2700, ui_y + 170, W - M - 70, ui_y + 770), 34, BLUE_SOFT, outline=LINE, width=2)
    draw.text((M + 2760, ui_y + 220), "主工作台三栏结构", font=fonts.title_m, fill=BLUE)
    draw_bullets(
        draw,
        M + 2768,
        ui_y + 330,
        W - M - 2900,
        [
            "左侧资料区：上传入口、课件列表、学习笔记摘要。",
            "中间研究对话区：围绕课件与笔记的统一提问入口。",
            "右侧学习任务台 / 测试区：任务推进与交卷后解析。",
        ],
        fonts.body_m,
        INK,
        BLUE,
        28,
    )
    rounded(draw, (M + 2700, ui_y + 860, W - M - 70, ui_y + 1390), 34, COPPER_SOFT, outline=LINE, width=2)
    draw.text((M + 2760, ui_y + 900), "视觉与交互取向", font=fonts.title_m, fill=COPPER)
    draw_bullets(
        draw,
        M + 2768,
        ui_y + 1010,
        W - M - 2900,
        [
            "三栏工作台，突出对话主舞台。",
            "浅色研究室风格，适合课程答辩展示。",
            "资料、对话、任务三块协作完成复习闭环。",
        ],
        fonts.body_m,
        INK,
        COPPER,
        28,
    )

    # Footer summary
    footer_y = 6200
    rounded(draw, (M, footer_y, W - M, H - M), 42, BLUE, outline=BLUE)
    draw.text((M + 80, footer_y + 70), "总结与展望", font=fonts.title_l, fill=WHITE)
    draw_text_block(
        draw,
        M + 82,
        footer_y + 190,
        2350,
        "课件智能知识点复习助手把传统静态课件转化为一个结构化、可追问、可测试、可导出的学习工作台，更适合课程复习与项目答辩展示。",
        fonts.body_l,
        "#E7EEF5",
        12,
    )
    draw_bullets(
        draw,
        W // 2 + 160,
        footer_y + 170,
        1700,
        [
            "OCR：支持扫描版 PDF 与图片型课件。",
            "公式规范化：让数学表达更接近标准排版。",
            "更稳的数学推导与自动评测能力。",
        ],
        fonts.body_m,
        WHITE,
        "#F0C39F",
        28,
    )

    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR = OUTPUT_PDF.parent
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT_PNG, format="PNG")
    canvas.convert("RGB").save(OUTPUT_PDF, "PDF", resolution=300.0)
    print(f"PNG written to {OUTPUT_PNG}")
    print(f"PDF written to {OUTPUT_PDF}")


if __name__ == "__main__":
    build_poster()
