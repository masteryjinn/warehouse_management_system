from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton

def show_scrollable_summary(self, title: str, summary_text: str, width=500, height=400):
    """Універсальне вікно з прокручуваним текстом"""
    dialog = QDialog(self)
    dialog.setWindowTitle(title)
    dialog.resize(width, height)

    layout = QVBoxLayout(dialog)

    text_edit = QTextEdit(dialog)
    text_edit.setReadOnly(True)
    text_edit.setText(summary_text)
    layout.addWidget(text_edit)

    ok_button = QPushButton("Закрити", dialog)
    ok_button.clicked.connect(dialog.accept)
    layout.addWidget(ok_button)

    dialog.exec()
