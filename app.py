import sys
from PySide6.QtWidgets import QApplication
from ui import FlashcardApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.show()
    sys.exit(app.exec())
