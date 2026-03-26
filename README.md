# 课件智能知识点复习助手

一个面向课程大作业的本地 Web 应用：上传课程 `PPTX/PDF` 后，系统会自动提取课件内容，调用 OpenAI 兼容接口生成学习笔记与复习任务台。用户可以围绕课件与学习笔记继续提问，完成任务后进入测试环境，完成选择题与填空题练习。

## 核心能力

- 支持上传 `.pptx` 与文本型 `.pdf`
- 自动抽取页面文本并按章节组织
- 自动生成章节标题、详细讲解与关键知识点
- 自动保存 Markdown 到 `data/outputs/<document_id>/`
- 自动规划 Learning Board 复习任务台
- 完成复习任务后进入测试环境，生成选择题与填空题
- 支持围绕课件与学习笔记的统一对话问答

## 技术栈

- 前端：React + TypeScript + Vite
- 后端：FastAPI + SQLite
- 模型：OpenAI 兼容模型，默认 `gpt-5.4`
- 文本提取：`python-pptx`、`PyMuPDF`

## 项目结构

```text
.
├── backend
│   ├── app
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── domain.py
│   │   ├── repository.py
│   │   ├── schemas.py
│   │   └── services
│   └── requirements.txt
├── data
│   ├── outputs
│   └── uploads
├── frontend
│   ├── src
│   ├── package.json
│   └── vite.config.ts
└── tmp
```

## 快速开始

### 1. 创建 Python 环境

按需求使用 conda 独立环境：

```bash
conda create -n courseware-knowledge-assistant python=3.11
conda activate courseware-knowledge-assistant
pip install -r backend/requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 配置环境变量

复制根目录 `.env.example` 为 `.env`，填入 OpenAI API Key：

```bash
cp .env.example .env
```

关键变量：

- `OPENAI_API_KEY`：OpenAI API Key
- `OPENAI_BASE_URL`：默认 `https://api.openai.com/v1`
- `OPENAI_MODEL`：默认 `gpt-5.4`
- `OPENAI_REASONING_EFFORT`：默认 `medium`

### 4. 启动后端

```bash
uvicorn backend.app.main:app --reload
```

### 5. 启动前端

```bash
cd frontend
npm run dev
```

浏览器访问 `http://127.0.0.1:5173`。

## API 约定

- `POST /api/documents/upload`
- `GET /api/documents`
- `GET /api/documents/{id}`
- `GET /api/documents/{id}/markdown`
- `POST /api/documents/{id}/chat`

`GET /api/documents/{id}/markdown?download=true` 可直接下载 Markdown。

## Git 与 GitHub

项目已按单仓库结构设计，默认本地使用 `main` 主分支。若要绑定 GitHub 远程仓库：

```bash
git remote add origin <your-github-repo-url>
git push -u origin main
```

## 当前范围

- 首版仅支持 `pptx` 与文本型 `pdf`
- 不支持扫描版 PDF OCR
- 不包含登录、权限、多用户协作
