import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class FlashcardApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Flashcard App")
        self.resize(600, 400)

        layout = QVBoxLayout()

        label = QLabel("Flashcard App is running.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px;")

        layout.addWidget(label)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec())
