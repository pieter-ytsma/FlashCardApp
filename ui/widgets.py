from PySide6.QtWidgets import QLineEdit, QToolButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class DeletableLineEdit(QLineEdit):
    def __init__(self, text="", on_delete=None, icon_color="white", parent=None):
        super().__init__(text, parent)
        self._btn = QToolButton(self)
        self._btn.setText("×")
        self._btn.setFixedSize(28, 28)

        font = QFont(self.font())
        font.setPointSize(10)
        self._btn.setFont(font)

        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.setStyleSheet(f"""
            QToolButton {{
                background: transparent;
                color: {icon_color};
                border: none;
                font-size: 14px;
                font-weight: 600;
            }}
            QToolButton:hover {{
                color: #f87171;
                background: rgba(239,68,68,0.15);
                border-radius: 6px;
            }}
        """)
        if on_delete:
            self._btn.clicked.connect(on_delete)
        self.setStyleSheet("QLineEdit { padding-right: 36px; }")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        sz = self._btn.size()
        self._btn.move(
            self.width() - sz.width() - 4,
            (self.height() - sz.height()) // 2
        )