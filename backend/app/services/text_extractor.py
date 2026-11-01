import os
from pathlib import Path
from typing import Dict, Any, Tuple
from pypdf import PdfReader
from PIL import Image


class TextExtractionError(Exception):
    pass


def extract_text_from_pdf(file_path: Path) -> Tuple[str, int, int, int]:
    """
    Extracts text from a PDF file using pypdf.
    Returns: (extracted_text, page_count, word_count, char_count)
    """
    try:
        reader = PdfReader(str(file_path))
        page_count = len(reader.pages)
        if page_count == 0:
            return "", 0, 0, 0

        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages_text.append(f"--- Page {i + 1} ---\n{text.strip()}")

        full_text = "\n\n".join(pages_text).strip()
        words = len(full_text.split())
        chars = len(full_text)

        return full_text, page_count, words, chars
    except Exception as e:
        raise TextExtractionError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_text_file(file_path: Path) -> Tuple[str, int, int, int]:
    """
    Extracts text from plain text, markdown, or code files.
    Returns: (extracted_text, page_count, word_count, char_count)
    """
    try:
        # Try UTF-8 first, fallback to latin-1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()

        full_text = content.strip()
        words = len(full_text.split())
        chars = len(full_text)
        return full_text, 1, words, chars
    except Exception as e:
        raise TextExtractionError(f"Failed to read text file: {str(e)}")


def extract_text_from_image(file_path: Path) -> Tuple[str, int, int, int]:
    """
    Extracts text and metadata from an image.
    Uses pytesseract if installed, otherwise extracts structured metadata.
    Returns: (extracted_text, page_count, word_count, char_count)
    """
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            img_format = img.format or "Image"
            mode = img.mode

        ocr_text = ""
        # Try OCR if pytesseract is available
        try:
            import pytesseract
            ocr_text = pytesseract.image_to_string(str(file_path)).strip()
        except Exception:
            # Fallback to rich image metadata description
            ocr_text = (
                f"[Image Document: {file_path.name}]\n"
                f"Format: {img_format}\n"
                f"Dimensions: {width} x {height} px\n"
                f"Color Mode: {mode}\n"
                f"Visual content indexed for user knowledge library."
            )

        words = len(ocr_text.split())
        chars = len(ocr_text)
        return ocr_text, 1, words, chars
    except Exception as e:
        raise TextExtractionError(f"Failed to process image file: {str(e)}")


def process_document_file(file_path: Path, file_type: str) -> Dict[str, Any]:
    """
    Universal dispatcher for extracting text based on file format.
    """
    if not file_path.exists():
        raise TextExtractionError(f"File not found: {file_path}")

    ext = file_path.suffix.lower()

    if ext == ".pdf" or file_type == "pdf":
        text, pages, words, chars = extract_text_from_pdf(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"] or file_type == "image":
        text, pages, words, chars = extract_text_from_image(file_path)
    elif ext in [".txt", ".md", ".json", ".csv", ".py", ".html", ".js", ".ts"] or file_type in ["text", "doc"]:
        text, pages, words, chars = extract_text_from_text_file(file_path)
    else:
        # Generic fallback
        text, pages, words, chars = extract_text_from_text_file(file_path)

    return {
        "extracted_text": text,
        "page_count": pages,
        "word_count": words,
        "char_count": chars,
    }
