from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime

class ReportChartDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📈 Аналітика виторгу")
        self.resize(900, 600)
        
        # Перетворюємо дати в об'єкти datetime для правильного сортування та відображення
        self.data = sorted(data, key=lambda x: x['date']) 
        self.chart_type = 'line'

        self.init_ui()
        self.draw_chart()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Верхня панель керування
        controls_layout = QHBoxLayout()
        
        label = QLabel("Тип візуалізації:")
        label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Лінійний графік", "Стовпчиковий графік"])
        self.combo_box.setFixedWidth(200)
        self.combo_box.currentTextChanged.connect(self.update_chart)

        controls_layout.addWidget(label)
        controls_layout.addWidget(self.combo_box)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)

        # Створення полотна Matplotlib
        # Встановлюємо колір фону, що пасує до твого вікна
        self.figure = Figure(figsize=(8, 5), facecolor='#ffffff')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def draw_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Підготовка даних
        dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in self.data]
        revenues = [float(item['total_revenue']) for item in self.data]

        if self.chart_type == 'line':
            # Стильна лінія з градієнтом або маркерами
            ax.plot(dates, revenues, marker='o', linestyle='-', linewidth=2.5, 
                    color='#3498db', markersize=6, markerfacecolor='#2980b9', 
                    label='Виторг за день')
            # Додаємо легку залівку під графіком
            ax.fill_between(dates, revenues, color='#3498db', alpha=0.1)
        
        elif self.chart_type == 'bar':
            ax.bar(dates, revenues, color='#5dade2', alpha=0.8, edgecolor='#2980b9', label='Виторг за день')

        # Форматування осей
        ax.set_title("Динаміка виторгу по днях", fontsize=14, pad=20, fontweight='bold', color='#2c3e50')
        ax.set_ylabel("Сума (грн)", fontsize=11, fontweight='bold')
        
        # Налаштування сітки (робимо її ледь помітною)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Розумне відображення дат на осі X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m')) # Формат "День.Місяць"
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        self.figure.autofmt_xdate() # Автоматичний нахил дат
        
        ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

    def update_chart(self, text):
        self.chart_type = 'line' if text == "Лінійний графік" else 'bar'
        self.draw_chart()