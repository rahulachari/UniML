import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def parse_pdf(filepath):
    images = convert_from_path(
        filepath,
        poppler_path=r"C:\poppler\Library\bin"
    )

    text_data = ""

    for img in images:
        text = pytesseract.image_to_string(img)
        text_data += text + "\n"

    lines = text_data.split("\n")

    data = []

    for line in lines:
        match = re.search(
            r'(\d{1,2}[\-/\s][A-Za-z0-9]{2,9}[\-/\s]\d{2,4}).*?([+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            line
        )

        if match:
            date = match.group(1)

            amount_str = match.group(2)
            amount_str = amount_str.replace(",", "").replace("₹", "")

            try:
                amount = float(amount_str)
                data.append([date, amount])
            except:
                continue  # ✅ inside loop (correct)

    # Safety fallback
    if len(data) == 0:
        raise Exception("Could not extract transactions from PDF.")

    df = pd.DataFrame(data, columns=["date", "amount"])

    return df