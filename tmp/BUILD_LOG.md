# BUILD LOG

## Phase 0 - 初始化记录

- 时间：2026-03-25
- 用途：记录从空目录搭建“课件智能知识点提取助手”的关键决策、验证结果与阻塞项。
- 生成方式：由实现过程中的人工记录维护。

### 当前已知事实

- 工作区初始为空目录。
- `conda 25.11.1`、`Python 3.13.11`、`Node v25.2.1`、`npm 11.6.2` 可用。
- 当前不是 git 仓库。

### 已确认决策

- 技术栈：`React + FastAPI`
- 模型：阿里云百炼 `qwen-turbo`
- 输入范围：`PPTX + 文本型 PDF`
- 输出形态：总 Markdown + 章节导航
- 聊天范围：课件优先，可少量补充常识
- 来源展示：显示页码/幻灯片编号
- UI 风格：现代教育 SaaS

### 可清理条件

- `tmp/` 目录中的过程文件在项目交付完成且信息已同步到正式文档后可清理。

## Phase 1 - 代码落地

- 创建了根配置与工程说明：`README.md`、`.gitignore`、`.env.example`
- 创建了后端模块：配置、SQLite 存储、PPTX/PDF 解析、章节聚合、Qwen 调用、Markdown 输出、检索与聊天接口
- 创建了前端模块：三栏布局、上传、历史文档、章节阅读、Markdown 预览、问答面板

## Phase 2 - 环境与依赖

- 前端依赖通过 `npm install --cache /Users/wanghaohua/Desktop/毕业实习/frontend/.npm-cache` 安装
  - 用途：避开系统全局 npm 缓存权限问题
  - 生成方式：在 `frontend/` 下执行带本地缓存目录的 `npm install`
- 创建 conda 环境：`conda create -n assistant python=3.11 -y`
  - 用途：按用户要求在独立环境中安装后端依赖
  - 风险：会写入用户本机 conda 环境目录
- 后端依赖安装：`conda run -n assistant pip install -r backend/requirements.txt`
  - 用途：运行 FastAPI 与课件解析依赖，供后续验证

## Phase 3 - 验证记录

- Python 语法检查：
  - 命令：`python -m compileall backend`
  - 结果：通过
- Conda 环境语法检查：
  - 命令：`conda run -n assistant python -m compileall backend`
  - 结果：通过
- FastAPI 导入检查：
  - 命令：`conda run -n assistant python -c "from backend.app.main import app; print(app.title)"`
  - 结果：输出 `课件智能知识点提取助手`
- 健康检查：
  - 命令：`conda run -n assistant python -c "from fastapi.testclient import TestClient; from backend.app.main import app; client = TestClient(app); print(client.get('/api/health').json())"`
  - 结果：返回 `{'status': 'ok'}`
- 前端构建：
  - 命令：`npm run build`
  - 结果：通过，生成 `frontend/dist/`
- 端到端烟测：
  - 产物：`tmp/test_smoke.py`
  - 用途：生成示例 PPTX/PDF，替换真实 Qwen 调用，验证上传、生成与聊天接口
  - 命令：`conda run -n assistant python -c "import runpy, sys; sys.path.insert(0, '.'); runpy.run_path('tmp/test_smoke.py', run_name='__main__')"`
  - 输出摘要：
    - `sample_courseware.pptx 200 监督学习`
    - `sample_courseware.pdf 200 第 1 部分`
    - `chat 200 ['第 1 张幻灯片']`

## Phase 4 - Git

- 初始化本地仓库：
  - 命令：`git init -b main`
  - 结果：成功，当前已进入本地 git 管理状态
- 本地提交状态：
  - 检查：`git config user.name`、`git config user.email`
  - 结果：当前机器未配置 git 提交身份，因此未自动创建首个 commit，也未绑定 GitHub remote

## Phase 5 - NotebookLM 风格重构

- 重构目标：
  - 从“多张独立卡片并列展示”改成“Sources / Chat / Studio”学习工作台
  - 聊天区成为主焦点，Markdown 预览降级到导出区
  - 左栏支持来源片段卡片与引用回跳
- 主要实现：
  - 前端重写 `frontend/src/App.tsx`
  - 前端重写 `frontend/src/styles.css`
  - 后端新增 `SourceFragment` 响应模型，并在 `DocumentDetail` 中返回 `sources`
- UI 决策：
  - 去掉 hero 横幅、气泡背景、玻璃拟态
  - 改为暖白纸面感 + 低饱和蓝灰的工具型界面
  - 平板与手机端使用顶部 pane 切换，避免三栏挤压
