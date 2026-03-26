# 课件智能知识点提取助手 CHECKLIST

- [x] Phase 0：建立项目骨架与工程基线
  - 计划：创建 `frontend/`、`backend/`、`data/`、`tmp/` 基础结构，补充 `README.md`、`.gitignore`、`.env.example`、运行说明与依赖清单。
  - 验收标准：项目目录完整，包含前后端入口文件与环境变量样例，第三方可按说明启动。
  - 证据：`README.md`；`backend/app/main.py`；`frontend/package.json`；`.env.example`
  - 已验证：目录结构已创建；`README.md` 包含 conda、npm、启动与 GitHub 绑定说明。

- [x] Phase 1：实现课件解析与知识点生成链路
  - 计划：实现 PPTX/PDF 文本提取、章节聚合、Qwen Turbo 调用、Markdown 输出与 SQLite 持久化。
  - 验收标准：后端能接收文件、生成章节标题/详细讲解/自测题，并保存到 `data/outputs/<document_id>/`。
  - 证据：`backend/app/services/parsers.py`；`backend/app/services/ai_client.py`；`backend/app/services/markdown_writer.py`；`data/app.db`
  - 已验证：`tmp/test_smoke.py` 通过伪 Qwen 烟测，`sample_courseware.pptx` 与 `sample_courseware.pdf` 上传接口均返回 `200`。

- [x] Phase 2：实现聊天问答与来源追踪
  - 计划：实现基于原始课件/生成笔记/全部内容的本地检索与问答接口，返回来源页码/幻灯片编号与补充说明标记。
  - 验收标准：`POST /api/documents/{id}/chat` 可根据不同 scope 返回差异化答案并附来源编号。
  - 证据：`backend/app/services/retrieval.py`；`backend/app/main.py`；聊天接口响应样例
  - 已验证：`tmp/test_smoke.py` 中 `POST /api/documents/{id}/chat` 返回 `200`，并附带来源编号列表。

- [x] Phase 3：实现现代教育 SaaS 风格前端
  - 计划：构建三栏式 React 界面，包含上传区、文档列表、章节浏览、Markdown 导出、聊天面板与响应式布局。
  - 验收标准：桌面端三栏布局完整，窄屏退化为单列；页面具备学习氛围与轻量动效。
  - 证据：`frontend/src/App.tsx`；`frontend/src/styles.css`；构建产物通过
  - 已验证：`npm run build` 成功，生成 `frontend/dist/` 产物。

- [x] Phase 4：本地 Git 初始化与工程验证
  - 计划：初始化本地 git、设置 `main` 主分支，执行前后端构建/语法验证/接口导入检查并记录结果。
  - 验收标准：存在 `.git/`，构建和基础检查完成；若受环境限制则记录阻塞项与替代方案。
  - 证据：`git status` 输出摘要；`npm run build`；`python -m compileall backend`
  - 已验证：`git init -b main` 成功；`python -m compileall backend` 与 `conda run -n assistant python -c "from backend.app.main import app; print(app.title)"` 成功。

- [x] Phase 5：NotebookLM 风格前端重构
  - 计划：把现有首页式多卡片布局重构为 Sources / Chat / Studio 三栏工作台，并补充来源卡片数据供前端引用回跳。
  - 验收标准：无大横幅，左栏显示来源片段，中栏聊天优先，右栏产出切换，Markdown 只在导出区按需展开。
  - 证据：`frontend/src/App.tsx`；`frontend/src/styles.css`；`backend/app/schemas.py`；`backend/app/repository.py`
  - 已验证：`npm run build` 通过；`tmp/test_smoke.py` 返回 `sources` 数量；聊天接口烟测仍返回 `200`。

