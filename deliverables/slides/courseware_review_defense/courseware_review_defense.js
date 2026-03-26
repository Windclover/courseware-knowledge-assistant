const path = require("path");
const PptxGenJS = require("pptxgenjs");
const { imageSizingContain } = require("./pptxgenjs_helpers/image");
const { safeOuterShadow } = require("./pptxgenjs_helpers/util");
const {
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require("./pptxgenjs_helpers/layout");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "OpenAI Codex";
pptx.company = "Courseware Review Desk";
pptx.subject = "课件智能知识点复习助手答辩讲解";
pptx.title = "课件智能知识点复习助手";
pptx.lang = "zh-CN";
pptx.theme = {
  headFontFace: "Source Han Serif SC",
  bodyFontFace: "PingFang SC",
  lang: "zh-CN",
};

const W = 13.333;
const H = 7.5;
const PAGE = "#F5F7FB";
const PAGE_ALT = "#EAF0F6";
const INK = "#122131";
const MUTED = "#5F6F81";
const LINE = "#D1D9E3";
const BLUE = "#23435E";
const BLUE_SOFT = "#EAF1F8";
const BLUE_DEEP = "#17334A";
const COPPER = "#8F6748";
const COPPER_SOFT = "#F6EDE6";
const GREEN_SOFT = "#E8F2ED";
const RED_SOFT = "#F7ECE8";
const WHITE = "#FFFFFF";
const NIGHT = "#10273A";
const NIGHT_SOFT = "#163850";
const SCREEN = path.join(__dirname, "assets/current_ui_rewrite_loaded.png");
const DESKTOP = path.join(__dirname, "assets/r0GqG.png");
const MOBILE = path.join(__dirname, "assets/Z2wV6.png");

function addSlideBase(title, kicker, pageNo) {
  const slide = pptx.addSlide();
  slide.background = { color: PAGE };
  slide.addShape(pptx._shapeType.rect, {
    x: 0,
    y: 0,
    w: W,
    h: H,
    line: { color: PAGE },
    fill: { color: PAGE },
  });
  slide.addShape(pptx._shapeType.rect, {
    x: 0.68,
    y: 0.44,
    w: 11.96,
    h: 0.02,
    line: { color: BLUE },
    fill: { color: BLUE },
  });
  slide.addText(`0${pageNo}`.slice(-2), {
    x: 11.1,
    y: 0.34,
    w: 1.1,
    h: 0.62,
    fontFace: "Source Han Serif SC",
    fontSize: 30,
    bold: true,
    color: "D9E2EC",
    align: "right",
    margin: 0,
  });
  slide.addText(kicker, {
    x: 0.7,
    y: 0.16,
    w: 4.0,
    h: 0.2,
    fontFace: "PingFang SC",
    fontSize: 9,
    color: COPPER,
    bold: true,
    charSpace: 1.2,
    margin: 0,
  });
  slide.addText(title, {
    x: 0.7,
    y: 0.56,
    w: 9.2,
    h: 0.5,
    fontFace: "Source Han Serif SC",
    fontSize: 25,
    bold: true,
    color: INK,
    margin: 0,
  });
  slide.addText("课件智能知识点复习助手 / Courseware Review Desk", {
    x: 0.72,
    y: 7.06,
    w: 5.8,
    h: 0.18,
    fontFace: "PingFang SC",
    fontSize: 8.5,
    color: MUTED,
    margin: 0,
  });
  return slide;
}

function addRoundCard(slide, x, y, w, h, fill, title, bodyLines, options = {}) {
  const bodyFontSize = options.bodySize || 10.5;
  const bodyBoxH = options.bodyBoxH || (bodyFontSize <= 9 ? 0.18 : 0.24);
  slide.addShape(pptx._shapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.12,
    fill: { color: fill },
    line: { color: options.lineColor || LINE, pt: 1 },
    shadow: safeOuterShadow("8EA0B2", 0.12, 45, 2, 1),
  });
  slide.addText(title, {
    x: x + 0.24,
    y: y + 0.2,
    w: w - 0.48,
    h: 0.24,
    fontFace: "Source Han Serif SC",
    fontSize: options.titleSize || 14,
    bold: true,
    color: options.titleColor || INK,
    margin: 0,
  });
  if (!bodyLines || bodyLines.length === 0) {
    return;
  }
  let cursorY = y + 0.62;
  bodyLines.forEach((line) => {
    slide.addShape(pptx._shapeType.ellipse, {
      x: x + 0.28,
      y: cursorY + 0.06,
      w: 0.08,
      h: 0.08,
      line: { color: options.dotColor || BLUE, pt: 0.5 },
      fill: { color: options.dotColor || BLUE },
    });
    slide.addText(line, {
      x: x + 0.42,
      y: cursorY,
      w: w - 0.66,
      h: bodyBoxH,
      fontFace: "PingFang SC",
      fontSize: bodyFontSize,
      color: MUTED,
      margin: 0,
    });
    cursorY += options.rowGap || 0.34;
  });
}

