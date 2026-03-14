import fitz
import sys

def extract_text(pdf_path, txt_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)

if __name__ == "__main__":
    extract_text(sys.argv[1], sys.argv[2])
