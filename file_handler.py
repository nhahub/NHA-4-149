"""
File Handler Utilities
أدوات استخراج النص من أنواع الملفات المختلفة
"""
import io
import os
import zipfile

import PyPDF2

from config.settings import ALLOWED_EXTENSIONS, SKIP_DIRS, CV_KEYWORDS, CV_KEYWORD_THRESHOLD


def extract_text_from_file(file, filename: str) -> str:
    """
    يستخرج النص من: PDF، ZIP، أو أي ملف نصي مدعوم.
    يرفع ValueError إذا لم يجد محتوى صالحاً.
    """
    ext = os.path.splitext(filename.lower())[1]

    if ext == ".pdf":
        return _extract_pdf(file)

    if ext == ".zip":
        return _extract_zip(file)

    return file.read().decode("utf-8", errors="ignore")


def _extract_pdf(file) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
    text   = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        raise ValueError("لا يمكن استخراج نص من هذا الـ PDF")
    return text


def _extract_zip(file) -> str:
    parts = []
    with zipfile.ZipFile(io.BytesIO(file.read())) as zf:
        for name in zf.namelist():
            # skip hidden/cache dirs
            if any(skip in name for skip in SKIP_DIRS):
                continue
            # only allowed extensions
            if not any(name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS if ext != ".zip"):
                continue
            try:
                text = zf.read(name).decode("utf-8", errors="ignore")
                if text.strip():
                    parts.append(f"\n\n### File: {name}\n{text}")
            except Exception:
                continue

    if not parts:
        raise ValueError("لم يتم العثور على ملفات صالحة داخل الـ ZIP")
    return "\n".join(parts)


def detect_content_type(content: str) -> str:
    """
    يكتشف إذا كان المحتوى CV أم كود برمجي.
    Returns: 'cv' | 'code'
    """
    content_lower = content.lower()
    score = sum(1 for kw in CV_KEYWORDS if kw in content_lower)
    return "cv" if score >= CV_KEYWORD_THRESHOLD else "code"