- [x] Phase 6：高端学术工作台前端二次重构
  - 计划：保留现有 Sources / Chat / Studio 架构，拆分前端组件并整体重写为“浅色研究室”风格，突出中间聊天区的高级感。
  - 验收标准：前端拆为 `TopBar / SourcesRail / ChatWorkspace / StudioPanel` 四块；聊天区视觉优先级明显高于左右栏；`npm run build` 通过。
  - 证据：`frontend/src/App.tsx`；`frontend/src/components/TopBar.tsx`；`frontend/src/components/SourcesRail.tsx`；`frontend/src/components/ChatWorkspace.tsx`；`frontend/src/components/StudioPanel.tsx`；`frontend/src/styles.css`
  - 已验证：`npm run build` 成功，新的构建产物为 `dist/assets/index-B73AaEDI.css` 与 `dist/assets/index-BS6jUrIi.js`。

- [x] Phase 7：基于 ui-ux-pro-max 的前端三次美化
  - 计划：根据 `ui-ux-pro-max` 的高优先级规则，进一步压缩视觉噪音、强化聊天区层级、优化排版和按钮样式，并统一中英文字面风格。
  - 验收标准：主工作区更简洁、更有秩序；聊天区成为视觉主角；来源区和右侧面板退后一级；`npm run build` 继续通过。
  - 证据：`frontend/src/components/TopBar.tsx`；`frontend/src/components/SourcesRail.tsx`；`frontend/src/components/ChatWorkspace.tsx`；`frontend/src/components/StudioPanel.tsx`；`frontend/src/styles.css`
  - 已验证：`npm run build` 成功，新的构建产物为 `dist/assets/index-5JYGpbHk.css` 与 `dist/assets/index-BBnShxlg.js`。

- [x] Phase 8：3.0 对话驱动学习研究台重构
  - 计划：把产品重构为“课件资料架 / 研究对话区 / 学习任务台”三段式工作台，后端新增 `learning_board` 聚合字段，前端重做组件边界与交互逻辑。
  - 验收标准：上传后默认进入中栏对话主区；右栏展示摘要、概念、练习、复习路径；任务勾选仅保留当前页面；前后端构建与烟测通过。
  - 证据：`backend/app/schemas.py`；`backend/app/repository.py`；`backend/app/services/learning_board.py`；`frontend/src/App.tsx`；`frontend/src/components/SourceRail.tsx`；`frontend/src/components/ChatStage.tsx`；`frontend/src/components/LearningBoard.tsx`；`frontend/src/styles.css`
  - 已验证：`npm run build` 成功；`conda run -n assistant python -m compileall backend` 成功；`tmp/test_smoke.py` 返回 `learning_board` 数据。

- [x] Phase 9：基于 Web Interface Guidelines 的实现收口
  - 计划：补齐 URL 状态同步、跳过链接、焦点态、输入标签、减少运动模式、移动端无横向滚动等工程细节，避免 3.0 工作台停留在“结构对了但质感未收尾”的状态。
  - 验收标准：前端继续通过构建；后端语法和烟测继续通过；交互细节满足可访问性与稳定性要求。
  - 证据：`frontend/src/App.tsx`；`frontend/src/components/ChatStage.tsx`；`frontend/src/components/LearningBoard.tsx`；`frontend/src/styles.css`
  - 已验证：`npm run build` 成功，新的构建产物为 `dist/assets/index-DUBljkJI.css` 与 `dist/assets/index-BZF-t78-.js`。

- [x] Phase 10：Pencil 完整界面稿重画
  - 计划：在独立 `.pen` 文件中重画“对话驱动学习研究台”的完整桌面与移动端界面稿，体现资料架 / 对话区 / 学习任务台三段式结构。
  - 验收标准：至少产出 1 个桌面主工作台和 1 个移动端适配画面；完成截图校验；设计稿保存在工作区。
  - 证据：`designs/courseware_research_lab.pen`；导出截图；`tmp/BUILD_LOG.md`
  - 已验证：桌面节点 `r0GqG` 与移动端节点 `Z2wV6` 已完成截图检查，并导出为 `designs/exports/r0GqG.png` 与 `designs/exports/Z2wV6.png`。

