import os
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient


RUN_ROOT = Path("/Users/wanghaohua/Desktop/毕业实习/tmp/chat_quality_runs") / uuid4().hex[:8]
os.environ["APP_DATABASE_PATH"] = str(RUN_ROOT / "app.db")
os.environ["APP_UPLOAD_ROOT"] = str(RUN_ROOT / "uploads")
os.environ["APP_OUTPUT_ROOT"] = str(RUN_ROOT / "outputs")

from backend.app.main import app


QUESTIONS = [
    "请先总结《罚函数法》",
    "pdf里面有什么内容需要掌握？",
    "用数学公式帮我讲一下",
    "请告诉我这份课件最重要的 3 个概念",
    "11",
    "123",
    "请根据摘要进一步解释《罚函数法》",
    "帮我出个练习题并且仔细讲一下吧",
    "怎么解决",
]


def main() -> None:
    pdf_path = Path("/Users/wanghaohua/Desktop/罚函数法.pdf")
    RUN_ROOT.mkdir(parents=True, exist_ok=True)

    with TestClient(app) as client:
        with pdf_path.open("rb") as handle:
            upload = client.post(
                "/api/documents/upload",
                files={"file": (pdf_path.name, handle, "application/pdf")},
            )

        print("upload_status", upload.status_code)
        payload = upload.json()
        if upload.status_code != 200:
            print(payload)
            return

        document_id = payload["document"]["id"]
        for index, question in enumerate(QUESTIONS, start=1):
            response = client.post(
                f"/api/documents/{document_id}/chat",
                json={"question": question, "scope": "all"},
            )
            body = response.json()
            print(f"--- TURN {index} ---")
            print("Q:", question)
            print("status:", response.status_code)
            print("sources:", body.get("source_refs"))
            answer = body.get("answer", "")
            print("len:", len(answer))
            print(answer)
            print()


if __name__ == "__main__":
    main()
