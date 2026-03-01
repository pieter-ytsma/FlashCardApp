from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QFileDialog,
    QDialog, QDialogButtonBox, QScrollArea, QToolButton,
)

import random
from pathlib import Path
from storage import save_deck, load_deck
from PySide6.QtCore import Qt, QSize, QSettings
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from helpers import start_card, check_answer
from PySide6.QtGui import QIcon

from .resources import (
    TRANSLATIONS,
    T,
    STYLESHEET_DARK,
    STYLESHEET_LIGHT,
    STYLESHEET,
    MAX_SLOTS,
)

from .widgets import DeletableLineEdit
from .dialogs.flashcard import FlashcardDialog
from .dialogs.practice import PracticeDialog
from .dialogs.edit_cards import EditCardsDialog
from .dialogs.add_card import AddCardDialog

class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icon.ico"))

        self.current_deck = None
        self.cards = []
        self.deck_path = None
        self._dirty = False
        self._loaded_deck_names = None  # lijst van namen bij meerdere geladen decks

        self.setup_ui()
        self.update_ui_for_no_deck()
        self._load_settings()

    def setup_ui(self):
        self.setWindowTitle("Flashcard App")
        self.resize(600, 300)
        self.setStyleSheet(STYLESHEET)

        # ===== MENU =====
        self.statusBar()  # activeer statusbalk
        self.menu = self.menuBar()
        self.deck_menu = self.menu.addMenu(T["menu_deck"])

        self.new_action = self.deck_menu.addAction(T["menu_new_deck"])
        self.new_action.triggered.connect(self.create_new_deck)
        self.new_action.setStatusTip("Ctrl+N")

        self.open_action = self.deck_menu.addAction(T["menu_load_deck"])
        self.open_action.triggered.connect(self.load_deck_dialog)
        self.open_action.setStatusTip("Ctrl+L")

        self.save_action = self.deck_menu.addAction(T["menu_save_deck"])
        self.save_action.triggered.connect(self.save_current_deck)
        self.save_action.setStatusTip("Ctrl+S")

        self.options_menu = self.menu.addMenu(T["menu_options"])
        self.dark_theme_action = self.options_menu.addAction(T["menu_dark_theme"])
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.setChecked(True)
        self.dark_theme_action.triggered.connect(self.toggle_theme)
        self.dark_theme_action.setStatusTip("Ctrl+D")
        self.repeat_action = self.options_menu.addAction(T["menu_repeat"])
        self.repeat_action.setCheckable(True)
        self.repeat_action.setChecked(True)
        self.repeat_action.setStatusTip("Ctrl+R")
        self.flip_cards_action = self.options_menu.addAction(T["menu_flip_cards"])
        self.flip_cards_action.setCheckable(True)
        self.flip_cards_action.setChecked(False)
        self.flip_cards_action.setStatusTip("Ctrl+F")

        self.lang_menu = self.menu.addMenu(T["menu_language"])
        self.lang_nl_action = self.lang_menu.addAction("Nederlands")
        self.lang_nl_action.setCheckable(True)
        self.lang_nl_action.setChecked(True)
        self.lang_nl_action.setStatusTip("Ctrl+1")
        self.lang_en_action = self.lang_menu.addAction("English")
        self.lang_en_action.setCheckable(True)
        self.lang_en_action.setStatusTip("Ctrl+2")
        self.lang_nl_action.triggered.connect(lambda: self.set_language("nl"))
        self.lang_en_action.triggered.connect(lambda: self.set_language("en"))

        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.create_new_deck)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(self.load_deck_dialog)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_current_deck)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self.dark_theme_action.trigger)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.repeat_action.trigger)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.flip_cards_action.trigger)
        QShortcut(QKeySequence("Ctrl+1"), self).activated.connect(lambda: self.set_language("nl"))
        QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(lambda: self.set_language("en"))

        # ===== LAYOUT =====
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)

        self.deck_label = QLabel(T["no_deck"])
        self.deck_label.setObjectName("DeckLabel")
        self.deck_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.deck_label)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.add_card_button = QPushButton(T["new_card"] + "  (N)")
        self.add_card_button.clicked.connect(self.add_card)
        self.add_card_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(self.add_card_button)

        self.edit_cards_button = QPushButton(T["edit_cards"] + "  (E)")
        self.edit_cards_button.clicked.connect(self.edit_cards)
        self.edit_cards_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(self.edit_cards_button)

        left_layout.addStretch()

        self.flashcard_button = QPushButton(T["flashcard"] + "  ↵")
        self.flashcard_button.clicked.connect(self.start_flashcard)
        self.flashcard_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        right_layout.addWidget(self.flashcard_button)

        self.practice_button = QPushButton(T["practice"] + "  ␣")
        self.practice_button.clicked.connect(self.start_practice)
        self.practice_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        right_layout.addWidget(self.practice_button)

        right_layout.addStretch()

        bottom_layout.addLayout(left_layout, 1)
        bottom_layout.addLayout(right_layout, 1)

        main_layout.addLayout(bottom_layout)

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def set_language(self, lang: str):
        global T
        T = TRANSLATIONS[lang]
        self.lang_nl_action.setChecked(lang == "nl")
        self.lang_en_action.setChecked(lang == "en")

        # Update menu teksten
        self.deck_menu.setTitle(T["menu_deck"])
        self.new_action.setText(T["menu_new_deck"])
        self.open_action.setText(T["menu_load_deck"])
        self.save_action.setText(T["menu_save_deck"])
        self.options_menu.setTitle(T["menu_options"])
        self.dark_theme_action.setText(T["menu_dark_theme"])
        self.repeat_action.setText(T["menu_repeat"])
        self.flip_cards_action.setText(T["menu_flip_cards"])
        self.lang_menu.setTitle(T["menu_language"])

        # Update knoppen
        self.add_card_button.setText(T["new_card"] + "  (N)")
        self.edit_cards_button.setText(T["edit_cards"] + "  (E)")
        self.flashcard_button.setText(T["flashcard"] + "  ↵")
        self.practice_button.setText(T["practice"] + "  ␣")

        # Update deck label
        if not self.current_deck:
            self.deck_label.setText(T["no_deck"])
        self._update_title()

    def toggle_theme(self):
        if self.dark_theme_action.isChecked():
            self.setStyleSheet(STYLESHEET_DARK)
        else:
            self.setStyleSheet(STYLESHEET_LIGHT)

    def update_ui_for_no_deck(self):
        self.deck_label.setText(T["no_deck"])
        self.setWindowTitle("Flashcard App")
        self.save_action.setEnabled(False)
        self.practice_button.setDisabled(True)
        self.flashcard_button.setDisabled(True)
        self.add_card_button.setDisabled(True)
        self.edit_cards_button.setDisabled(True)

    def update_ui_for_unsaved_deck(self):
        self.practice_button.setDisabled(True)
        self.flashcard_button.setDisabled(True)
        self.add_card_button.setDisabled(False)
        self.edit_cards_button.setDisabled(False)
        self.save_action.setEnabled(True)

    def update_ui_for_saved_deck(self):
        has_cards = bool(self.cards)

        self.practice_button.setDisabled(not has_cards)
        self.flashcard_button.setDisabled(not has_cards)
        self.add_card_button.setDisabled(False)
        self.edit_cards_button.setDisabled(False)
        self.save_action.setEnabled(True)

    def _save_settings(self):
        s = QSettings("FlashcardApp", "FlashcardApp")
        s.setValue("dark_theme", self.dark_theme_action.isChecked())
        s.setValue("repeat_incorrect", self.repeat_action.isChecked())
        s.setValue("flip_cards", self.flip_cards_action.isChecked())
        lang = "nl" if self.lang_nl_action.isChecked() else "en"
        s.setValue("language", lang)

    def _load_settings(self):
        s = QSettings("FlashcardApp", "FlashcardApp")
        dark = s.value("dark_theme", True, type=bool)
        repeat = s.value("repeat_incorrect", True, type=bool)
        flip = s.value("flip_cards", False, type=bool)
        lang = s.value("language", "nl", type=str)

        self.dark_theme_action.setChecked(dark)
        self.repeat_action.setChecked(repeat)
        self.flip_cards_action.setChecked(flip)
        self.toggle_theme()
        self.set_language(lang)

    def _update_title(self):
        if self.current_deck:
            if self._loaded_deck_names:
                # Meerdere decks samengevoegd
                name = " + ".join(self._loaded_deck_names)
                short_name = f"{len(self._loaded_deck_names)} decks"
            elif self.deck_path:
                name = Path(self.deck_path).stem
                short_name = name
            else:
                name = self.current_deck["name"]
                short_name = name
            dirty = " *" if self._dirty else ""
            self.setWindowTitle(f"Flashcard App - {name}{dirty}")
            self.deck_label.setText(short_name[:1].upper() + short_name[1:] if short_name else short_name)
        else:
            self.setWindowTitle("Flashcard App")
            self.deck_label.setText(T["no_deck"])

    def set_active_deck(self, deck: dict):
        self.current_deck = deck
        self.cards = deck["cards"]
        self.deck_path = None
        self._dirty = True
        self._loaded_deck_names = None
        self._update_title()
        self.update_ui_for_unsaved_deck()

    def _confirm_discard(self) -> bool:
        """
        Toont een waarschuwing als er niet-opgeslagen wijzigingen zijn.
        Geeft True terug als doorgaan veilig is (opgeslagen of bewust genegeerd),
        False als de gebruiker heeft geannuleerd.
        """
        if not (self._dirty and self.current_deck):
            return True

        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle(T["unsaved_warning_title"])
        msg.setText(T["unsaved_warning_text"])
        save_btn = msg.addButton(T["unsaved_save"], QMessageBox.ButtonRole.AcceptRole)
        discard_btn = msg.addButton(T["unsaved_discard"], QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = msg.addButton(T["unsaved_cancel"], QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(cancel_btn)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked == save_btn:
            self.save_current_deck()
            return True
        elif clicked == discard_btn:
            return True
        else:
            return False

    def create_new_deck(self):
        if not self._confirm_discard():
            return
        deck = {"name": T["new_deck_name"], "cards": []}
        self.set_active_deck(deck)

    def save_current_deck(self):
        if not self.current_deck:
            return

        # Bewuste keuze: een leeg deck (0 kaarten) mag worden opgeslagen.
        # Gebruik case: deck aanmaken en later kaarten toevoegen.

        if not self.deck_path:
            filepath, _ = QFileDialog.getSaveFileName(
                self, T["save_dialog"], "", "Deck files (*.json)"
            )
            if not filepath:
                return
            if not filepath.lower().endswith(".json"):
                filepath += ".json"
            self.deck_path = filepath

        save_deck(self.current_deck, self.deck_path)
        self._dirty = False
        self.update_ui_for_saved_deck()
        self._update_title()
        name = Path(self.deck_path).stem
        self.statusBar().showMessage(T["deck_saved"].format(name=name), 3000)

    def load_deck_dialog(self):
        if not self._confirm_discard():
            return

        filepaths, _ = QFileDialog.getOpenFileNames(
            self, T["load_dialog"], "", "Deck files (*.json)"
        )
        if not filepaths:
            return

        loaded_decks = []
        for filepath in filepaths:
            try:
                deck = load_deck(filepath)
                loaded_decks.append((filepath, deck))
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, T["load_error"], f"{Path(filepath).name}: {e}")
                return

        if len(loaded_decks) == 1:
            filepath, deck = loaded_decks[0]
            self.deck_path = filepath
            self.current_deck = deck
            self._loaded_deck_names = None
        else:
            # Meerdere decks: kaarten samenvoegen
            merged_cards = []
            for _, deck in loaded_decks:
                merged_cards.extend(deck["cards"])
            names = [Path(fp).stem for fp, _ in loaded_decks]
            merged_name = ", ".join(names)
            self.current_deck = {"name": merged_name, "cards": merged_cards}
            self.deck_path = None
            self._loaded_deck_names = names

        self.cards = self.current_deck["cards"]
        self._dirty = False
        self._update_title()
        self.update_ui_for_saved_deck()

        if self._loaded_deck_names:
            count = len(self._loaded_deck_names)
            total = len(self.cards)
            self.statusBar().showMessage(
                T.get("decks_merged", "{count} decks geladen, {total} kaarten totaal").format(
                    count=count, total=total
                ),
                4000,
            )

    def add_card(self):
        if not self.current_deck:
            return

        dialog = AddCardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            front, back = dialog.get_data()
            if not front or not back:
                return
            self.current_deck["cards"].append({"front": front, "back": back})
            self.cards = self.current_deck["cards"]
            self._dirty = True
            self._update_title()
            self.update_ui_for_saved_deck()

    def edit_cards(self):
        if not self.current_deck:
            return
        dialog = EditCardsDialog(self.current_deck["cards"], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._dirty = True
            self._update_title()
        self.cards = self.current_deck["cards"]

    def start_flashcard(self):
        if not self.cards:
            return
        stylesheet = STYLESHEET_DARK if self.dark_theme_action.isChecked() else STYLESHEET_LIGHT
        cards = self._get_cards_for_session()
        dialog = FlashcardDialog(cards, stylesheet, self)
        dialog.exec()

    def start_practice(self):
        if not self.cards:
            return
        repeat_incorrect = self.repeat_action.isChecked()
        stylesheet = STYLESHEET_DARK if self.dark_theme_action.isChecked() else STYLESHEET_LIGHT
        cards = self._get_cards_for_session()
        dialog = PracticeDialog(cards, repeat_incorrect, stylesheet, self)
        dialog.exec()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_N and self.add_card_button.isEnabled():
            if self.current_deck:
                self.add_card()
                event.accept()
                return
        elif event.key() == Qt.Key.Key_E:
            if self.current_deck:
                self.edit_cards()
                event.accept()
                return
        if self.cards:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                self.start_flashcard()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Space:
                self.start_practice()
                event.accept()
                return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        self._save_settings()
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()

    def _get_cards_for_session(self) -> list:
        """Geeft de kaarten terug, eventueel omgedraaid."""
        if not self.flip_cards_action.isChecked():
            return self.cards
        flipped = []
        for card in self.cards:
            new_front = ", ".join(card["back"])
            new_back = [card["front"]]
            flipped.append({"front": new_front, "back": new_back})
        return flipped