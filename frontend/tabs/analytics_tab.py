from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, 
                             QDateEdit, QPushButton, QTabWidget, QGroupBox,
                                QGridLayout, QTableWidget, QTableWidgetItem,
                                QTextEdit, QMessageBox, QHeaderView)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor
from datetime import datetime

from services.api_client import ApiClient

from config.config import API_URL
from utils import load_styles

# Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

METRIC_OPTIONS_DICT = {
    "abc_analysis": "ABC-аналіз товарів",
    "xyz_analysis": "XYZ-аналіз (стабільність попиту)",
    "abc_xyz_matrix": "ABC-XYZ матриця",
    "turnover": "Оборотність товарів",
    "critical_stock": "Критичні залишки",
    "sales_trend": "Тренд продажів",
    "write_offs": "Аналіз списань",
    "warehouse_efficiency": "Ефективність складу"
}

class AnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_styles())
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("📊 ПРОФЕСІЙНА АНАЛІТИКА СКЛАДУ")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Верхня панель: вибір метрики та періоду
        controls_group = QGroupBox("Параметри аналізу")
        controls_layout = QGridLayout()

        # Метрика
        controls_layout.addWidget(QLabel("Тип аналізу:"), 0, 0)
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(METRIC_OPTIONS_DICT.values())
        self.metric_combo.currentIndexChanged.connect(self.on_metric_changed)
        controls_layout.addWidget(self.metric_combo, 0, 1, 1, 2)

        # Період
        controls_layout.addWidget(QLabel("Період з:"), 1, 0)
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-3))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        controls_layout.addWidget(self.start_date, 1, 1)

        controls_layout.addWidget(QLabel("до:"), 1, 2)
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        controls_layout.addWidget(self.end_date, 1, 3)

        # Кнопка завантаження
        self.load_button = QPushButton("🔄 Завантажити аналіз")
        self.load_button.clicked.connect(self.load_analysis)
        self.load_button.setStyleSheet("padding: 8px; font-weight: bold;")
        controls_layout.addWidget(self.load_button, 2, 0, 1, 4)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Tabs для різних візуалізацій
        self.tabs = QTabWidget()
        
        # Tab 1: Графік
        self.chart_widget = QWidget()
        chart_layout = QVBoxLayout()
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        self.chart_widget.setLayout(chart_layout)
        self.tabs.addTab(self.chart_widget, "📈 Графік")

        # Tab 2: Таблиця
        self.table_widget = QWidget()
        table_layout = QVBoxLayout()
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.data_table)
        self.table_widget.setLayout(table_layout)
        self.tabs.addTab(self.table_widget, "📋 Таблиця даних")

        # Tab 3: Рекомендації
        self.recommendations_widget = QWidget()
        rec_layout = QVBoxLayout()
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        rec_layout.addWidget(self.recommendations_text)
        self.recommendations_widget.setLayout(rec_layout)
        self.tabs.addTab(self.recommendations_widget, "💡 Рекомендації")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def on_metric_changed(self):
        """Змінює доступність періоду для деяких метрик."""
        metric_name = self.metric_combo.currentText()
        metric = {v: k for k, v in METRIC_OPTIONS_DICT.items()}.get(metric_name)
        
        # Для деяких аналізів період не потрібен
        period_needed = metric not in ["critical_stock", "warehouse_efficiency"]
        self.start_date.setEnabled(period_needed)
        self.end_date.setEnabled(period_needed)

    def load_analysis(self):
        """Завантажує дані аналітики з API."""
        metric_name = self.metric_combo.currentText()
        metric = {v: k for k, v in METRIC_OPTIONS_DICT.items()}.get(metric_name, "abc_analysis")

        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        params={"metric": metric, "start_date": start, "end_date": end}
        result = ApiClient.get(self, f"{API_URL}/analytics/advanced", params=params)
        if result:
            if metric == "warehouse_efficiency":
                if not result.get("metrics"):
                    QMessageBox.information(self, "Інформація", "Дані відсутні.")
                    return
            else:
                if not result.get("values"):
                    QMessageBox.information(self, "Інформація", "Дані відсутні за обраний період.")
                    return

            # Візуалізація залежно від типу аналізу
            if metric == "abc_analysis":
                self.visualize_abc_analysis(result)
            elif metric == "xyz_analysis":
                self.visualize_xyz_analysis(result)
            elif metric == "abc_xyz_matrix":
                self.visualize_abc_xyz_matrix(result)
            elif metric == "turnover":
                self.visualize_turnover(result)
            elif metric == "critical_stock":
                self.visualize_critical_stock(result)
            elif metric == "sales_trend":
                self.visualize_sales_trend(result)
            elif metric == "write_offs":
                self.visualize_write_offs(result)
            elif metric == "warehouse_efficiency":
                self.visualize_warehouse_efficiency(result)

    def visualize_abc_analysis(self, data):
        """ABC-аналіз: класифікація товарів за оборотом."""
        values = data["values"]
        
        # Графік
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Групування за класами
        classes = {'A': [], 'B': [], 'C': []}
        for item in values:
            classes[item['abc_class']].append(item)
        
        # Кругова діаграма розподілу
        sizes = [len(classes['A']), len(classes['B']), len(classes['C'])]
        labels = [f"Клас A ({sizes[0]} товарів)\n80% обороту", 
                  f"Клас B ({sizes[1]} товарів)\n15% обороту", 
                  f"Клас C ({sizes[2]} товарів)\n5% обороту"]
        colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
        explode = (0.1, 0.05, 0)
        
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax.set_title("ABC-аналіз товарів", fontsize=14, fontweight='bold', pad=20)
        
        self.canvas.draw()
        
        # Таблиця
        self.populate_table(values, [
            "ID", "Назва", "Категорія", "Клас", "Оборот (грн)", 
            "% обороту", "Кумулятивний %", "Продано (од.)"
        ], lambda item: [
            str(item['product_id']),
            item['name'],
            item.get('category', 'N/A'),
            item['abc_class'],
            f"{item['revenue']:,.2f}",
            f"{item['revenue_percentage']:.2f}%",
            f"{item['cumulative_percentage']:.2f}%",
            str(item['sold_quantity'])
        ], abc_class_column=3)
        
        # Рекомендації
        self.generate_abc_recommendations(classes)

    def visualize_xyz_analysis(self, data):
        """XYZ-аналіз: стабільність попиту."""
        values = data["values"]
        
        # Графік
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Групування за класами
        classes = {'X': [], 'Y': [], 'Z': []}
        for item in values:
            classes[item['xyz_class']].append(item)
        
        # Стовпчикова діаграма
        class_names = ['X (стабільний)', 'Y (змінний)', 'Z (нестабільний)']
        counts = [len(classes['X']), len(classes['Y']), len(classes['Z'])]
        colors = ['#4ecdc4', '#f7dc6f', '#e74c3c']
        
        bars = ax.bar(class_names, counts, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Кількість товарів', fontsize=12)
        ax.set_title('XYZ-аналіз: стабільність попиту', fontsize=14, fontweight='bold')
        
        # Додаємо значення на стовпчики
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(count)}', ha='center', va='bottom', fontweight='bold')
        
        self.canvas.draw()
        
        # Таблиця
        self.populate_table(values, [
            "ID", "Назва", "Клас XYZ", "Коеф. варіації (%)", 
            "Сер. продаж", "Станд. відхилення", "Стабільність"
        ], lambda item: [
            str(item['product_id']),
            item['name'],
            item['xyz_class'],
            f"{item['coefficient_variation']:.2f}%",
            f"{item['avg_sales']:.2f}",
            f"{item['std_deviation']:.2f}",
            self.get_stability_text(item['xyz_class'])
        ])
        
        # Рекомендації
        self.generate_xyz_recommendations(classes)

    def visualize_abc_xyz_matrix(self, data):
        """ABC-XYZ матриця: комбінований аналіз."""
        values = data["values"]
        
        # Графік - матриця
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Створюємо матрицю 3x3
        matrix = {}
        for abc in ['A', 'B', 'C']:
            for xyz in ['X', 'Y', 'Z']:
                key = f"{abc}{xyz}"
                matrix[key] = [item for item in values 
                              if item['abc_class'] == abc and item['xyz_class'] == xyz]
        
        # Малюємо матрицю
        for i, abc in enumerate(['A', 'B', 'C']):
            for j, xyz in enumerate(['X', 'Y', 'Z']):
                key = f"{abc}{xyz}"
                count = len(matrix[key])
                
                # Колір залежно від пріоритету
                priority_colors = {
                    'AX': '#00b894', 'AY': '#00cec9', 'AZ': '#fdcb6e',
                    'BX': '#74b9ff', 'BY': '#a29bfe', 'BZ': '#fab1a0',
                    'CX': '#dfe6e9', 'CY': '#b2bec3', 'CZ': '#636e72'
                }
                color = priority_colors.get(key, '#ffffff')
                
                rect = Rectangle((j, 2-i), 1, 1, facecolor=color, edgecolor='black', linewidth=2)
                ax.add_patch(rect)
                
                # Текст
                ax.text(j+0.5, 2-i+0.6, key, ha='center', va='center', 
                       fontsize=16, fontweight='bold')
                ax.text(j+0.5, 2-i+0.3, f'{count} товарів', ha='center', va='center',
                       fontsize=10)
        
        ax.set_xlim(0, 3)
        ax.set_ylim(0, 3)
        ax.set_xticks([0.5, 1.5, 2.5])
        ax.set_yticks([0.5, 1.5, 2.5])
        ax.set_xticklabels(['X\n(стабільний)', 'Y\n(змінний)', 'Z\n(нестабільний)'])
        ax.set_yticklabels(['C\n(5% обороту)', 'B\n(15% обороту)', 'A\n(80% обороту)'])
        ax.set_title('ABC-XYZ Матриця', fontsize=14, fontweight='bold', pad=20)
        ax.set_aspect('equal')
        
        self.canvas.draw()
        
        # Таблиця
        self.populate_table(values, [
            "ID", "Назва", "ABC", "XYZ", "Група", "Оборот", "Стабільність", "Пріоритет"
        ], lambda item: [
            str(item['product_id']),
            item['name'],
            item['abc_class'],
            item['xyz_class'],
            f"{item['abc_class']}{item['xyz_class']}",
            f"{item['revenue']:,.2f}",
            self.get_stability_text(item['xyz_class']),
            self.get_priority_text(item['abc_class'], item['xyz_class'])
        ])
        
        # Рекомендації
        self.generate_matrix_recommendations(matrix)

    def visualize_turnover(self, data):
        """Оборотність товарів."""
        values = data["values"]
        
        # Графік
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Топ-10 товарів з найкращою оборотністю
        top_items = sorted(values, key=lambda x: x['turnover_days'])[:10]
        
        names = [item['name'][:20] for item in top_items]
        days = [item['turnover_days'] for item in top_items]
        colors = ['#27ae60' if d < 30 else '#f39c12' if d < 60 else '#e74c3c' for d in days]
        
        bars = ax.barh(names, days, color=colors, edgecolor='black')
        ax.set_xlabel('Днів оборотності', fontsize=12)
        ax.set_title('Топ-10 товарів за оборотністю', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        
        # Лінії порогів
        ax.axvline(30, color='green', linestyle='--', alpha=0.7, label='Швидка (< 30 днів)')
        ax.axvline(60, color='orange', linestyle='--', alpha=0.7, label='Середня (30-60 днів)')
        ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Таблиця
        self.populate_table(values, [
            "ID", "Назва", "Днів оборотності", "Продано", "Сер. запас", "Оцінка"
        ], lambda item: [
            str(item['product_id']),
            item['name'],
            f"{item['turnover_days']:.1f}",
            str(item['sold_quantity']),
            f"{item['avg_stock']:.1f}",
            self.get_turnover_rating(item['turnover_days'])
        ])
        
        # Рекомендації
        self.generate_turnover_recommendations(values)
        
    def visualize_critical_stock(self, data):
        """Критичні залишки."""
        values = data["values"]
        
        # Словник для перекладу статусів
        TYPE_CRYTICAL_REMAINING = {
            "CRITICAL": "Критично",
            "HIGH": "Висока",
            "MEDIUM": "Середня",
            "LOW": "Низька"
        }

        # Графік
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Топ-15 критичних товарів
        critical = sorted(values, key=lambda x: x['priority'])[:15]
        
        names = [item['name'][:25] for item in critical]
        stock = [item['current_stock'] for item in critical]
        recommended = [item['recommended_order'] for item in critical]
        
        criticality_colors = {
            'CRITICAL': '#e74c3c',
            'HIGH': '#e67e22',
            'MEDIUM': '#f39c12',
            'LOW': '#3498db'
        }
        colors = [criticality_colors.get(item['criticality'], '#95a5a6') for item in critical]
        
        x = range(len(names))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], stock, width, label='Поточний запас', 
            color=colors, edgecolor='black')
        ax.bar([i + width/2 for i in x], recommended, width, label='Рекомендовано замовити',
            color='#2ecc71', alpha=0.7, edgecolor='black')
        
        ax.set_ylabel('Кількість', fontsize=12)
        ax.set_title('Критичні залишки товарів', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Таблиця з використанням перекладу
        self.populate_table(values, [
            "ID", "Назва", "Поточний запас", "Мін. кількість", "До вичерпання (днів)",
            "Рекомендовано", "Критичність", "Вартість замовлення"
        ], lambda item: [
            str(item['product_id']),
            item['name'],
            str(item['current_stock']),
            str(item['min_quantity']),
            str(item['days_until_stockout']),
            str(item['recommended_order']),
            # ОСЬ ТУТ: беремо значення зі словника, якщо ключа немає — лишаємо як є
            TYPE_CRYTICAL_REMAINING.get(item['criticality'], item['criticality']),
            f"{item['estimated_cost']:,.2f} грн"
        ])
        
        self.generate_critical_stock_recommendations(values)

    def visualize_sales_trend(self, data):
        """Тренд продажів."""
        values = data["values"]
        
        # Графік
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        dates = [datetime.strptime(item["sale_date"], "%Y-%m-%d") for item in values]
        sales = [item["daily_revenue"] for item in values]
        
        # Лінія продажів
        line, = ax.plot(dates, sales, marker='o', linestyle='-', color='#3498db', 
                       linewidth=2, markersize=6, label='Продажі')
        
        # Ковзне середнє (7 днів)
        if len(sales) >= 7:
            moving_avg = []
            for i in range(len(sales)):
                start = max(0, i - 3)
                end = min(len(sales), i + 4)
                moving_avg.append(sum(sales[start:end]) / (end - start))
            ax.plot(dates, moving_avg, linestyle='--', color='#e74c3c', 
                   linewidth=2, label='Ковзне середнє (7 днів)')
        
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Сума продажів (грн)', fontsize=12)
        ax.set_title('Тренд продажів', fontsize=14, fontweight='bold')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.figure.autofmt_xdate(rotation=45)
        self.canvas.draw()
        
        # Таблиця
        self.populate_table(values, [
            "Дата", "Сума продажів"
        ], lambda item: [
            item["sale_date"],
            f"{item['daily_revenue']:,.2f} грн"
        ])
        
        # Рекомендації
        self.generate_sales_recommendations(values)

    def visualize_write_offs(self, data):
        """Аналіз списань."""
        values = data["values"]
        
        # Графік
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Динаміка списань
        dates = [datetime.strptime(item["write_off_date"], "%Y-%m-%d") for item in values]
        quantities = [item["total_written_off"] for item in values]
        
        ax.plot(dates, quantities, marker='o', color='#e74c3c', linewidth=2)
        ax.set_xlabel('Дата')
        ax.set_ylabel('Кількість списань')
        ax.set_title('Динаміка списань')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.grid(True, alpha=0.3)
        
        self.figure.autofmt_xdate(rotation=45)
        self.canvas.draw()
        
        # Таблиця
        self.populate_table(values, [
            "Дата", "Кількість списань"
        ], lambda item: [
            item["write_off_date"],
            str(item["total_written_off"])
        ])
        
        # Рекомендації
        self.generate_writeoffs_recommendations(values)

    def visualize_warehouse_efficiency(self, data):
        """Ефективність складу."""
        metrics = data["metrics"]
        
        # Графік - метрики
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        metric_names = ['Використання\nпростору', 'Оборотність', 'Точність\nінвентаризації', 
                       'Час обробки\nзамовлення', 'Загальна\nефективність']
        values = [
            metrics.get('space_utilization', 0),
            metrics.get('turnover_rate', 0),
            metrics.get('inventory_accuracy', 0),
            metrics.get('order_processing_speed', 0),
            metrics.get('overall_efficiency', 0)
        ]
        
        colors = ['#27ae60' if v >= 75 else '#f39c12' if v >= 50 else '#e74c3c' for v in values]
        bars = ax.bar(metric_names, values, color=colors, edgecolor='black', linewidth=2)
        
        ax.set_ylabel('Показник (%)', fontsize=12)
        ax.set_title('Ефективність складу', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.axhline(75, color='green', linestyle='--', alpha=0.5, label='Відмінно')
        ax.axhline(50, color='orange', linestyle='--', alpha=0.5, label='Задовільно')
        ax.legend()
        
        # Додаємо значення на стовпчики
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        self.canvas.draw()
        
        # Таблиця метрик
        metrics_data = [
            ["Використання простору", f"{metrics.get('space_utilization', 0):.1f}%"],
            ["Оборотність запасів", f"{metrics.get('turnover_rate', 0):.1f}%"],
            ["Точність інвентаризації", f"{metrics.get('inventory_accuracy', 0):.1f}%"],
            ["Швидкість обробки замовлень", f"{metrics.get('order_processing_speed', 0):.1f}%"],
            ["Загальна ефективність", f"{metrics.get('overall_efficiency', 0):.1f}%"]
        ]
        
        self.data_table.setRowCount(len(metrics_data))
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels(["Метрика", "Значення"])
        
        for i, row in enumerate(metrics_data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.data_table.setItem(i, j, item)
        
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Рекомендації
        self.generate_efficiency_recommendations(metrics)

    # ========== Helper методи ==========

    def populate_table(self, data, headers, row_mapper, abc_class_column=-1):
        """Заповнює таблицю даними."""
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(headers))
        self.data_table.setHorizontalHeaderLabels(headers)
        
        for i, item in enumerate(data):
            row_data = row_mapper(item)
            for j, value in enumerate(row_data):
                cell = QTableWidgetItem(str(value))
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Колір для ABC класів
                if abc_class_column >= 0 and j == abc_class_column:
                    abc_class = row_data[j]
                    if abc_class == 'A':
                        cell.setBackground(QColor(255, 107, 107, 100))
                    elif abc_class == 'B':
                        cell.setBackground(QColor(255, 217, 61, 100))
                    elif abc_class == 'C':
                        cell.setBackground(QColor(107, 207, 127, 100))
                
                self.data_table.setItem(i, j, cell)
        
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def get_stability_text(self, xyz_class):
        """Повертає опис стабільності."""
        mapping = {
            'X': 'Стабільний попит',
            'Y': 'Змінний попит',
            'Z': 'Нестабільний попит'
        }
        return mapping.get(xyz_class, 'Невідомо')

    def get_priority_text(self, abc_class, xyz_class):
        """Визначає пріоритет товару."""
        key = f"{abc_class}{xyz_class}"
        priority_map = {
            'AX': '🔴 Найвищий', 'AY': '🔴 Дуже високий', 'AZ': '🟠 Високий',
            'BX': '🟡 Середній+', 'BY': '🟡 Середній', 'BZ': '🟡 Середній-',
            'CX': '🟢 Низький', 'CY': '🟢 Дуже низький', 'CZ': '🟢 Мінімальний'}
        return priority_map.get(key, 'Невідомо')
    
    def get_turnover_rating(self, days):
        """Оцінка оборотності за днями."""
        if days < 30:
            return "Відмінно"
        elif days < 60:
            return "Добре"
        elif days < 90:
            return "Задовільно"
        else:
            return "Погано" 
        
    def generate_abc_recommendations(self, classes):
        """Генерує рекомендації для ABC-аналізу."""
        recs = []
        recs.append("Рекомендації за результатами ABC-аналізу:\n")
        recs.append(f"Клас A ({len(classes['A'])} товарів):\n"
                    "- Фокус на максимізації продажів та обслуговуванні клієнтів.\n"
                    "- Регулярний моніторинг запасів.\n")
        recs.append(f"Клас B ({len(classes['B'])} товарів):\n"
                    "- Оптимізація запасів та маркетингових зусиль.\n"
                    "- Аналіз тенденцій продажів.\n")
        recs.append(f"Клас C ({len(classes['C'])} товарів):\n"
                    "- Мінімізація запасів та витрат на обслуговування.\n"
                    "- Розглянути можливість зняття з продажу або заміни.\n")
        
        self.recommendations_text.setPlainText("".join(recs))

    def generate_xyz_recommendations(self, classes):
        """Генерує рекомендації для XYZ-аналізу."""
        recs = []
        recs.append("Рекомендації за результатами XYZ-аналізу:\n")
        recs.append(f"Клас X ({len(classes['X'])} товарів):\n"
                    "- Підтримуйте стабільний запас.\n"
                    "- Використовуйте прогнози для планування закупівель.\n")
        recs.append(f"Клас Y ({len(classes['Y'])} товарів):\n"
                    "- Аналізуйте сезонні коливання попиту.\n"
                    "- Використовуйте гнучкі стратегії управління запасами.\n")
        recs.append(f"Клас Z ({len(classes['Z'])} товарів):\n"
                    "- Мінімізуйте запаси та розгляньте альтернативні стратегії продажів.\n"
                    "- Частіше переглядайте асортимент.\n")
        
        self.recommendations_text.setPlainText("".join(recs))

    def generate_matrix_recommendations(self, matrix):
        """Генерує рекомендації для ABC-XYZ матриці."""
        recs = []
        recs.append("Рекомендації за результатами ABC-XYZ матриці:\n")
        for key, items in matrix.items():
            recs.append(f"Група {key} ({len(items)} товарів):\n")
            if key == 'AX':
                recs.append("- Максимальна увага на обслуговуванні та запасах.\n")
            elif key == 'AY':
                recs.append("- Регулярний моніторинг та адаптація запасів.\n")
            elif key == 'AZ':
                recs.append("- Мінімізація запасів, розглянути зняття з продажу.\n")
            elif key == 'BX':
                recs.append("- Оптимізація запасів, використання прогнозів.\n")
            elif key == 'BY':
                recs.append("- Аналіз тенденцій, гнучке управління запасами.\n")
            elif key == 'BZ':
                recs.append("- Мінімізація запасів, частіший перегляд асортименту.\n")
            elif key == 'CX':
                recs.append("- Мінімальні запаси, розглянути альтернативні стратегії продажів.\n")
            elif key == 'CY':
                recs.append("- Розглянути зняття з продажу або заміну товарів.\n")
            elif key == 'CZ':
                recs.append("- Максимальна мінімізація запасів, можливе зняття з продажу.\n")
        
        self.recommendations_text.setPlainText("".join(recs))

    def generate_turnover_recommendations(self, values):
        """Генерує рекомендації для аналізу оборотності."""
        recs = []
        recs.append("Рекомендації за результатами аналізу оборотності:\n")
        recs.append("- Товари з швидкою оборотністю (менше 30 днів) слід підтримувати в наявності.\n")
        recs.append("- Товари зі середньою оборотністю (30-60 днів) потребують оптимізації запасів.\n")
        recs.append("- Товари з повільною оборотністю (більше 60 днів) слід розглянути для зняття з продажу або заміни.\n")
        
        self.recommendations_text.setPlainText("".join(recs))
    
    def generate_critical_stock_recommendations(self, values):
        """Генерує рекомендації для критичних залишків."""
        recs = []
        recs.append("Рекомендації за результатами аналізу критичних залишків:\n")
        recs.append("- Пріоритетно замовляйте товари з високою та критичною критичністю.\n")
        recs.append("- Регулярно переглядайте мінімальні запаси та адаптуйте їх відповідно до попиту.\n")
        recs.append("- Використовуйте прогнози продажів для планування закупівель.\n")
        
        self.recommendations_text.setPlainText("".join(recs))
    
    def generate_sales_recommendations(self, values):
        """Генерує рекомендації для тренду продажів."""
        recs = []
        recs.append("Рекомендації за результатами аналізу тренду продажів:\n")
        recs.append("- Використовуйте виявлені тренди для планування маркетингових кампаній.\n")
        recs.append("- Адаптуйте запаси відповідно до сезонних коливань попиту.\n")
        recs.append("- Розгляньте впровадження акцій у періоди спадів продажів.\n")
        
        self.recommendations_text.setPlainText("".join(recs))

    def generate_writeoffs_recommendations(self, values):
        """Генерує рекомендації для аналізу списань."""
        recs = []
        recs.append("Рекомендації за результатами аналізу списань:\n")
        recs.append("- Визначте основні причини списань та розробіть стратегії їх зменшення.\n")
        recs.append("- Оптимізуйте управління запасами для зниження ризику псування товарів.\n")
        recs.append("- Проводьте регулярні інвентаризації для виявлення проблемних товарів.\n")
        
        self.recommendations_text.setPlainText("".join(recs))
    
    def generate_efficiency_recommendations(self, metrics):
        """Генерує рекомендації для ефективності складу."""
        recs = []
        recs.append("Рекомендації за результатами аналізу ефективності складу:\n")
        if metrics.get('space_utilization', 0) < 75:
            recs.append("- Оптимізуйте використання простору для збільшення ємності складу.\n")
        if metrics.get('turnover_rate', 0) < 75:
            recs.append("- Підвищуйте оборотність запасів через кращий менеджмент запасів.\n")
        if metrics.get('inventory_accuracy', 0) < 75:
            recs.append("- Покращуйте точність інвентаризації через впровадження сучасних технологій.\n")
        if metrics.get('order_processing_speed', 0) < 75:
            recs.append("- Скорочуйте час обробки замовлень через оптимізацію процесів.\n")
        
        recs.append("- Регулярно переглядайте та вдосконалюйте операційні процеси на складі.\n")
        
        self.recommendations_text.setPlainText("".join(recs))
        