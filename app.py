import sys
from PySide6.QtWidgets import QApplication
from ui import FlashcardApp

__version__ = "1.0.0"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlashcardApp()
    window.setWindowTitle(f"Flashcard App v{__version__}")
    window.show()
    sys.exit(app.exec())