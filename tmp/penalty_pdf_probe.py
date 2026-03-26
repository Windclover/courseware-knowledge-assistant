import os
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient


RUN_ROOT = Path("/Users/wanghaohua/Desktop/毕业实习/tmp/penalty_pdf_runs") / uuid4().hex[:8]
os.environ["APP_DATABASE_PATH"] = str(RUN_ROOT / "app.db")
os.environ["APP_UPLOAD_ROOT"] = str(RUN_ROOT / "uploads")
os.environ["APP_OUTPUT_ROOT"] = str(RUN_ROOT / "outputs")

from backend.app.main import app


def main() -> None:
    pdf_path = Path("/Users/wanghaohua/Desktop/罚函数法.pdf")
    RUN_ROOT.mkdir(parents=True, exist_ok=True)

    with TestClient(app) as client:
        with pdf_path.open("rb") as handle:
            response = client.post(
                "/api/documents/upload",
                files={"file": (pdf_path.name, handle, "application/pdf")},
            )

        print("upload_status", response.status_code)
        payload = response.json()
        if response.status_code != 200:
            print(payload)
            return

        document = payload["document"]
        print("title", document["title"])
        print("sections", len(document["sections"]))
        for section in document["sections"]:
            print(
                "section",
                section["section_index"],
                section["title"],
                "formula_notes=",
                len(section["formula_notes"]),
                "worked_examples=",
                len(section["worked_examples"]),
                "explanation_len=",
                len(section["detailed_explanation"]),
            )

        markdown = client.get(f"/api/documents/{document['id']}/markdown").json()
        print("markdown_len", len(markdown["content"]))
        print("markdown_preview")
        print(markdown["content"][:5000])

        assessment_response = client.post(f"/api/documents/{document['id']}/assessment")
        print("assessment_status", assessment_response.status_code)
        assessment = assessment_response.json()
        if assessment_response.status_code != 200:
            print(assessment)
            return
        print("assessment_count", len(assessment["questions"]))
        for question in assessment["questions"]:
            print(
                "question",
                question["type"],
                question["prompt"][:80],
                "display_answer=",
                question.get("display_answer", ""),
                "steps=",
                len(question.get("solution_steps", [])),
            )


if __name__ == "__main__":
    main()
