import fitz 

def extract_text_from_pdf(pdf_file):
    """Extract raw text from an uploaded PDF file object."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()