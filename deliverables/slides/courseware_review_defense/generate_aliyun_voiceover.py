#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
import wave
from pathlib import Path
from urllib import request


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parents[2]
SCRIPT_MD = ROOT / "notes" / "courseware_review_defense_script.md"
OUTPUT_DIR = PROJECT_ROOT / "output" / "speech" / "courseware_review_defense"
CHUNK_DIR = OUTPUT_DIR / "chunks"
FULL_WAV = OUTPUT_DIR / "courseware_review_defense_full.wav"
MANIFEST = OUTPUT_DIR / "courseware_review_defense_manifest.json"
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
MODEL = "qwen3-tts-instruct-flash"
VOICE = "Cherry"
INSTRUCTIONS = "语气稳重，正式，适合课程答辩讲解。语速中等偏慢，吐字清晰。"


def get_dashscope_key() -> str:
    env_path = PROJECT_ROOT / ".env"
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("DASHSCOPE_API_KEY="):
            value = line.split("=", 1)[1].strip()
            if value:
                return value
        if line.startswith("## "):
            value = line[3:].strip()
            if value:
                return value
    raise RuntimeError("未在 .env 中找到可用的 DASHSCOPE API Key。")


def parse_slide_scripts(text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r"^## Slide (\d+)｜(.+?)\n.*?- 推荐口播正文：\n\n(.+?)(?=\n## Slide |\Z)",
        re.S | re.M,
    )
    items: list[dict[str, str]] = []
    for match in pattern.finditer(text):
        slide_no, title, narration = match.groups()
        clean_narration = "\n".join(line.rstrip() for line in narration.strip().splitlines())
        items.append(
            {
                "slide": slide_no,
                "title": title.strip(),
                "input": clean_narration,
            }
        )
    if not items:
        raise RuntimeError("未能从讲稿中解析出逐页口播正文。")
    return items


def call_tts(api_key: str, text: str, out_path: Path) -> dict:
    payload = {
        "model": MODEL,
        "input": {
            "text": text,
            "voice": VOICE,
            "language_type": "Chinese",
            "instructions": INSTRUCTIONS,
            "optimize_instructions": True,
        },
    }
    req = request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=180) as response:
        body = response.read().decode("utf-8")
    data = json.loads(body)
    url = data.get("output", {}).get("audio", {}).get("url")
    if not url:
        raise RuntimeError(f"语音生成失败：{body}")
    request.urlretrieve(url, out_path)
    return data


def merge_wavs(inputs: list[Path], output_path: Path, silence_ms: int = 300) -> None:
    if not inputs:
        raise RuntimeError("没有可合并的 wav 文件。")

    with wave.open(str(inputs[0]), "rb") as first:
        params = first.getparams()
        nchannels = first.getnchannels()
        sampwidth = first.getsampwidth()
        framerate = first.getframerate()
        silence_frames = int(framerate * silence_ms / 1000)
        silence = b"\x00" * silence_frames * nchannels * sampwidth

    with wave.open(str(output_path), "wb") as out:
        out.setparams(params)
        for index, wav_path in enumerate(inputs):
            with wave.open(str(wav_path), "rb") as src:
                if (
                    src.getnchannels() != nchannels
                    or src.getsampwidth() != sampwidth
                    or src.getframerate() != framerate
                    or src.getcomptype() != params.comptype
                ):
                    raise RuntimeError(f"wav 参数不一致，无法拼接：{wav_path}")
                out.writeframes(src.readframes(src.getnframes()))
            if index < len(inputs) - 1:
                out.writeframes(silence)


def main() -> None:
    api_key = get_dashscope_key()
    slides = parse_slide_scripts(SCRIPT_MD.read_text(encoding="utf-8"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, str | int]] = []
    chunk_paths: list[Path] = []

    for item in slides:
        slide_no = str(item["slide"]).zfill(2)
        out_path = CHUNK_DIR / f"slide-{slide_no}.wav"
        data = call_tts(api_key, str(item["input"]), out_path)
        manifest.append(
            {
                "slide": int(item["slide"]),
                "title": str(item["title"]),
                "request_id": str(data.get("request_id", "")),
                "output": str(out_path),
                "characters": int(data.get("usage", {}).get("characters", 0)),
            }
        )
        chunk_paths.append(out_path)
        time.sleep(0.5)

    merge_wavs(chunk_paths, FULL_WAV)
    MANIFEST.write_text(
        json.dumps(
            {
                "model": MODEL,
                "voice": VOICE,
                "instructions": INSTRUCTIONS,
                "chunks": manifest,
                "full_output": str(FULL_WAV),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Generated {len(chunk_paths)} chunks")
    print(f"Full audio: {FULL_WAV}")


if __name__ == "__main__":
    main()
