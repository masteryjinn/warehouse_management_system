from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation

def fade_in_widget(widget):
    effect = QGraphicsOpacityEffect()
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity")
    animation.setDuration(500)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.start()
    widget._animation = animation