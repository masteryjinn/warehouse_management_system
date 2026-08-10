from datetime import datetime

def format_date(date_str, show_time=True): # Зробимо True за замовчуванням для логів
    """Форматує рядок дати у зручний для читання формат."""
    if not date_str:
        return ""
    
    # Видаляємо зайві пробіли та замінюємо T (якщо є)
    date_str = date_str.strip().replace("T", " ")
    # Замінюємо кому (мілісекунди в логах) на крапку, щоб %f спрацював
    date_str = date_str.replace(",", ".")
    
    formats = [
        "%Y-%m-%d %H:%M:%S.%f", # З мілісекундами (2026-04-17 15:13:05.962)
        "%Y-%m-%d %H:%M:%S",    # Без мілісекунд
        "%Y-%m-%d %H:%M",       # Дата та час без секунд
        "%Y-%m-%d"              # Тільки дата
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if show_time and fmt in ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]:
                # Повертаємо формат День.Місяць.Рік Години:Хвилини
                return dt.strftime("%d.%m.%Y %H:%M:%S")
            elif show_time and fmt == "%Y-%m-%d %H:%M":
                return dt.strftime("%d.%m.%Y %H:%M")
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            continue
            
    # Якщо жоден формат не підійшов
    print(f"Invalid date format: {date_str}")
    return date_str