function addPill(slide, x, y, w, label, fill = BLUE_SOFT, color = BLUE) {
  slide.addShape(pptx._shapeType.roundRect, {
    x,
    y,
    w,
    h: 0.32,
    rectRadius: 0.12,
    fill: { color: fill },
    line: { color: fill, pt: 1 },
  });
  slide.addText(label, {
    x,
    y: y + 0.04,
    w,
    h: 0.2,
    fontFace: "PingFang SC",
    fontSize: 9,
    bold: true,
    color,
    align: "center",
    margin: 0,
  });
}

function addMetricCard(slide, x, y, w, label, value, note, fill = WHITE) {
  slide.addShape(pptx._shapeType.roundRect, {
    x,
    y,
    w,
    h: 1.45,
    rectRadius: 0.12,
    fill: { color: fill },
    line: { color: LINE, pt: 1 },
    shadow: safeOuterShadow("8EA0B2", 0.12, 45, 2, 1),
  });
  slide.addShape(pptx._shapeType.rect, {
    x: x + 0.2,
    y: y + 0.18,
    w: 0.48,
    h: 0.03,
    line: { color: BLUE, pt: 0 },
    fill: { color: BLUE },
  });
  slide.addText(label, {
    x: x + 0.22,
    y: y + 0.28,
    w: w - 0.44,
    h: 0.18,
    fontFace: "PingFang SC",
    fontSize: 9.2,
    color: MUTED,
    margin: 0,
  });
  slide.addText(value, {
    x: x + 0.22,
    y: y + 0.48,
    w: w - 0.44,
    h: 0.46,
    fontFace: "Source Han Serif SC",
    fontSize: 27,
    bold: true,
    color: BLUE,
    margin: 0,
  });
  slide.addText(note, {
    x: x + 0.22,
    y: y + 1.02,
    w: w - 0.44,
    h: 0.22,
    fontFace: "PingFang SC",
    fontSize: 9.5,
    color: MUTED,
    margin: 0,
  });
}

function addFlowNode(slide, x, y, w, label, fill = WHITE, color = BLUE) {
  slide.addShape(pptx._shapeType.roundRect, {
    x,
    y,
    w,
    h: 0.78,
    rectRadius: 0.12,
    fill: { color: fill },
    line: { color, pt: 1.2 },
  });
  slide.addText(label, {
    x: x + 0.08,
    y: y + 0.18,
    w: w - 0.16,
    h: 0.36,
    fontFace: "PingFang SC",
    fontSize: 10.5,
    bold: true,
    color: INK,
    align: "center",
    valign: "mid",
    margin: 0,
  });
}

function addArrowText(slide, x, y, text = "→") {
  slide.addText(text, {
    x,
    y,
    w: 0.18,
    h: 0.18,
    fontFace: "PingFang SC",
    fontSize: 14,
    bold: true,
    color: COPPER,
    align: "center",
    margin: 0,
  });
}

