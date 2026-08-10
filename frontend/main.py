from PyQt6.QtWidgets import QApplication
from windows.authorization.login_window import AuthWindow
import sys

def main():
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
