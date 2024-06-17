from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from .schemas import Order, Product, Customer, UnitedOrder


def find(
        sheet: Worksheet,
         value,
         method: str = "equal",
         start: int = 1,
         end: int = 10000,
        ) -> dict | None:

    letters = list("ABCDEFGHIJ")

    for row in range(start, end):
        for column in letters:

            cell_value = str(sheet[column + str(row)].value)
            cell = {"row": row, "column": column}

            if cell_value == 'None':
                continue

            if method == "equal" and cell_value == value:
                return cell

            if method == "in" and value in cell_value:
                return cell

            if method == "startswith":
                if cell_value.startswith(value):
                    return cell
    return None


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
    min_row = find(sheet=sheet, value=united_orders_id[0])["row"]+1
    for order_id in united_orders_id:
        row = find(sheet=sheet, value=order_id)["row"]+1
        if row < min_row:
            min_row = row
    return min_row


def get_last_row(sheet: Worksheet):
    cell = find(sheet=sheet, value="Итого")
    return cell["row"]


# Возвращает строку - общее начало для всех id заказов, чтоб можно было отделить их
def get_templates_of_id(sheet: Worksheet) -> list[str]:
    cell = find(sheet=sheet, value="Групповые идентификаторы: ", method="in")
    row = cell["row"]
    column = cell["column"]

    # cell_value = sheet[column + str(row)].value.replace(";", "")
    # orders_id = cell_value.split()
    # orders_id.pop(0)
    # orders_id.pop(0)

    order_id = sheet[column + str(row)].value.split()[2]
    template_start = order_id.find("R")
    id_template = order_id[template_start:]
    id_template = id_template[:5]

    month = int(id_template[-2:])

    templates = []

    months = [str(month-1), str(month), str(month + 1)]

    for i in range(len(months)):
        month = months[i]
        if len(month) == 1:
            month = "0"+month
        templates.append(id_template[:3] + month)

    return templates


def parse(sheet: Worksheet) -> list[Order]:

    letters = "ABCDEFGHIJ"
    templates = get_templates_of_id(sheet)
    start_row = get_start_row(sheet)
    last_row = get_last_row(sheet)
    customer_id_column = find(sheet, "ID Клиента")["column"]
    orders: list[Order] = []

    for row in range(start_row, last_row):

        cell_value = str(sheet[f"A{row}"].value)

        # Нашли начало блока с инфой о заказе
        if cell_value.startswith(templates[0])\
            or cell_value.startswith(templates[1])\
                or cell_value.startswith(templates[2]):

            order_id = sheet[f"A{row}"].value
            name = sheet[f"D{row}"].value
            customer_id = sheet[f"{customer_id_column}{row}"].value
            phone = sheet[f"H{row}"].value
            order = Order(
                atomy_id=order_id,
                customer=Customer(name=name, atomy_id=customer_id),
                customer_phone=phone,
                products=[]
            )
            orders.append(order)
        else:
            product_id = sheet[f"A{row}"].value
            product_title = sheet[f"D{row}"].value
            product_amount = sheet[f"I{row}"].value
            product = Product(
                atomy_id=product_id,
                title=product_title,
                amount=product_amount
            )
            last_order = orders[-1]
            last_order.products.append(product)

    return orders


def parse_excel(filename: str):
    book = load_workbook(filename=filename, data_only=True)

    worksheet: Worksheet = book["Лист_1"]

    orders = parse(worksheet)
    united_order_id = get_united_orders_id(worksheet)[0]
    united_order = UnitedOrder(united_order_id=united_order_id, orders=orders)
    return united_order.model_dump()


