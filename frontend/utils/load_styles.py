def load_styles():
    return"""
            QWidget {
                background-color: #ffffff;
                color: #2c3e50;
                font-size: 14px;
            }

            QLineEdit {
                background-color: #f5f5f5;
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                color: #2c3e50;
            }

            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 12px;
                border: none;
                outline: none;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #2980b9;
            }

            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            
            QPushButton#cancel_button {
                background-color: #ecf0f1;
                color: #2c3e50;
            }

            QPushButton#cancel_button:hover {
                background-color: #d6dbdf;
            }

            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                gridline-color: #dcdcdc;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #d6eaf8;
                color: #1c2833;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                color: #2c3e50;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #dcdcdc;
            }

            QLabel {
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #3498db;
                border-radius: 4px;
                background-color: #fff;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 2px solid #2980b9;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #2980b9;
                background-color: #ecf6fc;
            }

            QLineEdit {
                background-color: #f5faff;
                padding: 8px;
                border: 1px solid #3498db;
                border-radius: 6px;
                color: #1b263b;
                font-size: 15px;
                font-weight: bold;
            }

            QLineEdit:focus {
                background-color: #e8f4fc;
                border: 1px solid #2980b9;
            }
        """

import os

def load_dialog_styles():
    # Абсолютний шлях до стрілочки
    arrow_down_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons', 'arrow_down_white_2.png')).replace('\\', '/')
    arrow_up_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons', 'arrow_up_white.png')).replace('\\', '/')
    return f"""
        QWidget {{
            background-color: #ffffff;
            color: #2c3e50;
            font-family: Arial, sans-serif;
            font-size: 14px;
        }}

        QLabel {{
            font-weight: bold;
            font-size: 16px;
            color: #1b263b;
            margin-bottom: 4px;
        }}

        QLineEdit {{
            background-color: #f5faff;
            padding: 8px;
            border: 1px solid #3498db;
            border-radius: 6px;
            color: #1b263b;
            font-size: 15px;
            font-weight: bold;
        }}

        QLineEdit:focus {{
            background-color: #e8f4fc;
            border: 1px solid #2980b9;
        }}

        QCheckBox {{
            font-size: 14px;
            color: #415a77;
            padding: 6px 0;
            outline: none;
        }}

        QPushButton {{
            background-color: #3498db;
            color: white;
            padding: 10px 12px;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            outline: none;
        }}

        QPushButton:hover {{
            background-color: #2980b9;
        }}

        QPushButton:disabled {{
            background-color: #bdc3c7;
        }}

        QPushButton#cancel_button {{
            background-color: #ecf0f1;
            color: #2c3e50;
        }}

        QPushButton#cancel_button:hover {{
            background-color: #d6dbdf;
        }}

        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid #3498db;
            border-radius: 4px;
            background-color: #fff;
        }}

        QCheckBox::indicator:checked {{
            background-color: #3498db;
            border: 2px solid #2980b9;
        }}

        QCheckBox::indicator:hover {{
            border: 2px solid #2980b9;
            background-color: #f0f0f0;
        }}

        QDateEdit {{
            background-color: #f5faff;
            padding: 6px 10px;
            border: 1px solid #3498db;
            border-radius: 6px;
            font-size: 15px;
            color: #1b263b;
            font-weight: bold;
        }}

        QDateEdit:focus {{
            background-color: #e8f4fc;
            border: 1px solid #2980b9;
        }}

        QDateEdit:disabled {{
            color: #aaa;
            background-color: #f3f3f3;
            border: 1px solid #ccc;
        }}

        QDateEdit:enabled {{
            color: #000;
            background-color: #ffffff;
            border: 1px solid #aaa;
        }}

        QDateEdit::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 1px solid #3498db;
            background-color: #3498db;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}

        QDateEdit::down-arrow {{
            image: url("{arrow_down_path}");
            width: 21px;
            height: 20px;
        }}

        QComboBox {{
            background-color: #f5faff;
            border: 1px solid #3498db;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 15px;
            color: #1b263b;
            font-weight: bold;
        }}

        QComboBox:focus {{
            border: 1px solid #2980b9;
            background-color: #e8f4fc;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            border: none;
            width: 25px;
            background-color: #3498db;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}

        QComboBox::down-arrow {{
            image: url("{arrow_down_path}");
            width: 21px;
            height: 20px;
        }}

        QListWidget {{
            background-color: #f5faff;
            border: 1px solid #3498db;
            border-radius: 6px;
            font-size: 14px;
            color: #1b263b;
            padding: 4px;
            outline: none;
        }}

        QListWidget::item {{
            padding: 8px 12px;
            border-radius: 4px;
            margin: 2px;
            font-weight: bold;
            color: #1b263b;
        }}

        QListWidget::item:hover {{
            background-color: #e8f4fc;
            color: #2980b9;
        }}

        QListWidget::item:selected {{
            background-color: #3498db;
            color: white;
        }}

        QListWidget::item:selected:active {{
            background-color: #2980b9;
        }}

        QSpinBox {{
            background-color: #f5faff;
            padding: 6px 10px;
            border: 1px solid #3498db;
            border-radius: 6px;
            font-size: 15px;
            color: #1b263b;
            font-weight: bold;
        }}
        QSpinBox:focus {{
            background-color: #e8f4fc;
            border: 1px solid #2980b9;
        }}
        QSpinBox::up-button{{
            image: url("{arrow_up_path}");
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 25px;
            background-color: #3498db;
            border-top-right-radius: 6px;
        }}

        QSpinBox::down-button{{
            image: url("{arrow_down_path}");
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 25px;
            background-color: #3498db;
            border-bottom-right-radius: 6px;
        }}
        QTextEdit {{
            background-color: #f5faff;
            padding: 8px;
            border: 1px solid #3498db;
            border-radius: 6px;
            color: #1b263b;
            font-size: 15px;
            font-weight: bold;
        }}
        QTextEdit:focus {{
            background-color: #e8f4fc;
            border: 1px solid #2980b9;
        }}
        QDateTimeEdit {{
            background-color: #f5faff;
            padding: 6px 10px;
            border: 1px solid #3498db;
            border-radius: 6px;
            font-size: 15px;
            color: #1b263b;
            font-weight: bold;
        }}
        QDateTimeEdit:focus {{
            background-color: #e8f4fc;
            border: 1px solid #2980b9;
        }}
        QDateTimeEdit::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 1px solid #3498db;
            background-color: #3498db;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}  
        QDateTimeEdit::down-arrow {{
            image: url("{arrow_down_path}");
            width: 21px;
            height: 20px;
        }}  
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            border: none;
            width: 25px;
            background-color: #3498db;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}
        QComboBox::down-arrow {{
            image: url("{arrow_down_path}");
            width: 21px;
            height: 20px;
        }}
        QComboBox{{
            background-color: #f5faff;
            border: 1px solid #3498db;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 15px;
            color: #1b263b;
            font-weight: bold;
        }}
        QSpinBox {{
            background-color: #f5faff;
            padding: 6px 10px;
            border: 1px solid #3498db;
            border-radius: 6px;
            font-size: 15px;
            color: #1b263b;
            font-weight: bold;
        }}
        QSpinBox:focus {{
            background-color: #e8f4fc;
            border: 1px solid #2980b9;      
        }}
        QSpinBox::up-button{{
            image: url("{arrow_up_path}");
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 25px;
            background-color: #3498db;
            border-top-right-radius: 6px;
        }}
        QSpinBox::down-button{{
            image: url("{arrow_down_path}");
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 25px;
            background-color: #3498db;
            border-bottom-right-radius: 6px;
        }}
        QSpinBox::disabled {{
            color: #aaa;
            background-color: #f3f3f3;
            border: 1px solid #ccc;
        }}
    """

def load_combobox_styles():
    arrow_down_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons', 'arrow_down_white_2.png')).replace('\\', '/')
    arrow_up_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons', 'arrow_up_white.png')).replace('\\', '/')
    return f"""
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            border: none;
            width: 25px;
            background-color: #3498db;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }}
        QComboBox::down-arrow {{
            image: url("{arrow_down_path}");
            width: 21px;
            height: 20px;
        }}
        QComboBox{{
            background-color: #f5faff;
            border: 1px solid #3498db;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 15px;
            color: #1b263b;
            font-weight: bold;
        }}
        """