- 本阶段验证：
  - 前端构建：
    - 命令：`npm run build`
    - 结果：通过，生成新的 `frontend/dist/`
  - 后端语法检查：
    - 命令：`conda run -n assistant python -m compileall backend`
    - 结果：通过
  - 端到端烟测：
    - 命令：`conda run -n assistant python -c "import runpy, sys; sys.path.insert(0, '.'); runpy.run_path('tmp/test_smoke.py', run_name='__main__')"`
  - 输出摘要：
    - `sample_courseware.pptx 200 监督学习 1`
    - `sample_courseware.pdf 200 第 1 部分 1`
    - `chat 200 ['第 1 张幻灯片']`

## Phase 6 - 高端学术工作台二次重构

- 重构目标：
  - 保留三栏工作台，但将视觉从“功能原型”提升到“浅色研究室”风格
  - 中栏聊天区成为绝对主焦点，左右两栏退后一级
  - 前端按职责拆为 `TopBar / SourcesRail / ChatWorkspace / StudioPanel`
- 主要实现：
  - 新增组件文件：
    - `frontend/src/components/TopBar.tsx`
    - `frontend/src/components/SourcesRail.tsx`
    - `frontend/src/components/ChatWorkspace.tsx`
    - `frontend/src/components/StudioPanel.tsx`
  - `frontend/src/App.tsx` 仅保留状态管理、数据流和跨区联动逻辑
  - `frontend/src/styles.css` 整体重写为冷白底、石墨文字、雾蓝灰/铜金点缀的轻奢学术风格
- 关键设计决策：
  - 顶栏改为真正的工具栏，不再承担说明性内容
  - 来源列表改为“研究资料架”风格，选中项用左侧标记线强调
  - 聊天消息区改为“研究笔记对话”风格，AI 回答区增加正文式排版与脚注感引用
  - Studio 右栏用更克制的折叠研究条目呈现章节与自测题
- 本阶段验证：
  - 前端构建：
    - 命令：`npm run build`
    - 结果：通过
    - 产物：`dist/assets/index-B73AaEDI.css`、`dist/assets/index-BS6jUrIi.js`
- 当前残留：
  - 已完成构建级验证，但未进行浏览器截图级视觉验收；如需继续微调，可基于实际观感再做第三轮样式修整

## Phase 7 - ui-ux-pro-max 指南驱动的三次美化

- 触发原因：
  - 用户明确点名 `ui-ux-pro-max`，并指出现有前端“很丑”
- 技能使用情况：
  - 已读取用户提供的 `ui-ux-pro-max` 技能正文
  - 尝试执行技能中推荐的 `search.py --design-system` 流程，但本机 skill 目录中的 `scripts` 为路径占位文件，指向的真实脚本不存在，因此无法自动生成设计系统
  - 回退为按技能正文中的高优先级规则执行人工重构：层级、排版、字体、配色、按钮、响应式与交互反馈
- 本轮具体调整：
  - 顶栏品牌、状态和上传/导出区统一为更克制的研究工具语言
  - Sources 区改成更像资料架的细列表，而非柔软卡片堆叠
  - Chat 区改成正文型消息排版，回答区强化为主要视觉焦点
  - Studio 区保持辅助角色，进一步削弱重量
  - 样式系统重新收口到冷白、石墨黑、雾蓝灰和铜棕点缀
- 本阶段验证：
  - 前端构建：
    - 命令：`npm run build`
    - 结果：通过
    - 产物：`dist/assets/index-5JYGpbHk.css`、`dist/assets/index-BBnShxlg.js`

## Phase 8 - 3.0 对话驱动学习研究台

- 重构目标：
  - 从“来源 / 对话 / 导出”三块并列工具区，升级为单课件、对话驱动的学习研究工作台
  - 中栏为唯一主工作流，右栏从 `Studio` 改成学习任务台
  - 后端补齐 `learning_board` 聚合字段，前端不再在浏览器里临时拼装任务数据
- 后端实现：
  - `backend/app/schemas.py` 新增：
    - `LearningSummaryItem`
    - `LearningConceptItem`
    - `LearningPracticeItem`
    - `LearningReviewStep`
    - `LearningBoard`
  - `backend/app/services/learning_board.py` 新增学习任务聚合逻辑
  - `backend/app/repository.py` 在 `DocumentDetail` 中注入 `learning_board`
