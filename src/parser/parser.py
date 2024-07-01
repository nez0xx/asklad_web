from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from src.api_v1.orders.schemas import OrderSchema
from .schemas import UnitedOrder
from .utils import find
from ..api_v1.orders.products.schemas import ProductSchema


def get_united_orders_id(sheet: Worksheet):
    cell = find(sheet=sheet, value="Групповые идентификаторы: ", method="in")
    row = cell["row"]
    column = cell["column"]

    ids = sheet[column + str(row)].value.replace(";", "")
    ids = ids.split()
    ids.pop(0)
    ids.pop(0)

    return ids


def get_start_row(sheet):
    united_orders_id = get_united_orders_id(sheet)
    min_row = find(sheet=sheet, value=united_orders_id[0])["row"]

    for order_id in united_orders_id:
        row = find(sheet=sheet, value=order_id)["row"]
        if row < min_row:
            min_row = row
    return min_row


def get_last_row(sheet: Worksheet):
    cell = find(sheet=sheet, value="Итого")
    return cell["row"]


'''
Возвращает строку - общее начало для всех id заказов, чтоб можно было найти их
Функция сначала отделяет часть united_order_id, а затем подставляет к концу этой части ближайшие цифры, чтоб учесть
заказы, которые могут быть сделаны в соседних месяцах.
'''
def get_templates_of_orders_id(sheet: Worksheet) -> list[str]:
    cell = find(sheet=sheet, value="Групповые идентификаторы: ", method="in")
    row = cell["row"]
    column = cell["column"]

    united_order_id: str = sheet[column + str(row)].value.split()[2]
    start = united_order_id.find("R")
    order_id_template = united_order_id[start:]
    order_id_template = order_id_template[:5]

    month = int(order_id_template[-2:])

    templates = []

    months = [str(month-1), str(month), str(month + 1)]

    for i in range(len(months)):
        month = months[i]
        if len(month) == 1:
            month = "0"+month
        templates.append(order_id_template[:3] + month)

    return templates


def parse_worksheet(sheet: Worksheet) -> list[UnitedOrder]:
    id_templates = get_templates_of_orders_id(sheet)
    start_row = get_start_row(sheet)
    last_row = get_last_row(sheet)

    customer_id_column = find(sheet, "ID Клиента")["column"]
    order_id_column = find(sheet, "ID Заказа")["column"]
    customer_name_column = find(sheet, "ФИО")["column"]
    customer_phone_column = find(sheet, "Телефон")["column"]
    product_title_column = "D"
    product_amount_column = find(sheet, "Заказано")["column"]
    product_id_column = order_id_column

    united_order_ids = get_united_orders_id(sheet)

    united_orders: list[UnitedOrder] = []

    for row in range(start_row, last_row):

        cell_value = str(sheet[f"{order_id_column}{row}"].value)

        if cell_value in united_order_ids:
            united_order = UnitedOrder(united_order_id=cell_value, orders=list())
            united_orders.append(united_order)
            continue

        # Если нашли начало блока с информацией о конкретном заказе
        if cell_value.startswith(id_templates[0])\
            or cell_value.startswith(id_templates[1])\
                or cell_value.startswith(id_templates[2]):

            order_id = sheet[f"{order_id_column}{row}"].value
            name = sheet[f"{customer_name_column}{row}"].value
            customer_id = sheet[f"{customer_id_column}{row}"].value
            phone = sheet[f"{customer_phone_column}{row}"].value
            order = OrderSchema(
                order_id=order_id,
                customer_name=name,
                customer_id=customer_id,
                customer_phone=phone,
                products=[]
            )

            united_orders[-1].orders.append(order)

        else:

            product_id = sheet[f"{product_id_column}{row}"].value
            # строка с product_title это объединенная строка, поэтому приходится вытаскивать значения как из матрицы
            product_title = sheet[f"{product_title_column}{row}"].value
            product_amount = sheet[f"{product_amount_column}{row}"].value

            product = ProductSchema(
                product_id=product_id,
                title=product_title,
                amount=product_amount
            )

            last_order = united_orders[-1].orders[-1]
            last_order.products.append(product)

    return united_orders


def parse(filename: str):
    book = load_workbook(filename=filename, data_only=True)
    worksheet: Worksheet = book["Лист_1"]

    united_orders = parse_worksheet(worksheet)
    united_orders_json = []

    for elem in united_orders:
        united_orders_json.append(elem.model_dump())

    return united_orders_json


