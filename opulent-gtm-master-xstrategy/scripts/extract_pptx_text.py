from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source-pack" / "gtm-engineering-template.pptx"
OUTPUT = ROOT / "research" / "evidence" / "gtm-engineering-template-text.txt"
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def numeric_key(name: str):
    match = re.search(r"(\d+)", name)
    return int(match.group(1)) if match else 0


def text_from_xml(data: bytes):
    root = ET.fromstring(data)
    values = []
    for element in root.findall(".//a:t", NS):
        if element.text and element.text.strip():
            values.append(element.text.strip())
    return values


def main():
    sections = []
    with zipfile.ZipFile(SOURCE) as archive:
        slides = sorted(
            [name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)],
            key=numeric_key,
        )
        for index, slide in enumerate(slides, start=1):
            texts = text_from_xml(archive.read(slide))
            sections.append(f"SLIDE {index}\n" + "\n".join(texts))
        notes = sorted(
            [name for name in archive.namelist() if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)],
            key=numeric_key,
        )
        if notes:
            sections.append("NOTES")
            for index, note in enumerate(notes, start=1):
                texts = text_from_xml(archive.read(note))
                sections.append(f"NOTES {index}\n" + "\n".join(texts))
    OUTPUT.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