- 前端实现：
  - `frontend/src/App.tsx` 改为只负责数据获取、URL 状态同步、跨区联动和临时任务状态
  - 组件边界调整为：
    - `TopBar`
    - `SourceRail`
    - `ChatStage`
    - `LearningBoard`
  - 新增能力：
    - URL 同步 `doc / pane / scope`
    - 学习任务完成状态仅当前页面内存保存
    - 任务项可一键把问题送到聊天区
    - 学习进度汇总与进度条
  - 样式系统重写为更明确的三层结构：
    - 资料架更轻
    - 聊天主区更强
    - 学习任务台更像辅助研究面板
- 本阶段验证：
  - 前端构建：
    - 命令：`npm run build`
    - 结果：通过
    - 产物：`dist/assets/index-BMcLenXh.css`、`dist/assets/index-CrVWjMBM.js`
  - 后端语法检查：
    - 命令：`conda run -n assistant python -m compileall backend`
    - 结果：通过
  - 端到端烟测：
    - 命令：`conda run -n assistant python -c "import runpy, sys; sys.path.insert(0, '.'); runpy.run_path('tmp/test_smoke.py', run_name='__main__')"`
    - 输出摘要：
      - `sample_courseware.pptx 200 监督学习 1 2 3`
      - `sample_courseware.pdf 200 第 1 部分 1 2 3`
      - `chat 200 ['第 1 张幻灯片']`

## Phase 9 - Web Interface Guidelines 收口

- 触发原因：
  - 用户显式点名 `web-design-guidelines`，要求“重新设计整个 UI 和功能”
- 执行方式：
  - 已读取技能说明
  - 已按技能要求抓取最新 guidelines 源地址
  - 在 3.0 重构基础上，补齐以下实现细节：
    - `skip link`
    - `aria-live` 错误提示
    - URL 同步 `doc / pane / scope`
    - 输入标签与 `name`
    - `focus-visible` 样式
    - `prefers-reduced-motion`
    - `overflow-x: hidden`
    - 数字使用 `tabular-nums`
    - 点击目标与 hover/active 反馈收口
- 本阶段验证：
  - 前端构建：
    - 命令：`npm run build`
    - 结果：通过
    - 产物：`dist/assets/index-DUBljkJI.css`、`dist/assets/index-BZF-t78-.js`
  - 后端语法检查：
    - 命令：`conda run -n assistant python -m compileall backend`
    - 结果：通过
  - 端到端烟测：
    - 命令：`conda run -n assistant python -c "import runpy, sys; sys.path.insert(0, '.'); runpy.run_path('tmp/test_smoke.py', run_name='__main__')"`
    - 输出摘要：
      - `sample_courseware.pptx 200 监督学习 1 2 3`
      - `sample_courseware.pdf 200 第 1 部分 1 2 3`
      - `chat 200 ['第 1 张幻灯片']`

## Phase 10 - Pencil 设计稿

- 目标：
  - 用独立 `.pen` 文件重画完整界面稿，而不是继续在代码里抽象描述
- 初始化：
  - 新建工作区文件：`designs/courseware_research_lab.pen`
  - 用途：承载桌面主工作台与移动端适配设计稿
- 设计方向：
  - 桌面稿：冷白研究工作台，三栏结构明确，中栏对话为主舞台
  - 移动稿：单列研究台，保留“对话 + 任务 + 来源”核心信息
- 主要产出：
  - 桌面节点：`r0GqG`
  - 移动节点：`Z2wV6`
- 导出结果：
  - `/Users/wanghaohua/Desktop/毕业实习/designs/exports/r0GqG.png`
  - `/Users/wanghaohua/Desktop/毕业实习/designs/exports/Z2wV6.png`
- 视觉检查：
  - 已通过 `get_screenshot` 检查桌面与移动画面，无明显错位或重叠

## Phase 11 - Pencil 稿落代码

- 目标：
  - 按 Pencil 设计稿，把产品实现为单课件、对话驱动的学习研究台
- 后端实现：
  - `backend/app/schemas.py` 新增 `LearningBoard` 及其子项类型
  - `backend/app/services/learning_board.py` 新增聚合逻辑
  - `backend/app/repository.py` 在 `DocumentDetail` 中返回 `learning_board`
- 前端实现：
  - `frontend/src/App.tsx` 重构为状态与联动总控
  - 组件结构改为：
    - `TopBar`
    - `SourceRail`
    - `ChatStage`
    - `LearningBoard`
  - 新增能力：
    - 单课件 URL 状态同步 `doc / pane / scope`
    - 学习任务临时勾选状态
    - 学习进度展示
    - 任务项一键转化为聊天问题
  - 旧组件 `SourcesRail / ChatWorkspace / StudioPanel` 被替换
- 设计落地要点：
  - 中栏成为唯一主舞台
  - 右栏从“导出区”重构为“学习任务台”
  - Markdown 降级为次级导出能力
  - 桌面端三栏，移动端 pane 切换
