# app/services/ocr.py — OCR Fallback for Scanned PDFs
#
# WHY OCR:
#   Some legal documents are scanned images embedded in PDFs (no selectable text).
#   We use pytesseract (wrapper for Google's Tesseract OCR engine) to read those.
#
# ALTERNATIVES:
#   - EasyOCR: better multilingual support, no system install needed
#   - PaddleOCR: very accurate, heavier dependency
#   - AWS Textract / Google Vision: cloud-based, high accuracy, costs money
import pytesseract

def ocr_pdf_page(page) -> str:
    """
    Takes a PyMuPDF page object, renders it to an image,
    and runs Tesseract OCR to extract text.
    """
    try:
        from PIL import Image
        import io
    except ImportError:
        raise ImportError(
            "OCR dependencies not installed. Run: pip install pytesseract Pillow\n"
            "Also install Tesseract: https://github.com/tesseract-ocr/tesseract"
        )

    # Render page as a high-res PNG image
    mat = page.get_pixmap(dpi=300)
    img_bytes = mat.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes))

    # Run OCR
    text = pytesseract.image_to_string(image, lang="eng")
    return text


def extract_text_from_scanned_pdf(file_path: str) -> str:
    """
    Full OCR pipeline for a scanned PDF file.
    Used when all pages are image-based (no native text layer).
    """
    try:
        import fitz
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install PyMuPDF")

    doc = fitz.open(file_path)
    all_text = []

    for page in doc:
        try:
            text = ocr_pdf_page(page)
            all_text.append(text)
        except Exception as e:
            all_text.append(f"[OCR failed for page: {e}]")

    doc.close()
    return "\n\n".join(all_text)