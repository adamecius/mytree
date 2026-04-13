"""Utility to convert image-based PDF/DjVu documents into Markdown via DeepSeek-VL.

The converter extracts each page as an image, dispatches page-level inference across one
or more GPUs, and reports progress with elapsed time and ETA.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import queue
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from openai import OpenAI
except ImportError as exc:  # pragma: no cover - import guard
    raise RuntimeError(
        "The 'openai' package is required. Install it with: pip install openai"
    ) from exc


@dataclass(slots=True)
class PageResult:
    page_number: int
    markdown: str


def _to_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(image_path.as_posix())
    mime_type = mime_type or "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _run_cmd(cmd: list[str], error_hint: str) -> None:
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except FileNotFoundError as exc:
        raise RuntimeError(error_hint) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode("utf-8", errors="ignore") if exc.stderr else ""
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{stderr}") from exc


def _extract_pdf_pages(input_path: Path, output_dir: Path, dpi: int) -> list[Path]:
    _run_cmd(
        [
            "pdftoppm",
            "-r",
            str(dpi),
            "-png",
            input_path.as_posix(),
            (output_dir / "page").as_posix(),
        ],
        "Missing dependency 'pdftoppm'. Install poppler-utils.",
    )
    return sorted(output_dir.glob("page-*.png"))


def _extract_djvu_pages(input_path: Path, output_dir: Path, dpi: int) -> list[Path]:
    page_count_cmd = ["djvused", input_path.as_posix(), "-e", "n"]
    try:
        res = subprocess.run(page_count_cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("Missing dependency 'djvused'. Install djvulibre-bin.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Could not inspect DjVu file: {exc.stderr}") from exc

    page_count = int(res.stdout.strip())
    images: list[Path] = []
    for page_number in range(1, page_count + 1):
        out_file = output_dir / f"page-{page_number:06d}.png"
        _run_cmd(
            [
                "ddjvu",
                "-format=png",
                "-dpi",
                str(dpi),
                "-page",
                str(page_number),
                input_path.as_posix(),
                out_file.as_posix(),
            ],
            "Missing dependency 'ddjvu'. Install djvulibre-bin.",
        )
        images.append(out_file)

    return images


def _extract_pages(input_path: Path, output_dir: Path, dpi: int) -> list[Path]:
    suffix = input_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf_pages(input_path, output_dir, dpi)
    if suffix in {".djvu", ".djv"}:
        return _extract_djvu_pages(input_path, output_dir, dpi)
    raise ValueError("Unsupported file type. Expected .pdf, .djvu, or .djv")


def _infer_page_markdown(
    *,
    api_key: str,
    base_url: str,
    model: str,
    image_path: Path,
    prompt: str,
    temperature: float,
    max_tokens: int,
) -> str:
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {
                "role": "system",
                "content": "You are an OCR-to-Markdown assistant. Keep structure faithful to the page.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": _to_data_url(image_path)}},
                ],
            },
        ],
    )
    return response.choices[0].message.content or ""


def _gpu_worker(
    *,
    worker_id: int,
    gpu_id: str,
    jobs: "queue.Queue[tuple[int, Path] | None]",
    results: "queue.Queue[PageResult]",
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
) -> None:
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id

    while True:
        item = jobs.get()
        if item is None:
            return

        page_number, image_path = item
        try:
            markdown = _infer_page_markdown(
                api_key=api_key,
                base_url=base_url,
                model=model,
                image_path=image_path,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - network / API failure path
            markdown = f"<!-- worker {worker_id} failed on page {page_number}: {exc} -->"

        results.put(PageResult(page_number=page_number, markdown=markdown.strip()))


def _format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def convert_document(
    *,
    input_path: Path,
    output_path: Path,
    api_key: str,
    base_url: str,
    model: str,
    prompt: str,
    gpu_ids: Iterable[str],
    dpi: int,
    temperature: float,
    max_tokens: int,
) -> Path:
    with tempfile.TemporaryDirectory(prefix="doc-pages-") as tmp_dir:
        page_images = _extract_pages(input_path=input_path, output_dir=Path(tmp_dir), dpi=dpi)
        total_pages = len(page_images)
        if total_pages == 0:
            raise RuntimeError("No pages were extracted from the input document.")

        selected_gpus = [gpu.strip() for gpu in gpu_ids if gpu.strip()]
        if not selected_gpus:
            selected_gpus = ["0"]

        jobs: "queue.Queue[tuple[int, Path] | None]" = queue.Queue()
        results: "queue.Queue[PageResult]" = queue.Queue()

        for idx, page_img in enumerate(page_images, start=1):
            jobs.put((idx, page_img))
        for _ in selected_gpus:
            jobs.put(None)

        workers: list[threading.Thread] = []
        for worker_id, gpu_id in enumerate(selected_gpus, start=1):
            thread = threading.Thread(
                target=_gpu_worker,
                kwargs={
                    "worker_id": worker_id,
                    "gpu_id": gpu_id,
                    "jobs": jobs,
                    "results": results,
                    "api_key": api_key,
                    "base_url": base_url,
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                daemon=True,
            )
            thread.start()
            workers.append(thread)

        started = time.perf_counter()
        finished = 0
        collected: dict[int, str] = {}

        while finished < total_pages:
            result = results.get()
            finished += 1
            collected[result.page_number] = result.markdown

            elapsed = time.perf_counter() - started
            avg_per_page = elapsed / finished
            remaining = avg_per_page * (total_pages - finished)
            print(
                f"[progress] page {finished}/{total_pages} "
                f"elapsed={_format_duration(elapsed)} "
                f"eta={_format_duration(remaining)}"
            )

        for thread in workers:
            thread.join()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as fh:
            for page_number in range(1, total_pages + 1):
                fh.write(f"\n\n<!-- PAGE {page_number} -->\n\n")
                fh.write(collected.get(page_number, ""))
                fh.write("\n")

    return output_path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert an image-based PDF/DjVu document to Markdown via DeepSeek-VL."
    )
    parser.add_argument("input", type=Path, help="Input .pdf/.djvu/.djv file")
    parser.add_argument("output", type=Path, help="Output Markdown file path")
    parser.add_argument(
        "--api-key",
        default=os.getenv("DEEPSEEK_API_KEY", ""),
        help="DeepSeek API key (defaults to DEEPSEEK_API_KEY env var)",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        help="DeepSeek-compatible base URL",
    )
    parser.add_argument("--model", default="deepseek-vl2", help="Vision model identifier")
    parser.add_argument(
        "--prompt",
        default=(
            "Read this page and output faithful Markdown. Preserve headings, lists, tables, "
            "math, code, and figure captions when present."
        ),
        help="Prompt sent with each page image",
    )
    parser.add_argument(
        "--gpus",
        default=os.getenv("DOC2MD_GPUS", "0"),
        help="Comma-separated GPU ids, e.g. '0,1,2,3'",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Rasterization DPI")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=4096, help="Completion token cap")
    parser.add_argument(
        "--json-summary",
        action="store_true",
        help="Print JSON summary at the end for automation",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if not args.api_key:
        parser.error("Missing API key. Pass --api-key or set DEEPSEEK_API_KEY")

    started = time.perf_counter()
    output_path = convert_document(
        input_path=args.input,
        output_path=args.output,
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
        prompt=args.prompt,
        gpu_ids=args.gpus.split(","),
        dpi=args.dpi,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    elapsed = time.perf_counter() - started

    summary = {
        "input": args.input.as_posix(),
        "output": output_path.as_posix(),
        "elapsed_seconds": round(elapsed, 3),
    }
    if args.json_summary:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(f"Done: {output_path} (elapsed: {_format_duration(elapsed)})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
