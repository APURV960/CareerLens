import io
import pdfplumber

def parse_resume(path_or_bytes):
    """
    Parses resume PDF text from either a local file path, raw file bytes, 
    or an in-memory file stream.
    """
    text = ""
    
    # If the input is raw bytes, wrap it in a BytesIO stream
    if isinstance(path_or_bytes, bytes):
        file_source = io.BytesIO(path_or_bytes)
    else:
        file_source = path_or_bytes

    with pdfplumber.open(file_source) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text