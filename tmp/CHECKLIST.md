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

- [x] Phase 15：隔离烟测数据并恢复首页空状态
  - 计划：修复 `tmp/test_smoke.py` 污染真实 `data/app.db` 的问题；为后端数据路径增加环境变量覆盖；清空真实样例数据并验证首页恢复为空。
  - 验收标准：`GET /api/documents` 在真实库上返回空数组；运行 `tmp/test_smoke.py` 后真实库仍为空；首页不再出现 `sample_courseware`。
  - 证据：`backend/app/config.py`；`tmp/test_smoke.py`；`.gitignore`；`data/app.db`
  - 已验证：`sqlite3 data/app.db "SELECT COUNT(*) FROM documents;"` 返回 `0`；`conda run -n assistant python -c "from fastapi.testclient import TestClient; from backend.app.main import app; client=TestClient(app); print(client.get('/api/documents').json())"` 在烟测前后都返回 `[]`；隔离产物位于 `tmp/smoke_runs/`。

- [x] Phase 16：真实 Qwen 接口问答长度调优
  - 计划：使用真实百炼 `qwen-turbo` 跑一轮实际上传与两轮对话，确认“回答过短”的现象；随后调整后端提示词与输出预算，再做回归验证。
  - 验收标准：真实接口可成功生成课件笔记并完成两轮问答；追问回答长度明显提升，不再只停留在 1-2 句短答。
  - 证据：`backend/app/services/ai_client.py`；`tmp/real_qwen_probe.py`
  - 已验证：第一次真实回归中 `chat1_len=204`、`chat2_len=94`；调优后再次回归为 `chat1_len=254`、`chat2_len=234`。

- [x] Phase 17：数学课件笔记与计算题链路增强
  - 计划：修复 PDF 标题切分、为章节新增公式与例题结构、让 Markdown 输出更像笔记，并让 assessment 支持计算题与完整导出字段。
  - 验收标准：真实 `罚函数法.pdf` 不再只生成 1 个 section；Markdown 包含公式和例题步骤；assessment 中出现计算题；前后端构建通过。
  - 证据：`backend/app/services/parsers.py`；`backend/app/services/section_builder.py`；`backend/app/services/ai_client.py`；`backend/app/services/markdown_writer.py`；`backend/app/schemas.py`；`frontend/src/App.tsx`；`frontend/src/components/LearningBoard.tsx`
  - 已验证：`罚函数法.pdf` 真实回归中 `sections=11`、`markdown_len=11025`、assessment 含 `2` 道 calculation 题；`npm run build` 与 `conda run -n assistant python -m compileall backend` 通过；`tmp/test_smoke.py` 恢复通过。

- [x] Phase 18：研究对话区质量修复
  - 计划：修复聊天经常退化成“泛化总结”的问题，增强问题类型识别、上下文承接、公式表达稳定性和练习题连续追问能力。
  - 验收标准：`11/123` 这类低信息输入不再胡答；“用数学公式讲一下”能输出可读公式；“帮我出个练习题 / 怎么解决”能承接上一轮；后端编译继续通过。
  - 证据：`backend/app/main.py`；`backend/app/services/retrieval.py`；`backend/app/services/ai_client.py`；`tmp/chat_quality_probe.py`
  - 已验证：真实 `罚函数法.pdf` 九轮对话回归中，`11/123` 返回澄清提示；公式回答不再出现 JSON 转义乱码；练习题与“怎么解决”已承接同一道题。

- [x] Phase 19：答辩 PPT 交付
  - 计划：基于现有项目内容、界面截图和答辩结构要求，制作一套 14 页中文答辩 PPT，并交付可编辑 `.pptx + .js`。
  - 验收标准：PPT 成功生成；页数为 14 页；包含封面、背景、功能、流程、架构、难点、成果、展望等固定内容；提供预览图与重建脚本。
  - 证据：`deliverables/slides/courseware_review_defense/courseware_review_defense.js`；`deliverables/slides/courseware_review_defense/courseware_review_defense.pptx`；`deliverables/slides/courseware_review_defense/README.md`
  - 已验证：`node courseware_review_defense.js` 成功输出 `.pptx`；`conda run -n assistant python -c "from pptx import Presentation; ..."` 返回 `slides 14`；Quick Look 预览图与 montage 已生成到 `deliverables/slides/courseware_review_defense/review/`。

