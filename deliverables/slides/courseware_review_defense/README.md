# 课件智能知识点复习助手答辩 PPT

交付物：

- `courseware_review_defense.pptx`
- `courseware_review_defense.js`
- `build_deck.sh`
- `render_preview.sh`

## 说明

- 该 deck 采用 `PptxGenJS` 生成，比例固定为 `16:9`
- 主素材来自项目当前界面截图与 Pencil 导出图
- 工作区内已包含 `pptxgenjs_helpers` 和本地 `node_modules/`，可直接重建

## 重新生成

```bash
cd /Users/wanghaohua/Desktop/毕业实习/deliverables/slides/courseware_review_defense
./build_deck.sh
```

## 生成预览图

```bash
cd /Users/wanghaohua/Desktop/毕业实习/deliverables/slides/courseware_review_defense
./render_preview.sh
```

预览图默认输出到 `review/` 目录。
