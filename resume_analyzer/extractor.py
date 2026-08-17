import os

from pypdf import PdfReader
from docx import Document


def extract_pdf_text(filepath):

    text = ""

    reader = PdfReader(filepath)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def extract_docx_text(filepath):

    document = Document(filepath)

    text = ""

    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            text += paragraph.text + "\n"

    return text.strip()


def extract_resume_text(filepath):

    extension = os.path.splitext(filepath)[1].lower()

    if extension == ".pdf":

        return extract_pdf_text(filepath)

    elif extension == ".docx":

        return extract_docx_text(filepath)

    else:

        raise ValueError(
            "Unsupported resume format. "
            "Use PDF or DOCX."
        )