- [x] Phase 20：答辩稿与配音素材交付
  - 计划：围绕现有 14 页答辩 PPT 产出逐页讲稿、完整串讲稿和一键配音脚本；若音频接口可用则直接生成总音频，不可用则明确记录阻塞与复现方式。
  - 验收标准：逐页讲稿与完整总稿落盘；存在一键配音脚本；明确验证当前 Audio API 可用性；如果不可用则给出阻塞说明与后续可执行命令。
  - 证据：`deliverables/slides/courseware_review_defense/notes/courseware_review_defense_script.md`；`deliverables/slides/courseware_review_defense/notes/courseware_review_defense_full_narration.txt`；`deliverables/slides/courseware_review_defense/generate_voiceover.sh`；`output/speech/courseware_review_defense/README.md`
  - 已验证：逐页讲稿、总稿、TTS 指令文件与生成脚本已创建；当前 `.codex` 中转不支持 `Audio Speech API`，官方接口又返回 `401 invalid_api_key`，因此音频未能在本轮直接生成，阻塞已记录。

- [x] Phase 21：切换阿里云百炼语音合成并生成总音频
  - 计划：使用 `.env` 注释中的阿里云百炼 key 作为 `DASHSCOPE_API_KEY`，通过阿里云官方 HTTP 接口逐页生成 wav，再拼接为一条完整答辩音频。
  - 验收标准：14 段逐页音频全部生成；总音频成功合并；存在 manifest；总时长接近 10 分钟。
  - 证据：`deliverables/slides/courseware_review_defense/generate_aliyun_voiceover.py`；`output/speech/courseware_review_defense/chunks/`；`output/speech/courseware_review_defense/courseware_review_defense_full.wav`
  - 已验证：14 段 `slide-01.wav` 到 `slide-14.wav` 已生成；总音频 `courseware_review_defense_full.wav` 已生成；manifest 已生成；总时长约 `638.22` 秒。

- [x] Phase 22：项目海报 PDF 交付
  - 计划：基于现有项目内容与界面素材，制作一张 A2 竖版项目海报，突出项目价值、流程、亮点和技术创新，不展示真实结果数据。
  - 验收标准：成功生成海报 PNG 与 PDF；使用 `pdftoppm` 渲染预览；海报单页、结构清晰、适合答辩展示。
  - 证据：`deliverables/poster/courseware_review_assistant/build_poster.py`；`output/pdf/courseware_review_assistant_poster.pdf`；`deliverables/poster/courseware_review_assistant/review/poster_page.png`
  - 已验证：海报 PNG 与 PDF 已生成；`pdftoppm` 成功渲染预览图；海报未包含真实结果展示或个人信息。

- [x] Phase 23：2.2 项目具体工作 LaTeX 文档交付
  - 计划：只覆盖 `2.2.1 - 2.2.5`，基于当前项目代码、日志、PPT、海报、答辩稿和对话记录，写成中文课程报告风 LaTeX 文档，并使用占图盒子保留所有待补截图位置。
  - 验收标准：`report_2_2.tex` 可直接编译为 PDF；正文结构完整；无真实截图时也能成功输出；提供待补截图清单。
  - 证据：`deliverables/report_2_2/report_2_2.tex`；`deliverables/report_2_2/report_2_2.pdf`；`deliverables/report_2_2/screenshot_placeholder_list.md`
  - 已验证：`latexmk -xelatex` 成功生成 `report_2_2.pdf`；`pdftoppm` 成功渲染第一页预览图；截图清单已单独导出。