- [x] Phase 11：按 Pencil 稿实现前端 3.0
  - 计划：把 Pencil 设计稿映射回 React 代码，重构为“资料架 / 研究对话区 / 学习任务台”三段式工作台，并补齐 `learning_board` 数据聚合与前端临时任务状态。
  - 验收标准：前端结构与 Pencil 稿一致；新增学习任务台数据在接口中可见；构建、后端语法和烟测通过。
  - 证据：`frontend/src/App.tsx`；`frontend/src/components/SourceRail.tsx`；`frontend/src/components/ChatStage.tsx`；`frontend/src/components/LearningBoard.tsx`；`frontend/src/components/TopBar.tsx`；`frontend/src/styles.css`；`backend/app/schemas.py`；`backend/app/repository.py`；`backend/app/services/learning_board.py`
  - 已验证：`npm run build` 成功；`conda run -n assistant python -m compileall backend` 成功；`tmp/test_smoke.py` 返回 `learning_board` 结构。

- [x] Phase 12：删除并重写前端以贴近 Pencil 稿
  - 计划：不再在旧前端上修补，直接重写 `App`、四个组件和整份样式表，并用真实浏览器截图对照 Pencil 导出图修正偏差。
  - 验收标准：真实页面 loaded state 在结构、按钮层级、信息密度上接近 Pencil 稿；本地开发端口变化时不再触发 `Failed to fetch`。
  - 证据：`frontend/src/App.tsx`；`frontend/src/components/TopBar.tsx`；`frontend/src/components/SourceRail.tsx`；`frontend/src/components/ChatStage.tsx`；`frontend/src/components/LearningBoard.tsx`；`frontend/src/styles.css`；`backend/app/config.py`；`backend/app/main.py`；`run_local.sh`
  - 已验证：`npm run build` 成功；`tmp/current_ui_rewrite_loaded.png` 已与 `designs/exports/r0GqG.png` 做视觉对照。

- [x] Phase 13：产品重构为“课件智能知识点复习助手”
  - 计划：将产品从“提取助手”调整为“复习助手”，移除片段来源展示，改成单一对话区 + AI 规划学习任务台，并在任务完成后进入测试环境。
  - 验收标准：UI 中不再展示来源片段；上传后自动生成学习笔记；Learning Board 由 AI 规划；全部勾选后进入选择题/填空题测试环境；构建与烟测通过。
  - 证据：`backend/app/services/ai_client.py`；`backend/app/services/learning_board.py`；`backend/app/main.py`；`frontend/src/App.tsx`；`frontend/src/components/ChatStage.tsx`；`frontend/src/components/LearningBoard.tsx`；`frontend/src/components/SourceRail.tsx`；`frontend/src/components/TopBar.tsx`
  - 已验证：`npm run build` 成功；`conda run -n assistant python -m compileall backend` 成功；`tmp/test_smoke.py` 已验证 assessment 接口返回 `200`。

- [x] Phase 14：复习助手工作流收口与联动自检
  - 计划：检查前端是否足够美观、上下文是否合理、测试环境是否按“先做题后出答案与解析”、上传和导出是否都可用且入口唯一，并修正发现的问题。
  - 验收标准：对话默认综合课件+学习笔记；Learning Board 与测试环境联动合理；上传和导出按钮只保留一处；构建和烟测继续通过。
  - 证据：`frontend/src/App.tsx`；`frontend/src/components/TopBar.tsx`；`frontend/src/components/SourceRail.tsx`；`frontend/src/components/ChatStage.tsx`；`frontend/src/components/LearningBoard.tsx`；`backend/app/main.py`；`backend/app/services/ai_client.py`
  - 已验证：`npm run build` 成功；`tmp/test_smoke.py` 输出 `assessment 200 2`；导出逻辑改为顶部统一按钮。
