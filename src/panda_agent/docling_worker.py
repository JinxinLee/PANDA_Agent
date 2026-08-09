"""Isolated CPU-limited Docling converter for one PDF."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption


def main() -> None:
    source, destination = Path(sys.argv[1]), Path(sys.argv[2])
    options = PdfPipelineOptions()
    options.do_ocr = False
    options.do_table_structure = True
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )
    exported = converter.convert(source).document.export_to_dict()
    destination.write_text(
        json.dumps(exported, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
