from .schemas import Table


def generate_html(tables: list[Table]):
    html = """
    <!DOCTYPE HTML>
    
    <html>
        <head>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
        """
    for table in tables:
        html += f'<table class="{table.type}">'

        for i in range(len(table.data)):
            row = table.data[i]
            html += "<tr>\n"

            for j in range(len(row)):
                elem = row[j]
                if elem is None:
                    continue
                elem = elem.replace("\n", " ")
                if i == 0:
                    html += f'  <th class="{table.columns[j]}">{elem}</th>\n'
                    continue
                html += f'  <td class="{table.columns[j]}">{elem}</td>\n'

            html += "</tr>\n"

        if table.type == "user_info":
            html += "</table><br>\n"
        else:
            html += "</table>\n"

    html += "</body></html>"

    return html

