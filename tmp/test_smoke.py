from pathlib import Path

import fitz
from fastapi.testclient import TestClient
from pptx import Presentation

from backend.app.domain import ChatAnswerResult, GeneratedSection
import backend.app.main as main_module
import backend.app.services.pipeline as pipeline_module


TMP_DIR = Path("tmp")


class FakeQwen:
    def generate_section(self, document_title, draft):
        return GeneratedSection(
            section_index=draft.section_index,
            title=draft.title,
            detailed_explanation=f"{draft.title} 的详细讲解：用于复习与答辩展示。",
            key_points=[
                "监督学习依赖带标签数据",
                "分类与回归是典型任务",
            ],
            quiz=[
                "什么是监督学习？",
                "分类任务与回归任务有何区别？",
                "带标签数据有什么作用？",
            ],
            source_refs=draft.source_refs,
        )

    def answer_question(self, **kwargs):
        return ChatAnswerResult(
            answer="这是基于课件内容生成的回答。",
            source_refs=["第 1 张幻灯片"],
            supplemental=True,
            supplemental_notes="这里补充了一点通用常识。",
        )


def create_sample_files() -> tuple[Path, Path]:
    TMP_DIR.mkdir(exist_ok=True)

    pptx_path = TMP_DIR / "sample_courseware.pptx"
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide.shapes.title.text = "监督学习"
    slide.placeholders[1].text = "监督学习依赖带标签数据\n常见任务包括分类和回归"
    presentation.save(pptx_path)

    pdf_path = TMP_DIR / "sample_courseware.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "监督学习导论\n监督学习使用带标签数据。\n分类与回归是典型任务。",
    )
    document.save(pdf_path)
    document.close()

    return pptx_path, pdf_path


def main() -> None:
    pipeline_module.QwenClient = FakeQwen
    main_module.QwenClient = FakeQwen
    pptx_path, pdf_path = create_sample_files()

    with TestClient(main_module.app) as client:
        last_document_id = ""
        for file_path, content_type in [
            (
                pptx_path,
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ),
            (pdf_path, "application/pdf"),
        ]:
            with file_path.open("rb") as handle:
                response = client.post(
                    "/api/documents/upload",
                    files={"file": (file_path.name, handle, content_type)},
                )
            payload = response.json()
            last_document_id = payload["document"]["id"]
            print(
                file_path.name,
                response.status_code,
                payload["document"]["sections"][0]["title"],
                len(payload["document"]["sources"]),
                len(payload["document"]["learning_board"]["concepts"]),
                len(payload["document"]["learning_board"]["practice"]),
            )

        chat_response = client.post(
            f"/api/documents/{last_document_id}/chat",
            json={"question": "这一章讲了什么？", "scope": "all"},
        )
        chat_payload = chat_response.json()
        print("chat", chat_response.status_code, chat_payload["source_refs"])


if __name__ == "__main__":
    main()
