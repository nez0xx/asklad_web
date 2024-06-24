from openpyxl.worksheet.worksheet import Worksheet


def find(sheet: Worksheet, value, method: str = "equal", start: int = 1, end: int = 10000) -> dict | None:

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