function finalizeSlide(slide) {
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function buildCover() {
  const slide = pptx.addSlide();
  slide.background = { color: PAGE };
  slide.addShape(pptx._shapeType.rect, {
    x: 0,
    y: 0,
    w: W,
    h: H,
    line: { color: PAGE },
    fill: { color: PAGE },
  });
  slide.addShape(pptx._shapeType.rect, {
    x: 0,
    y: 0,
    w: 6.15,
    h: H,
    line: { color: NIGHT, pt: 0 },
    fill: { color: NIGHT },
  });
  slide.addShape(pptx._shapeType.rect, {
    x: 0.78,
    y: 0.9,
    w: 0.04,
    h: 5.66,
    line: { color: COPPER, pt: 0 },
    fill: { color: COPPER },
  });
  slide.addText("Courseware Review Desk", {
    x: 1.02,
    y: 0.78,
    w: 2.9,
    h: 0.2,
    fontFace: "PingFang SC",
    fontSize: 9,
    color: "D8E4EF",
    bold: true,
    charSpace: 1.4,
    margin: 0,
  });
  slide.addText("课件智能知识点复习助手", {
    x: 1.02,
    y: 1.18,
    w: 4.7,
    h: 1.2,
    fontFace: "Source Han Serif SC",
    fontSize: 28,
    bold: true,
    color: WHITE,
    margin: 0,
  });
  slide.addText("课程大作业 / 项目答辩讲解", {
    x: 1.04,
    y: 2.48,
    w: 3.5,
    h: 0.26,
    fontFace: "PingFang SC",
    fontSize: 11.5,
    color: COPPER,
    bold: true,
    margin: 0,
  });
  slide.addText(
    "上传课件后自动生成学习笔记、学习任务台与测试环境，\n围绕“课件 + 笔记”开展结构化复习与多轮问答。",
    {
      x: 1.04,
      y: 3.0,
      w: 4.3,
      h: 1.02,
      fontFace: "PingFang SC",
      fontSize: 12.4,
      color: "D7E1EB",
      breakLine: false,
      margin: 0,
    }
  );
  addPill(slide, 1.02, 4.5, 1.34, "React + Vite", "284862", WHITE);
  addPill(slide, 2.48, 4.5, 1.38, "FastAPI", "1B3950", WHITE);
  addPill(slide, 3.98, 4.5, 1.64, "OpenAI API", COPPER, WHITE);
  addPill(slide, 1.02, 4.94, 1.2, "SQLite", "385046", WHITE);
  addPill(slide, 2.36, 4.94, 1.72, "PPTX / PDF", "23394D", WHITE);
  addPill(slide, 4.22, 4.94, 1.2, "答辩版", "6E4D37", WHITE);

  slide.addShape(pptx._shapeType.roundRect, {
    x: 6.62,
    y: 0.72,
    w: 5.94,
    h: 6.02,
    rectRadius: 0.14,
    fill: { color: WHITE },
    line: { color: LINE, pt: 1 },
    shadow: safeOuterShadow("8396A9", 0.16, 45, 3, 1),
  });
  slide.addImage({
    path: SCREEN,
    ...imageSizingContain(SCREEN, 6.9, 0.96, 5.42, 5.56),
  });
  slide.addText("课程答辩展示稿", {
    x: 9.32,
    y: 6.78,
    w: 2.7,
    h: 0.2,
    fontFace: "PingFang SC",
    fontSize: 9.4,
    color: MUTED,
    align: "right",
    margin: 0,
  });
}

function buildDeck() {
  buildCover();

  let slide = addSlideBase("项目背景与痛点", "01 / 背景问题", 2);
  addRoundCard(slide, 0.82, 1.4, 2.85, 1.56, BLUE_SOFT, "课件内容长", [
    "PPT/PDF 页面多，难以快速抓住重点",
    "数学类课件常夹杂公式与例题",
  ]);
  addRoundCard(slide, 3.98, 1.4, 2.85, 1.56, WHITE, "复习重点散", [
    "章节、公式、例题不在同一复习视图",
    "学生需要手动整理笔记",
  ]);
  addRoundCard(slide, 7.14, 1.4, 2.85, 1.56, WHITE, "互动性不足", [
    "传统课件缺少即时追问与解释",
    "复习过程中难承接上下文",
  ]);
  addRoundCard(slide, 10.3, 1.4, 2.2, 1.56, COPPER_SOFT, "练习成本高", [
    "题目、答案、解析需要老师单独准备",
  ], { rowGap: 0.42 });
  slide.addShape(pptx._shapeType.roundRect, {
    x: 0.82,
    y: 3.52,
    w: 11.68,
    h: 2.54,
    rectRadius: 0.12,
    fill: { color: WHITE },
    line: { color: LINE, pt: 1 },
    shadow: safeOuterShadow("8EA0B2", 0.1, 45, 2, 1),
  });
  slide.addText("项目目标", {
    x: 1.08,
    y: 3.78,
    w: 1.3,
    h: 0.22,
    fontFace: "Source Han Serif SC",
    fontSize: 15,
    bold: true,
    color: BLUE,
    margin: 0,
  });
  slide.addText(
    "把传统 PPT / PDF 课件转化成一个可复习、可追问、可测试、可导出的学习工作台。",
    {
      x: 1.08,
      y: 4.18,
      w: 5.25,
      h: 0.5,
      fontFace: "PingFang SC",
      fontSize: 14,
      color: INK,
      bold: true,
      margin: 0,
    }
  );
  addRoundCard(slide, 7.0, 3.88, 1.55, 1.48, BLUE_SOFT, "可复习", ["章节讲解", "知识点整理"]);
  addRoundCard(slide, 8.76, 3.88, 1.55, 1.48, GREEN_SOFT, "可追问", ["统一对话", "上下文承接"]);
  addRoundCard(slide, 10.52, 3.88, 1.55, 1.48, COPPER_SOFT, "可测试", ["选择/填空/计算", "交卷后解析"]);
  slide.addText("最终还能统一导出复习记录、任务完成情况与测试结果。", {
    x: 7.58,
    y: 5.58,
    w: 4.22,
    h: 0.26,
    fontFace: "PingFang SC",
    fontSize: 10,
    color: MUTED,
    bold: true,
    margin: 0,
  });
  finalizeSlide(slide);

  slide = addSlideBase("项目目标与核心价值", "02 / 产品定位", 3);
  addFlowNode(slide, 0.92, 2.08, 1.55, "课程 PPT / PDF", WHITE, BLUE);
  addArrowText(slide, 2.62, 2.22);
  addFlowNode(slide, 2.98, 2.08, 1.58, "课件解析", BLUE_SOFT, BLUE);
  addArrowText(slide, 4.72, 2.22);
  addFlowNode(slide, 5.08, 2.08, 1.58, "学习笔记", WHITE, BLUE);
  addArrowText(slide, 6.82, 2.22);
  addFlowNode(slide, 7.18, 2.08, 1.7, "Learning Board", GREEN_SOFT, BLUE);
  addArrowText(slide, 9.04, 2.22);
  addFlowNode(slide, 9.4, 2.08, 1.55, "测试环境", WHITE, BLUE);
  addArrowText(slide, 11.1, 2.22);
  addFlowNode(slide, 11.42, 2.08, 1.1, "导出", COPPER_SOFT, COPPER);
  addRoundCard(slide, 1.02, 4.0, 3.72, 1.95, WHITE, "输入端价值", [
    "兼容课件常见格式，降低老师与学生的使用门槛",
    "不要求额外整理素材即可直接复习",
  ], { rowGap: 0.42 });
  addRoundCard(slide, 4.98, 4.0, 3.3, 1.95, BLUE_SOFT, "过程端价值", [
    "把“看课件”升级为“理解 + 追问 + 练习”",
    "让公式、章节、例题进入同一工作流",
  ], { rowGap: 0.42 });
  addRoundCard(slide, 8.56, 4.0, 3.0, 1.95, WHITE, "结果端价值", [
    "形成结构化复习路径",
    "适合课程复习、答辩准备和课后自测",
  ], { rowGap: 0.42 });
  finalizeSlide(slide);

  slide = addSlideBase("整体功能总览", "03 / 功能版图", 4);
  addRoundCard(slide, 0.9, 1.55, 2.8, 2.0, BLUE_SOFT, "课件解析", [
    "提取 PPT / PDF 文本",
    "按章节聚合与组织内容",
    "数学课件支持公式候选抽取",
  ], { rowGap: 0.38 });
  addRoundCard(slide, 3.95, 1.55, 2.8, 2.0, WHITE, "笔记生成", [
    "章节概述与详细讲解",
    "关键知识点",
    "核心公式、例题与步骤",
  ], { rowGap: 0.38 });
  addRoundCard(slide, 7.0, 1.55, 2.8, 2.0, WHITE, "对话问答", [
    "围绕课件 + 笔记统一提问",
    "支持多轮上下文承接",
    "公式解释与练习题追问",
  ], { rowGap: 0.38 });
  addRoundCard(slide, 10.05, 1.55, 2.35, 2.0, COPPER_SOFT, "测试与导出", [
    "选择题 / 填空题 / 计算题",
    "交卷后显示答案与解析",
    "导出复习记录",
  ], { rowGap: 0.38 });
  slide.addShape(pptx._shapeType.roundRect, {
    x: 0.9,
    y: 4.1,
    w: 11.5,
    h: 1.7,
    rectRadius: 0.12,
    fill: { color: PAGE_ALT },
    line: { color: PAGE_ALT },
  });
  slide.addText("一句话概括：上传一份课件，系统自动完成“解析 - 笔记 - 任务 - 对话 - 测试 - 导出”的完整学习闭环。", {
    x: 1.15,
    y: 4.44,
    w: 10.95,
    h: 0.5,
    fontFace: "Source Han Serif SC",
    fontSize: 18,
    bold: true,
    color: BLUE_DEEP,
    align: "center",
    margin: 0,
  });
  finalizeSlide(slide);

  slide = addSlideBase("系统工作流", "04 / 主流程", 5);
  const nodes = [
    ["上传课件", 0.9],
    ["文本解析与去噪", 2.62],
    ["章节切分", 4.46],
    ["学习笔记生成", 6.08],
    ["Learning Board", 7.98],
    ["测试环境", 9.92],
    ["导出复习记录", 11.5],
  ];
  nodes.forEach(([label, x], index) => {
    const widths = [1.4, 1.55, 1.3, 1.62, 1.55, 1.35, 1.16];
    addFlowNode(
      slide,
      Number(x),
      2.2,
      widths[index],
      label,
      index % 2 === 0 ? WHITE : BLUE_SOFT,
      index === nodes.length - 1 ? COPPER : BLUE
    );
    if (index < nodes.length - 1) {
      if (index !== nodes.length - 2) {
        addArrowText(slide, Number(x) + widths[index] + 0.08, 2.34);
      }
    }
  });
  addRoundCard(slide, 1.0, 4.15, 3.6, 1.7, WHITE, "用户侧体验", [
    "从上传开始进入统一工作台",
    "不需要在多个页面之间来回切换",
  ], { rowGap: 0.42 });
  addRoundCard(slide, 4.86, 4.15, 3.65, 1.7, BLUE_SOFT, "系统侧处理", [
    "解析层负责提取文本与清洗噪声",
    "生成层负责笔记、任务与测试题",
  ], { rowGap: 0.42 });
  addRoundCard(slide, 8.78, 4.15, 3.2, 1.7, WHITE, "结果侧输出", [
    "可追问、可测试、可导出",
    "形成课程答辩可展示的学习闭环",
  ], { rowGap: 0.42 });
  finalizeSlide(slide);

  slide = addSlideBase("界面展示：主工作台", "05 / 前端界面", 6);
  slide.addShape(pptx._shapeType.roundRect, {
    x: 0.82,
    y: 1.28,
    w: 11.72,
    h: 4.34,
    rectRadius: 0.14,
    fill: { color: WHITE },
    line: { color: LINE, pt: 1 },
    shadow: safeOuterShadow("8EA0B2", 0.18, 45, 3, 1),
  });
  slide.addImage({ path: SCREEN, ...imageSizingContain(SCREEN, 1.02, 1.42, 11.32, 3.98) });
  addRoundCard(slide, 0.98, 5.74, 3.22, 1.06, BLUE_SOFT, "左侧资料区", [
    "上传入口",
    "课件列表与笔记摘要",
  ], { bodySize: 8.7, rowGap: 0.2, titleSize: 11.5 });
  addRoundCard(slide, 4.96, 5.74, 3.36, 1.06, WHITE, "中间研究对话区", [
    "围绕课件 + 笔记提问",
    "多轮承接是主舞台",
  ], { bodySize: 8.7, rowGap: 0.2, titleSize: 11.5 });
  addRoundCard(slide, 8.98, 5.74, 3.12, 1.06, COPPER_SOFT, "右侧任务台 / 测试区", [
    "完成任务后进入测试环境",
  ], { bodySize: 8.7, rowGap: 0.2, titleSize: 11.5, dotColor: COPPER, titleColor: COPPER });
  finalizeSlide(slide);

  slide = addSlideBase("核心功能一：课件解析与章节组织", "06 / 解析链路", 7);
  addRoundCard(slide, 0.92, 1.45, 4.32, 4.9, WHITE, "解析层做什么", [
    "支持 .pptx 与文本型 .pdf",
    "PDF 先提取行文本，再识别噪声页眉/页脚",
    "根据页面标题做章节切分，而不是简单按页堆叠",
    "数学类课件会同步抽取公式候选与例题候选",
  ], { rowGap: 0.48, bodySize: 10.4 });
  addFlowNode(slide, 5.72, 1.78, 1.45, "24 页 PDF", WHITE, BLUE);
  addArrowText(slide, 7.28, 1.93);
  addFlowNode(slide, 7.62, 1.78, 1.62, "目录去噪", BLUE_SOFT, BLUE);
  addArrowText(slide, 9.38, 1.93);
  addFlowNode(slide, 9.72, 1.78, 1.75, "标题识别", WHITE, BLUE);
  addArrowText(slide, 11.63, 1.93);
  addFlowNode(slide, 11.92, 1.78, 0.84, "11 段", COPPER_SOFT, COPPER);
  addMetricCard(slide, 5.78, 3.08, 2.0, "真实案例", "罚函数法.pdf", "24 页数学课件");
  addMetricCard(slide, 7.98, 3.08, 1.6, "修复前", "1", "整个 PDF 只聚成 1 section", RED_SOFT);
  addMetricCard(slide, 9.8, 3.08, 1.6, "修复后", "11", "能拆出多个主要章节", GREEN_SOFT);
  slide.addImage({ path: DESKTOP, ...imageSizingContain(DESKTOP, 5.78, 4.9, 5.9, 1.5) });
  finalizeSlide(slide);

  slide = addSlideBase("核心功能二：智能学习笔记生成", "07 / 笔记生成", 8);
  addRoundCard(slide, 0.95, 1.42, 3.7, 5.2, BLUE_SOFT, "一份真正可复习的笔记", [
    "章节概述",
    "详细讲解",
    "关键知识点",
    "核心公式",
    "例题与计算步骤",
    "来源页码",
  ], { rowGap: 0.55, bodySize: 11.2 });
  slide.addShape(pptx._shapeType.roundRect, {
    x: 5.0,
    y: 1.46,
    w: 6.86,
    h: 2.0,
    rectRadius: 0.12,
    fill: { color: WHITE },
    line: { color: LINE, pt: 1 },
  });
  slide.addText("核心公式示例", {
    x: 5.28,
    y: 1.72,
    w: 1.5,
    h: 0.22,
    fontFace: "Source Han Serif SC",
    fontSize: 15,
    bold: true,
    color: BLUE,
    margin: 0,
  });
  slide.addText("P_E(x, σ) = f(x) + (1/(2σ)) * Σ c_i(x)^2", {
    x: 5.28,
    y: 2.12,
    w: 6.1,
    h: 0.28,
    fontFace: "Courier New",
    fontSize: 16,
    color: INK,
    margin: 0,
  });
  slide.addText("解释：把原目标函数与惩罚项组合，惩罚违反约束的解。", {
    x: 5.28,
    y: 2.58,
    w: 6.0,
    h: 0.24,
    fontFace: "PingFang SC",
    fontSize: 10.5,
    color: MUTED,
    margin: 0,
  });
  slide.addShape(pptx._shapeType.roundRect, {
    x: 5.0,
    y: 3.82,
    w: 6.86,
    h: 2.35,
    rectRadius: 0.12,
    fill: { color: WHITE },
    line: { color: LINE, pt: 1 },
  });
  slide.addText("例题与计算步骤示例", {
    x: 5.28,
    y: 4.08,
    w: 2.1,
    h: 0.22,
    fontFace: "Source Han Serif SC",
    fontSize: 15,
    bold: true,
    color: BLUE,
    margin: 0,
  });
  const exampleLines = [
    "题目：min x1^2 + x2^2, s.t. x1 - x2 + 1 = 0",
    "1. 写出罚函数",
    "2. 求极值点表达式",
    "3. 说明 σ 增大时的逼近趋势",
  ];
  exampleLines.forEach((line, index) => {
    slide.addText(line, {
      x: 5.28,
      y: 4.46 + index * 0.34,
      w: 6.0,
      h: 0.22,
      fontFace: index === 0 ? "Courier New" : "PingFang SC",
      fontSize: index === 0 ? 11 : 10.3,
      color: index === 0 ? INK : MUTED,
      margin: 0,
    });
  });
  finalizeSlide(slide);

  slide = addSlideBase("核心功能三：研究对话区", "08 / 问答能力", 9);
  addRoundCard(slide, 0.92, 1.45, 4.1, 4.88, WHITE, "对话不只是“复述课件”", [
    "问题类型识别：summary / concepts / formula / exercise / follow_up",
    "全局与局部检索分流：整份课件问题不再被单页带偏",
    "低信息输入澄清：如 11、123 不再胡答",
    "练习题与追问承接：上一轮题目可以继续求解",
  ], { rowGap: 0.5, bodySize: 10.2 });
  slide.addShape(pptx._shapeType.roundRect, {
    x: 5.36,
    y: 1.5,
    w: 6.1,
    h: 1.42,
    rectRadius: 0.12,
    fill: { color: BLUE_SOFT },
    line: { color: LINE, pt: 1 },
  });
  slide.addText("用户：用数学公式帮我讲一下", {
    x: 5.64,
    y: 1.76,
    w: 5.4,
    h: 0.2,
    fontFace: "PingFang SC",
    fontSize: 10.5,
    color: BLUE_DEEP,
    bold: true,
    margin: 0,
  });
  slide.addText(
    "系统：P_E(x, σ) = f(x) + (1/(2σ)) * Σ c_i(x)^2\n改用纯文本公式表达，避免 JSON 转义导致的乱码。",
    {
      x: 5.64,
      y: 2.12,
      w: 5.4,
      h: 0.56,
      fontFace: "PingFang SC",
      fontSize: 10.2,
      color: INK,
      margin: 0,
    }
  );
  addFlowNode(slide, 5.48, 3.38, 1.42, "问题识别", WHITE, BLUE);
  addArrowText(slide, 7.02, 3.53);
  addFlowNode(slide, 7.34, 3.38, 1.58, "检索分流", BLUE_SOFT, BLUE);
  addArrowText(slide, 9.08, 3.53);
  addFlowNode(slide, 9.4, 3.38, 1.85, "回答骨架", WHITE, BLUE);
  addRoundCard(slide, 5.38, 4.45, 6.12, 1.7, COPPER_SOFT, "对话质量增强结果", [
    "真实回归中：公式问答更稳定，多轮练习题可继续求解",
    "“11 / 123” 这类输入会提示澄清，不再输出假答案",
  ], { rowGap: 0.42, bodySize: 10.2, dotColor: COPPER, titleColor: COPPER });
  finalizeSlide(slide);

  slide = addSlideBase("核心功能四：学习任务与测试环境", "09 / 任务与测试", 10);
  addRoundCard(slide, 0.92, 1.42, 3.4, 4.98, BLUE_SOFT, "Learning Board 四块内容", [
    "摘要：形成章节总览",
    "概念：提炼核心术语与定义",
    "练习：给出任务式练习入口",
    "复习路径：组织建议的学习顺序",
  ], { rowGap: 0.6, bodySize: 11.0 });
  slide.addShape(pptx._shapeType.roundRect, {
    x: 4.7,
    y: 1.5,
    w: 6.7,
    h: 4.9,
    rectRadius: 0.12,
    fill: { color: WHITE },
    line: { color: LINE, pt: 1 },
    shadow: safeOuterShadow("8EA0B2", 0.12, 45, 2, 1),
  });
  addPill(slide, 4.98, 1.78, 1.1, "选择题");
  addPill(slide, 6.2, 1.78, 1.1, "填空题", GREEN_SOFT, BLUE);
  addPill(slide, 7.42, 1.78, 1.1, "计算题", COPPER_SOFT, COPPER);
  slide.addText("测试区能力", {
    x: 8.72,
    y: 1.82,
    w: 1.3,
    h: 0.18,
    fontFace: "Source Han Serif SC",
    fontSize: 13,
    color: BLUE,
    bold: true,
    margin: 0,
  });
  addRoundCard(slide, 4.98, 2.28, 2.98, 1.45, WHITE, "题目前", [
    "只展示题目，不提前泄露答案",
    "支持用户填写与切换题型",
  ], { rowGap: 0.38, bodySize: 9.8 });
  addRoundCard(slide, 8.14, 2.28, 2.98, 1.45, WHITE, "交卷后", [
    "显示正确 / 错误",
    "展示标准答案、解析与参考步骤",
  ], { rowGap: 0.38, bodySize: 9.8 });
  addRoundCard(slide, 5.62, 4.2, 4.88, 1.45, PAGE_ALT, "导出结果", [
    "统一导出学习笔记、任务完成情况、测试题、用户答案、正确答案与解析",
  ], { rowGap: 0.42, bodySize: 9.8 });
  finalizeSlide(slide);

  slide = addSlideBase("技术架构", "10 / 技术实现", 11);
  addFlowNode(slide, 0.96, 2.0, 1.5, "React\nVite", WHITE, BLUE);
  addArrowText(slide, 2.56, 2.2);
  addFlowNode(slide, 2.9, 2.0, 1.8, "FastAPI", BLUE_SOFT, BLUE);
  addArrowText(slide, 4.84, 2.2);
  addFlowNode(slide, 5.2, 2.0, 1.7, "解析层\nPPTX / PDF", WHITE, BLUE);
  addArrowText(slide, 7.02, 2.2);
  addFlowNode(slide, 7.38, 2.0, 1.9, "模型层\nResponses API", COPPER_SOFT, COPPER);
  addArrowText(slide, 9.42, 2.2);
  addFlowNode(slide, 9.76, 2.0, 1.55, "SQLite", WHITE, BLUE);
  addArrowText(slide, 11.45, 2.2);
  addFlowNode(slide, 11.78, 2.0, 0.7, "MD", GREEN_SOFT, BLUE);
  addRoundCard(slide, 0.98, 4.08, 5.75, 1.92, WHITE, "关键技术组合", [
    "前端：React + TypeScript + Vite",
    "后端：FastAPI + SQLite",
    "文本提取：python-pptx、PyMuPDF",
    "模型调用：OpenAI compatible Responses API（默认 gpt-5.4，medium）",
  ], { rowGap: 0.3, bodySize: 9.4 });
  slide.addShape(pptx._shapeType.roundRect, {
    x: 7.0,
    y: 4.05,
    w: 5.4,
    h: 2.02,
    rectRadius: 0.12,
    fill: { color: BLUE_SOFT },
    line: { color: LINE, pt: 1 },
  });
  slide.addText("主要 API", {
    x: 7.28,
    y: 4.28,
    w: 1.4,
    h: 0.2,
    fontFace: "Source Han Serif SC",
    fontSize: 14,
    bold: true,
    color: BLUE,
    margin: 0,
  });
  [
    "POST /api/documents/upload",
    "GET /api/documents/{id}",
    "POST /api/documents/{id}/chat",
    "POST /api/documents/{id}/assessment",
    "GET /api/documents/{id}/markdown",
  ].forEach((line, index) => {
    slide.addText(line, {
      x: 7.3,
      y: 4.7 + index * 0.24,
      w: 4.6,
      h: 0.16,
      fontFace: "Courier New",
      fontSize: 9.8,
      color: INK,
      margin: 0,
    });
  });
  finalizeSlide(slide);

  slide = addSlideBase("关键实现难点与解决方案", "11 / 关键问题", 12);
  slide.addShape(pptx._shapeType.roundRect, {
    x: 0.92,
    y: 1.42,
    w: 11.5,
    h: 5.52,
    rectRadius: 0.12,
    fill: { color: WHITE },
    line: { color: LINE, pt: 1 },
  });
  slide.addText("实现难点", {
    x: 1.18,
    y: 1.7,
    w: 2.0,
    h: 0.2,
    fontFace: "Source Han Serif SC",
    fontSize: 14,
    bold: true,
    color: BLUE,
    margin: 0,
  });
  slide.addText("对应解决方案", {
    x: 6.32,
    y: 1.7,
    w: 2.4,
    h: 0.2,
    fontFace: "Source Han Serif SC",
    fontSize: 14,
    bold: true,
    color: BLUE,
    margin: 0,
  });
  const challenges = [
    ["PDF 目录噪声导致章节切分失败", "按页做行文本去噪，过滤高频页眉页脚，再识别真实短标题"],
    ["Markdown 笔记过短、缺公式", "章节新增公式说明与例题步骤，Markdown 重构为“讲解 + 公式 + 例题”结构"],
    ["测试题全是概念题", "assessment 增加 calculation 类型，并优先从公式与例题组织计算题"],
    ["对话容易退化成泛化总结", "问题类型识别 + 全局/局部检索分流 + 练习题承接逻辑"],
  ];
  challenges.forEach(([left, right], index) => {
    const y = 2.15 + index * 1.02;
    slide.addShape(pptx._shapeType.rect, {
      x: 1.14,
      y,
      w: 4.72,
      h: 0.72,
      fill: { color: index % 2 === 0 ? BLUE_SOFT : PAGE_ALT },
      line: { color: LINE, pt: 0.8 },
    });
    slide.addText(left, {
      x: 1.34,
      y: y + 0.18,
      w: 4.34,
      h: 0.32,
      fontFace: "PingFang SC",
      fontSize: 11,
      color: INK,
      bold: true,
      margin: 0,
    });
    slide.addShape(pptx._shapeType.rect, {
      x: 6.16,
      y,
      w: 5.92,
      h: 0.72,
      fill: { color: WHITE },
      line: { color: LINE, pt: 0.8 },
    });
    slide.addText(right, {
      x: 6.34,
      y: y + 0.12,
      w: 5.58,
      h: 0.42,
      fontFace: "PingFang SC",
      fontSize: 10.2,
      color: MUTED,
      margin: 0,
    });
  });
  finalizeSlide(slide);

  slide = addSlideBase("项目成果与当前效果", "12 / 结果验证", 13);
  addMetricCard(slide, 0.94, 1.52, 2.55, "数学课件章节切分", "11", "罚函数法.pdf 可拆成 11 个 section", GREEN_SOFT);
  addMetricCard(slide, 3.7, 1.52, 2.55, "学习笔记长度", "11025", "Markdown 长度显著提升", BLUE_SOFT);
  addMetricCard(slide, 6.46, 1.52, 2.55, "计算题数量", "2", "assessment 已稳定生成计算题", COPPER_SOFT);
  addMetricCard(slide, 9.22, 1.52, 2.55, "对话回归", "9 轮", "公式问答、练习追问已增强", WHITE);
  slide.addShape(pptx._shapeType.roundRect, {
    x: 0.94,
    y: 3.7,
    w: 11.06,
    h: 2.36,
    rectRadius: 0.12,
    fill: { color: WHITE },
    line: { color: LINE, pt: 1 },
  });
  slide.addText("结果总结", {
    x: 1.2,
    y: 3.98,
    w: 1.3,
    h: 0.2,
    fontFace: "Source Han Serif SC",
    fontSize: 15,
    bold: true,
    color: BLUE,
    margin: 0,
  });
  const resultRows = [
    ["笔记质量", "从“几百字摘要”提升为“含讲解、公式、例题”的复习笔记"],
    ["测试效果", "从概念题为主，提升为选择题 / 填空题 / 计算题并存"],
    ["对话体验", "从泛化复述，提升为可承接上下文、可解释公式、可继续解题"],
  ];
  resultRows.forEach(([k, v], index) => {
    slide.addText(`${k}：${v}`, {
      x: 1.2,
      y: 4.4 + index * 0.42,
      w: 10.2,
      h: 0.24,
      fontFace: "PingFang SC",
      fontSize: 11,
      color: index === 0 ? INK : MUTED,
      bold: index === 0,
      margin: 0,
    });
  });
  finalizeSlide(slide);

  slide = addSlideBase("总结与展望", "13 / 收尾", 14);
  addRoundCard(slide, 0.92, 1.42, 5.3, 3.18, WHITE, "项目总结", [
    "完成了一条从课件上传到笔记、任务、测试、导出的完整学习闭环",
    "针对数学课件补强了章节切分、公式说明、例题整理与计算题生成",
    "前后端联动可运行，适合课程答辩演示与后续继续扩展",
  ], { rowGap: 0.58, bodySize: 11 });
  addRoundCard(slide, 6.6, 1.42, 5.0, 3.18, BLUE_SOFT, "后续展望", [
    "OCR：支持扫描版 PDF 与图片型课件",
    "公式规范化：让数学表达更接近标准 LaTeX 排版",
    "评测增强：让数学推导与自动判分更稳定",
  ], { rowGap: 0.58, bodySize: 11 });
  slide.addShape(pptx._shapeType.roundRect, {
    x: 0.92,
    y: 5.2,
    w: 11.56,
    h: 1.18,
    rectRadius: 0.12,
    fill: { color: COPPER_SOFT },
    line: { color: COPPER_SOFT },
  });
  slide.addText("谢谢观看，欢迎提问。", {
    x: 1.1,
    y: 5.55,
    w: 11.1,
    h: 0.32,
    fontFace: "Source Han Serif SC",
    fontSize: 24,
    bold: true,
    color: BLUE_DEEP,
    align: "center",
    margin: 0,
  });
  finalizeSlide(slide);
}

async function main() {
  buildDeck();
  const out = path.join(__dirname, "courseware_review_defense.pptx");
  await pptx.writeFile({ fileName: out });
  console.log(`PPT written to ${out}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
