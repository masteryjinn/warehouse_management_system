from io import BytesIO
from decimal import Decimal, InvalidOperation
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth

def safe_decimal(value):
    if value is None:
        return Decimal(0)
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    value = str(value).strip().replace(',', '.')
    value = ''.join(ch for ch in value if (ch.isdigit() or ch == '.'))
    try:
        return Decimal(value)
    except InvalidOperation:
        return Decimal(0)

def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

def split_text(text, font_name, font_size, max_width):
    if not text:
        return [""]

    words = []
    for w in text.split(" "):
        parts = w.split("-")
        for i, p in enumerate(parts):
            if p:
                words.append(p + ("-" if i < len(parts)-1 else ""))
            else:
                words.append("-")

    lines, current_line = [], ""

    for word in words:
        test_line = (current_line + " " + word).strip()
        if stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = ""
            if stringWidth(word, font_name, font_size) <= max_width:
                current_line = word
            else:
                cut_word = ""
                for ch in word:
                    if stringWidth(cut_word + ch, font_name, font_size) > max_width:
                        lines.append(cut_word)
                        cut_word = ch
                    else:
                        cut_word += ch
                if cut_word:
                    current_line = cut_word

    if current_line:
        lines.append(current_line)

    return lines

def generate_invoice_pdf(order_id: int, order_data: list):
    if not order_data:
        return None

    pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSans.ttf'))
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Беремо дані клієнта та дату з першого рядка
    info = order_data[0]
    cust_name = info.get('customer_name', 'Не вказано')
    cust_phone = info.get('phone', '-')
    cust_addr = info.get('address', '-')
    cust_email = info.get('email', '-')
    order_date = info.get('order_date')
    date_str = order_date.strftime("%d.%m.%Y %H:%M") if order_date else "-"

    # Колонки: Назва, К-ть, Од, Ціна, Сума, Категорія
    x_positions = [50, 240, 290, 340, 420, 500]
    col_widths = [190, 50, 50, 80, 80, 80]
    headers = ["Назва", "К-ть", "Од.", "Ціна", "Сума", "Категорія"]
    center_cols = [False, True, True, True, True, False]
    
    line_height = 14
    page_margin = 50
    padding_x = 3
    padding_y = 5

    def draw_table_header(y_pos):
        c.setFont("DejaVu", 10)
        c.setLineWidth(1.2)
        # Верхня лінія
        c.line(x_positions[0], y_pos, x_positions[0] + sum(col_widths), y_pos)
        
        # Сірий фон заголовка
        c.setFillColorRGB(0.95, 0.95, 0.95)
        c.rect(x_positions[0], y_pos - 20, sum(col_widths), 20, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)

        for i, h in enumerate(headers):
            if center_cols[i]:
                tw = stringWidth(h, 'DejaVu', 10)
                c.drawString(x_positions[i] + (col_widths[i]-tw)/2, y_pos - 14, h)
            else:
                c.drawString(x_positions[i] + padding_x, y_pos - 14, h)
        
        # Нижня лінія заголовка
        y_bottom = y_pos - 20
        c.setLineWidth(1)
        c.line(x_positions[0], y_bottom, x_positions[0] + sum(col_widths), y_bottom)
        return y_bottom

    # --- ШАПКА ДОКУМЕНТА ---
    y = height - 50
    c.setFont("DejaVu", 18)
    c.drawString(50, y, f"НАКЛАДНА №{order_id}")
    
    c.setFont("DejaVu", 10)
    c.drawRightString(width - 50, y, f"Дата: {date_str}")
    
    y -= 15
    c.setLineWidth(1)
    c.line(50, y, width - 50, y)
    
    y -= 25
    c.setFont("DejaVu", 11)
    c.drawString(50, y, f"Отримувач: {cust_name}")
    y -= 15
    c.setFont("DejaVu", 10)
    c.drawString(50, y, f"Телефон: {cust_phone} | Email: {cust_email}")
    y -= 15
    
    # Обробка довгої адреси (якщо адреса дуже довга, вона не залізе на таблицю)
    addr_lines = split_text(f"Адреса: {cust_addr}", "DejaVu", 10, width - 100)
    for line in addr_lines:
        c.drawString(50, y, line)
        y -= 12
    
    y -= 15
    y = draw_table_header(y)

    total_sum = Decimal(0)

    # --- ТІЛО ТАБЛИЦІ ---
    for row in order_data:
        p_name = str(row.get('product_name', '-'))
        qty = safe_int(row.get('quantity', 0))
        unit = str(row.get('unit', '-'))
        price = safe_decimal(row.get('price', 0))
        cat = str(row.get('category_name', '-'))
        
        line_total = qty * price
        total_sum += line_total

        values = [p_name, str(qty), unit, f"{price:.2f}", f"{line_total:.2f}", cat]
        
        # Розрахунок висоти рядка
        cell_lines = []
        max_lines_in_row = 1
        for i, val in enumerate(values):
            lines = split_text(val, 'DejaVu', 9, col_widths[i] - 2*padding_x)
            cell_lines.append(lines)
            max_lines_in_row = max(max_lines_in_row, len(lines))

        row_height = max_lines_in_row * line_height + 2 * padding_y

        # Перевірка на нову сторінку
        if y - row_height < page_margin + 60:
            c.showPage()
            y = height - 50
            y = draw_table_header(y)

        y_top = y
        y_bottom = y - row_height

        # Малюємо текст у клітинках
        c.setFont("DejaVu", 9)
        for i, lines in enumerate(cell_lines):
            # Центруємо текст вертикально всередині клітинки
            text_block_height = len(lines) * line_height
            start_y = y_top - padding_y - line_height + 2 # базова лінія першого рядка
            
            for j, line in enumerate(lines):
                current_line_y = start_y - (j * line_height)
                if center_cols[i]:
                    tw = stringWidth(line, 'DejaVu', 9)
                    c.drawString(x_positions[i] + (col_widths[i]-tw)/2, current_line_y, line)
                else:
                    c.drawString(x_positions[i] + padding_x, current_line_y, line)

        # Малюємо рамки
        curr_x = x_positions[0]
        for w in col_widths:
            c.rect(curr_x, y_bottom, w, row_height, fill=0, stroke=1)
            curr_x += w
        
        y = y_bottom

    # --- ПІДСУМОК ---
    y -= 30
    if y < page_margin + 40:
        c.showPage()
        y = height - 50
        
    c.setFont("DejaVu", 12)
    # ТУТ БУЛА ПОМИЛКА: final_text змінено на final_sum_str
    final_sum_str = f"ЗАГАЛЬНА СУМА: {total_sum:.2f} грн"
    tw = stringWidth(final_sum_str, "DejaVu", 12)
    c.drawString(x_positions[0] + sum(col_widths) - tw, y, final_sum_str)

    # --- БЛОК ПІДПИСІВ ---
    y -= 70
    if y < page_margin:
        c.showPage()
        y = height - 80

    c.setFont("DejaVu", 10)
    c.drawString(50, y, "Відпустив (склад): ____________________")
    c.setFont("DejaVu", 7)
    c.drawString(165, y - 10, "(підпис, ПІБ)")
    
    c.setFont("DejaVu", 10)
    c.drawString(width - 250, y, "Прийняв (клієнт): ____________________")
    c.setFont("DejaVu", 7)
    c.drawString(width - 135, y - 10, "(підпис, ПІБ)")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer