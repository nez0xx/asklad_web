import os
from datetime import datetime

import httpx
from fastapi import UploadFile, HTTPException, status

from src.core.database import Order
from src.core.settings import BASE_DIR, settings
from src.parser import parse

import openpyxl
from openpyxl.styles import NamedStyle, Font, Border, Side


def normalize_phone(phone: str):
    reserve_phone = phone
    letters = " +-_()"

    for i in letters:
        phone = phone.replace(i, "")

    if len(phone) == 11:
        phone = "+7" + phone[1::]
        return phone

    elif len(phone) == 10:
        phone = "+7" + phone
        return phone

    return reserve_phone


async def parse_excel(file: UploadFile, ):
    content = await file.read()
    date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{date}_{file.filename}"
    full_filename = os.path.join(BASE_DIR, 'uploaded_files', filename)

    with open(full_filename, "wb") as f:
        f.write(content)

    # json объекты
    try:
        united_orders = parse(full_filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File parsing error: {e}"
        )
    os.remove(full_filename)
    return united_orders


async def create_payment_list_excel(orders: list[Order]):
    wb = openpyxl.Workbook()
    wb.create_sheet(title='Первый лист', index=0)

    ns = NamedStyle(name='highlight')
    border = Side(style='thin', color='000000')
    ns.border = Border(left=border, top=border, right=border, bottom=border)

    wb.add_named_style(ns)

    # получаем лист, с которым будем работать
    sheet = wb['Первый лист']
    sheet.cell(row=2, column=1, value="ID Заказа").style = 'highlight'
    sheet.cell(row=2, column=2, value="ФИО").style = 'highlight'
    sheet.cell(row=2, column=3, value="Телефон").style = 'highlight'
    sheet.cell(row=2, column=4, value="Дата выдачи").style = 'highlight'
    sheet.cell(row=2, column=5, value="Подпись клиента").style = 'highlight'

    for i in range(len(orders)):
        row = i+3
        order = orders[i]

        sheet.cell(row=row, column=1, value=order.id).style = 'highlight'
        sheet.cell(row=row, column=2, value=order.customer_name).style = 'highlight'
        sheet.cell(row=row, column=3, value=order.customer_phone).style = 'highlight'
        sheet.cell(row=row, column=4).style = 'highlight'
        sheet.cell(row=row, column=5).style = 'highlight'

        sheet.row_dimensions[row].height = 30
    #sheet.row_dimensions[1].height = 70

    sheet.column_dimensions['A'].width = 15
    sheet.column_dimensions['B'].width = 50
    sheet.column_dimensions['C'].width = 20
    sheet.column_dimensions['D'].width = 15
    sheet.column_dimensions['E'].width = 20



    date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{date}_payment.xlsx"
    full_filename = os.path.join(BASE_DIR, 'uploaded_files', filename)

    wb.save(full_filename)

    return full_filename



