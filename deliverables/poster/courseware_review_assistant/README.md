# 课件智能知识点复习助手项目海报

交付物：

- `build_poster.py`
- `courseware_review_assistant_poster.png`
- `output/pdf/courseware_review_assistant_poster.pdf`
- `review/poster_page.png`

## 生成海报

```bash
python3 /Users/wanghaohua/Desktop/毕业实习/deliverables/poster/courseware_review_assistant/build_poster.py
```

## 渲染预览

```bash
cd /Users/wanghaohua/Desktop/毕业实习/deliverables/poster/courseware_review_assistant
pdftoppm -png -singlefile ../../../output/pdf/courseware_review_assistant_poster.pdf review/poster_page
```

## 说明

- 海报规格：A2 竖版
- 风格：清晰、稳重、技术型项目展示
- 内容：仅展示项目能力、流程、技术创新与界面亮点，不展示真实结果数据或个人信息
