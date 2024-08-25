import os

import fitz
from .generation import generate_html
from .schemas import Table
from datetime import datetime
import time

import pdfkit

from src.core.settings import BASE_DIR


def extract_comment(text):
    text = text.split("Комментарии и пожелания:")[1]
    comment = text.split("Код товара")[0]
    return comment


def extract_tables(filename):
    doc = fitz.open(filename)
    tables = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pdf_tables = page.find_tables()

        text = page.get_text()
        list_text = text.split("\n")

        date, phone = None, None
        comment = extract_comment(text)

        for i in range(len(list_text)):
            if list_text[i] == "Дата накладной":
                date = list_text[i+1]
            if list_text[i] == "Моб. телефон:":
                phone = list_text[i+1]
                break

        table_user_info = [["Дата накладной:", date, "    ", "Моб. телефон:", phone]]
        table_comment = [["Комментарий:", comment]]
        table_info = pdf_tables[0].extract()
        table_products = pdf_tables[1].extract()

        tables.append(Table(
            type="info",
            columns=["userId", "name", "orderId", "payment"],
            font_size=9,
            data=table_info
        ))
        tables.append(Table(
            type="products",
            columns=["prodId", "amount", "prodName", "price1", "price2", "price3", "price4"],
            font_size=7,
            data=table_products
        ))

        tables.append(Table(
            type="user_info",
            columns=["date_h", "date", "empty", "phone_h", "phone"],
            font_size=7,
            data=table_user_info
        ))
        tables.append(Table(
            type="comment",
            columns=["title", "comment"],
            font_size=7,
            data=table_comment
        ))

    return tables


def convert_pdf(filename: str):
    tables = extract_tables(filename)

    now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    pdf_filename = os.path.join(BASE_DIR, "uploaded_files", f"{now}_pdf.pdf")

    html = generate_html(tables)

    options = {
        "enable-local-file-access": "",
        'encoding': 'UTF-8'
    }
    css_path = os.path.join(BASE_DIR, "src", "pdf_parser", "styles.css")
    pdfkit.from_string(html, pdf_filename, options=options, css=css_path)

    return pdf_filename



