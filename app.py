import sys
from PySide6.QtWidgets import QApplication, QLineEdit
from PySide6.QtCore import QObject, QEvent
from ui import FlashcardApp

__version__ = "1.0.0"

MACRON_MAP = {
    "a": "ā", "e": "ē", "i": "ī", "o": "ō", "u": "ū",
    "A": "Ā", "E": "Ē", "I": "Ī", "O": "Ō", "U": "Ū",
}

class MacronInputFilter(QObject):
    """
    Dead key filter: ~ gevolgd door een klinker → macron-variant.
    Werkt op elk QLineEdit in de applicatie.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dead = False  # wachten op volgende toets na ~

    def eventFilter(self, obj, event):
        if not isinstance(obj, QLineEdit):
            return False
        if event.type() != QEvent.Type.KeyPress:
            return False

        text = event.text()

        if self._dead:
            self._dead = False
            if text in MACRON_MAP:
                # Vervang door macron-karakter
                obj.insert(MACRON_MAP[text])
                return True  # originele toets inslikken
            else:
                # Geen klinker: voer ~ en het getypte teken alsnog in
                obj.insert("~")
                if text:
                    obj.insert(text)
                return True

        if text == "~":
            self._dead = True
            return True  # ~ nog niet invoegen, wachten op volgende toets

        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    macron_filter = MacronInputFilter(app)
    app.installEventFilter(macron_filter)

    window = FlashcardApp()
    window.setWindowTitle(f"Flashcard App v{__version__}")
    window.show()
    sys.exit(app.exec())
