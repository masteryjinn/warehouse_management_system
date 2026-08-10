from PyQt6.QtCore import QObject, pyqtSignal

class AppSignals(QObject):
    _instance = None
    logout_requested = pyqtSignal()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AppSignals()
        return cls._instance