- 本阶段验证：
  - 前端构建：
    - 命令：`npm run build`
    - 结果：通过
    - 产物：`dist/assets/index-DUBljkJI.css`、`dist/assets/index-BZF-t78-.js`
  - 后端语法检查：
    - 命令：`conda run -n assistant python -m compileall backend`
    - 结果：通过
  - 端到端烟测：
    - 命令：`conda run -n assistant python -c "import runpy, sys; sys.path.insert(0, '.'); runpy.run_path('tmp/test_smoke.py', run_name='__main__')"`
    - 输出摘要：
      - `sample_courseware.pptx 200 监督学习 1 2 3`
      - `sample_courseware.pdf 200 第 1 部分 1 2 3`
      - `chat 200 ['第 1 张幻灯片']`

## Phase 12 - 前端删除重写与真实页面对照

- 用户反馈：
  - “前端和 Pencil 的效果完全不一样”
- 排查结果：
  - 首先定位到一个运行时问题：前端有时跑到 `5174/5175/5176`，而后端原本只允许 `5173`，导致 loaded state 实际是 `Failed to fetch`
  - 这会让页面看起来和设计稿完全不是一回事
- 修复：
  - `backend/app/config.py`：新增 `cors_origin_regex`
  - `backend/app/main.py`：启用 `allow_origin_regex`
  - `.env.example`：补充 `CORS_ORIGIN_REGEX`
  - `run_local.sh`：改为自动选择空闲前端端口并打印真实地址
- 前端重写：
  - 删除并重写：
    - `frontend/src/App.tsx`
    - `frontend/src/components/TopBar.tsx`
    - `frontend/src/components/SourceRail.tsx`
    - `frontend/src/components/ChatStage.tsx`
    - `frontend/src/components/LearningBoard.tsx`
    - `frontend/src/styles.css`
  - 保留后端接口层与类型层，只重建展示结构与样式
- 真实页面截图对照：
  - 错误态截图：`tmp/current_ui.png`
  - 载入后截图：`tmp/current_ui_rewrite_loaded.png`
  - Pencil 参考图：`designs/exports/r0GqG.png`
- 本阶段验证：
  - `curl -i -H 'Origin: http://127.0.0.1:5176' http://127.0.0.1:8001/api/documents`
    - 返回 `access-control-allow-origin: http://127.0.0.1:5176`
  - `npm run build`
    - 通过
    - 产物：`dist/assets/index-Dt-tmoYr.css`、`dist/assets/index-FBEKs0D-.js`
  - 重写后再次构建：
    - 通过
    - 产物：`dist/assets/index-Dt-tmoYr.css`、`dist/assets/index-FBEKs0D-.js`

## Phase 13 - 复习助手产品重构

- 产品调整：
  - 名称从“课件智能知识点提取助手”改为“课件智能知识点复习助手”
  - 删除 UI 中的片段来源展示，仅保留课件与学习笔记摘要
  - 研究对话区移除原始课件 / 生成笔记 / 全部内容切换，默认统一基于课件 + 学习笔记回答
  - 学习笔记生成阶段不再直接生成自测题
- 后端实现：
  - `QwenClient.generate_section()` 去掉 quiz 输出
  - 新增 `QwenClient.generate_learning_board()` 规划学习任务台
  - 新增 `QwenClient.generate_assessment()` 生成选择题与填空题
  - `GET /api/documents/{id}` 返回的 `learning_board` 结构升级
  - 新增 `POST /api/documents/{id}/assessment`
- 前端实现：
  - 左栏改为“课件与学习笔记”
  - 中栏改为单一干净对话区
  - 右栏学习任务全部完成后切换到测试环境
  - 测试环境支持：
    - 单选题作答
    - 填空题作答
    - 提交后显示正确/错误
    - 显示题目解析
- 本阶段验证：
  - 前端构建：
    - 命令：`npm run build`
    - 结果：通过
    - 产物：`dist/assets/index-BsoGBjr0.css`、`dist/assets/index-Bb6306az.js`
  - 后端语法检查：
    - 命令：`conda run -n assistant python -m compileall backend`
    - 结果：通过
  - 端到端烟测：
    - 命令：`conda run -n assistant python -c "import runpy, sys; sys.path.insert(0, '.'); runpy.run_path('tmp/test_smoke.py', run_name='__main__')"`
    - 输出摘要：
      - `sample_courseware.pptx 200 监督学习 1 1 1`
      - `sample_courseware.pdf 200 第 1 部分 1 1 1`
      - `chat 200 ['第 1 张幻灯片']`
      - `assessment 200 2`
