from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QFileDialog,
    QDialog, QDialogButtonBox, QScrollArea, QToolButton
)

import random
from pathlib import Path
from storage import save_deck, load_deck
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from helpers import start_card, check_answer


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


TRANSLATIONS = {
    "nl": {
        "menu_deck": "Deck",
        "menu_new_deck": "Nieuw deck",
        "menu_load_deck": "Deck laden",
        "menu_save_deck": "Deck opslaan",
        "menu_options": "Opties",
        "menu_dark_theme": "Donker thema",
        "menu_repeat": "Fout beantwoorde kaarten herhalen",
        "menu_flip_cards": "Kaarten omdraaien",
        "menu_language": "Taal",
        "no_deck": "Geen deck geladen.",
        "new_card": "Nieuwe kaart",
        "edit_cards": "Kaarten bewerken",
        "flashcard": "Oefenen",
        "practice": "Invullen",
        "show_answers": "Toon antwoorden",
        "next_card": "Volgende kaart",
        "stop": "Stoppen",
        "flip": "Draaien",
        "deck_finished": "Deck doorgewerkt!",
        "score_text": "Deck doorgewerkt!  {score:.1f} / 10",
        "window_practice": "Invullen",
        "window_flashcard": "Oefenen",
        "window_edit": "Kaarten bewerken",
        "window_add": "Kaart toevoegen",
        "save_close": "Wijzigen",
        "close": "Sluiten zonder opslaan",
        "card_number": "Kaart {n}",
        "front": "Voorkant",
        "answers": "Antwoorden",
        "add_answer": "+ Antwoord toevoegen",
        "delete_card": "Kaart verwijderen",
        "placeholder_front": "Voorkant",
        "placeholder_answer": "Antwoord {n}",
        "placeholder_input": "Typ een antwoord en druk Enter…",
        "save_dialog": "Deck opslaan",
        "load_dialog": "Deck laden",
        "deck_saved": "Deck opgeslagen: {name}",
        "deck_loaded": "Deck geladen: {name}",
        "load_error": "Fout bij laden: {error}",
        "new_deck_name": "Nieuw deck",
        "unsaved_warning_title": "Niet opgeslagen wijzigingen",
        "unsaved_warning_text": "Het deck heeft niet-opgeslagen wijzigingen. Wil je opslaan voordat je afsluit?",
        "unsaved_save": "Opslaan",
        "unsaved_discard": "Afsluiten",
        "unsaved_cancel": "Annuleren",
    },
    "en": {
        "menu_deck": "Deck",
        "menu_new_deck": "New deck",
        "menu_load_deck": "Load deck",
        "menu_save_deck": "Save deck",
        "menu_options": "Options",
        "menu_dark_theme": "Dark theme",
        "menu_repeat": "Repeat incorrectly answered cards",
        "menu_flip_cards": "Flip cards",
        "menu_language": "Language",
        "no_deck": "No deck loaded.",
        "new_card": "New card",
        "edit_cards": "Edit cards",
        "flashcard": "Study",
        "practice": "Test yourself",
        "show_answers": "Show answers",
        "next_card": "Next card",
        "stop": "Stop",
        "flip": "Flip",
        "deck_finished": "Deck completed!",
        "score_text": "Deck completed!  {score:.1f} / 10",
        "window_practice": "Test yourself",
        "window_flashcard": "Study",
        "window_edit": "Edit cards",
        "window_add": "Add card",
        "save_close": "Confirm changes",
        "close": "Close without saving",
        "card_number": "Card {n}",
        "front": "Front",
        "answers": "Answers",
        "add_answer": "+ Add answer",
        "delete_card": "Delete card",
        "placeholder_front": "Front",
        "placeholder_answer": "Answer {n}",
        "placeholder_input": "Type an answer and press Enter…",
        "save_dialog": "Save deck",
        "load_dialog": "Load deck",
        "deck_saved": "Deck saved: {name}",
        "deck_loaded": "Deck loaded: {name}",
        "load_error": "Error loading: {error}",
        "new_deck_name": "New deck",
        "unsaved_warning_title": "Unsaved changes",
        "unsaved_warning_text": "The deck has unsaved changes. Do you want to save before quitting?",
        "unsaved_save": "Save",
        "unsaved_discard": "Quit",
        "unsaved_cancel": "Cancel",
    }
}

T = TRANSLATIONS["nl"]  # actieve taal

STYLESHEET_DARK = """
    QWidget {
        background-color: #121212;
        color: white;
        font-family: Segoe UI;
    }
    QFrame {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 0px;
    }
    QLabel#FrontLabel {
        font-size: 32px;
        padding: 8px;
    }
    QLabel#SlotLabelEmpty {
        font-size: 32px;
        padding: 10px;
        background-color: #1a1a1a;
        border-radius: 10px;
    }
    QLabel#SlotLabel {
        font-size: 32px;
        padding: 10px;
        background-color: #2a2a2a;
        border-radius: 10px;
    }
    QLabel#SlotLabelCorrect {
        font-size: 32px;
        padding: 10px;
        background-color: #14532d;
        border-radius: 10px;
    }
    QLabel#SlotLabelShown {
        font-size: 32px;
        padding: 10px;
        background-color: #2a2a2a;
        border-radius: 10px;
    }
    QLabel#SlotLabelWrong {
        font-size: 32px;
        padding: 10px;
        background-color: #7f1d1d;
        border-radius: 10px;
    }
    QLineEdit {
        padding: 12px;
        border-radius: 10px;
        background-color: #1f1f1f;
        border: 1px solid #2a2a2a;
        font-size: 16px;
        color: white;
    }
    QPushButton {
        background-color: #2d2d2d;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 10px;
        font-size: 15px;
    }
    QPushButton:hover {
        background-color: #3a3a3a;
    }
    QPushButton:disabled {
        background-color: #1a1a1a;
        color: #444;
    }
    QPushButton#PrimaryButton {
        background-color: #2563eb;
    }
    QPushButton#PrimaryButton:hover {
        background-color: #1d4ed8;
    }
    QPushButton#ReadyButton {
        background-color: #16a34a;
    }
    QPushButton#ReadyButton:hover {
        background-color: #15803d;
    }
    QLineEdit:focus {
        border: 1px solid #2563eb;
    }
    QPushButton#SecondaryButton {
        background-color: transparent;
        color: #9ca3af;
        border: 1px dashed #2a2a2a;
        border-radius: 8px;
        font-size: 13px;
        padding: 8px;
    }
    QPushButton#SecondaryButton:hover {
        border-color: #2563eb;
        color: white;
    }
"""

STYLESHEET_LIGHT = """
    QWidget {
        background-color: #f5f5f5;
        color: #111;
        font-family: Segoe UI;
    }
    QFrame {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 0px;
    }
    QLabel#FrontLabel {
        font-size: 32px;
        padding: 8px;
        color: #111;
    }
    QLabel#SlotLabelEmpty {
        font-size: 32px;
        padding: 10px;
        background-color: #e0e0e0;
        border-radius: 10px;
        color: #111;
    }
    QLabel#SlotLabel {
        font-size: 32px;
        padding: 10px;
        background-color: #e8e8e8;
        border-radius: 10px;
        color: #111;
    }
    QLabel#SlotLabelCorrect {
        font-size: 32px;
        padding: 10px;
        background-color: #bbf7d0;
        border-radius: 10px;
        color: #111;
    }
    QLabel#SlotLabelShown {
        font-size: 32px;
        padding: 10px;
        background-color: #e8e8e8;
        border-radius: 10px;
        color: #111;
    }
    QLabel#SlotLabelWrong {
        font-size: 32px;
        padding: 10px;
        background-color: #fecaca;
        border-radius: 10px;
        color: #111;
    }
    QLineEdit {
        padding: 12px;
        border-radius: 10px;
        background-color: #ffffff;
        border: 1px solid #ccc;
        font-size: 16px;
        color: #111;
    }
    QPushButton {
        background-color: #e8e8e8;
        color: #111;
        border: none;
        padding: 12px;
        border-radius: 10px;
        font-size: 15px;
    }
    QPushButton:hover {
        background-color: #d0d0d0;
    }
    QPushButton:disabled {
        background-color: #f0f0f0;
        color: #aaa;
    }
    QPushButton#PrimaryButton {
        background-color: #2563eb;
        color: white;
    }
    QPushButton#PrimaryButton:hover {
        background-color: #1d4ed8;
    }
    QPushButton#ReadyButton {
        background-color: #16a34a;
        color: white;
    }
    QPushButton#ReadyButton:hover {
        background-color: #15803d;
    }
    QLineEdit:focus {
        border: 1px solid #2563eb;
    }
    QPushButton#SecondaryButton {
        background-color: transparent;
        color: #9ca3af;
        border: 1px dashed #d0d0d0;
        border-radius: 8px;
        font-size: 13px;
        padding: 8px;
    }
    QPushButton#SecondaryButton:hover {
        border-color: #2563eb;
        color: #111;
    }
"""

STYLESHEET = STYLESHEET_DARK

MAX_SLOTS = 6


class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_deck = None
        self.cards = []
        self.deck_path = None
        self._dirty = False

        self.setup_ui()
        self.update_ui_for_no_deck()

    def setup_ui(self):
        self.setWindowTitle("Flashcard App")
        self.resize(600, 300)
        self.setStyleSheet(STYLESHEET)

        # ===== MENU =====
        self.menu = self.menuBar()
        self.deck_menu = self.menu.addMenu(T["menu_deck"])

        self.new_action = self.deck_menu.addAction(T["menu_new_deck"])
        self.new_action.triggered.connect(self.create_new_deck)

        self.open_action = self.deck_menu.addAction(T["menu_load_deck"])
        self.open_action.triggered.connect(self.load_deck_dialog)

        self.save_action = self.deck_menu.addAction(T["menu_save_deck"])
        self.save_action.triggered.connect(self.save_current_deck)

        self.options_menu = self.menu.addMenu(T["menu_options"])
        self.dark_theme_action = self.options_menu.addAction(T["menu_dark_theme"])
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.setChecked(True)
        self.dark_theme_action.triggered.connect(self.toggle_theme)
        self.repeat_action = self.options_menu.addAction(T["menu_repeat"])
        self.repeat_action.setCheckable(True)
        self.repeat_action.setChecked(True)
        self.flip_cards_action = self.options_menu.addAction(T["menu_flip_cards"])
        self.flip_cards_action.setCheckable(True)
        self.flip_cards_action.setChecked(False)

        self.lang_menu = self.menu.addMenu(T["menu_language"])
        self.lang_nl_action = self.lang_menu.addAction("Nederlands")
        self.lang_nl_action.setCheckable(True)
        self.lang_nl_action.setChecked(True)
        self.lang_en_action = self.lang_menu.addAction("English")
        self.lang_en_action.setCheckable(True)
        self.lang_nl_action.triggered.connect(lambda: self.set_language("nl"))
        self.lang_en_action.triggered.connect(lambda: self.set_language("en"))

        # ===== LAYOUT =====
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        self.deck_label = QLabel(T["no_deck"])
        self.deck_label.setObjectName("FrontLabel")
        self.deck_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.deck_label)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.add_card_button = QPushButton(T["new_card"])
        self.add_card_button.clicked.connect(self.add_card)
        self.add_card_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(self.add_card_button)

        self.edit_cards_button = QPushButton(T["edit_cards"])
        self.edit_cards_button.clicked.connect(self.edit_cards)
        self.edit_cards_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        left_layout.addWidget(self.edit_cards_button)

        left_layout.addStretch()

        self.flashcard_button = QPushButton(T["flashcard"])
        self.flashcard_button.clicked.connect(self.start_flashcard)
        self.flashcard_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        right_layout.addWidget(self.flashcard_button)

        self.practice_button = QPushButton(T["practice"])
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
        self.add_card_button.setText(T["new_card"])
        self.edit_cards_button.setText(T["edit_cards"])
        self.flashcard_button.setText(T["flashcard"])
        self.practice_button.setText(T["practice"])

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
        self.practice_button.setDisabled(True)
        self.flashcard_button.setDisabled(True)
        self.add_card_button.setDisabled(True)
        self.edit_cards_button.setDisabled(True)
        self.save_action.setEnabled(False)

    def update_ui_for_unsaved_deck(self):
        self.practice_button.setDisabled(True)
        self.flashcard_button.setDisabled(True)
        self.add_card_button.setDisabled(False)
        self.edit_cards_button.setDisabled(False)
        self.save_action.setEnabled(True)

    def update_ui_for_saved_deck(self):
        self.practice_button.setDisabled(False)
        self.flashcard_button.setDisabled(False)
        self.add_card_button.setDisabled(False)
        self.edit_cards_button.setDisabled(False)
        self.save_action.setEnabled(True)

    def _update_title(self):
        if self.current_deck:
            name = Path(self.deck_path).stem if self.deck_path else self.current_deck["name"]
            dirty = " *" if self._dirty else ""
            self.setWindowTitle(f"Flashcard App - {name}{dirty}")
        else:
            self.setWindowTitle("Flashcard App")

    def set_active_deck(self, deck: dict):
        self.current_deck = deck
        self.cards = deck["cards"]
        self.deck_path = None
        self._dirty = True
        self._update_title()
        self.update_ui_for_unsaved_deck()

    def create_new_deck(self):
        deck = {"name": T["new_deck_name"], "cards": []}
        self.set_active_deck(deck)

    def save_current_deck(self):
        if not self.current_deck:
            return

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

    def load_deck_dialog(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, T["load_dialog"], "", "Deck files (*.json)"
        )
        if not filepath:
            return

        try:
            deck = load_deck(filepath)
        except Exception as e:
            self.deck_label.setText(T["load_error"].format(error=e))
            return

        self.deck_path = filepath
        self.current_deck = deck
        self.cards = deck["cards"]
        self._dirty = False
        self._update_title()
        self.update_ui_for_saved_deck()

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
        if self._dirty and self.current_deck:
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
                event.accept()
            elif clicked == discard_btn:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

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


# ===== PRACTICE DIALOG =====

class PracticeDialog(QDialog):
    def __init__(self, cards: list, repeat_incorrect: bool = True, stylesheet: str = STYLESHEET_DARK, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T["window_practice"])
        self.resize(900, 600)
        self.setStyleSheet(stylesheet)

        self.cards = cards
        self.repeat_incorrect = repeat_incorrect
        self.current_card = None
        self.state = None
        self.slot_labels = []
        self.card_complete = False
        self.queue = []
        self.card_scores = []

        self.setup_ui()
        self.start_session()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Kaartframe
        self.card_frame = QFrame()
        card_layout = QVBoxLayout()
        card_layout.setSpacing(14)

        self.front_label = QLabel("")
        self.front_label.setObjectName("FrontLabel")
        self.front_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.front_label)

        self.slots_layout = QVBoxLayout()
        card_layout.addLayout(self.slots_layout)

        self.card_frame.setLayout(card_layout)
        layout.addWidget(self.card_frame)

        # Invoer
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText(T["placeholder_input"])
        self.answer_input.returnPressed.connect(self.on_check_clicked)
        layout.addWidget(self.answer_input)

        # Knoppen
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.show_answers_button = QPushButton(T["show_answers"])
        self.show_answers_button.clicked.connect(self.show_answers)
        btn_layout.addWidget(self.show_answers_button)

        self.next_button = QPushButton(T["next_card"])
        self.next_button.clicked.connect(self.next_card)
        self.next_button.setObjectName("PrimaryButton")
        btn_layout.addWidget(self.next_button)

        self.stop_button = QPushButton(T["stop"])
        self.stop_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.stop_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def start_session(self):
        self.queue = list(self.cards)
        random.shuffle(self.queue)
        card = self.queue.pop(0)
        self.load_card(card)

    def clear_slots(self):
        while self.slots_layout.count():
            item = self.slots_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                inner = item.layout()
                while inner.count():
                    child = inner.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None)
        self.slot_labels = []

    def build_slots(self, count):
        self.clear_slots()
        labels = []
        for i in range(count):
            label = QLabel("")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setObjectName("SlotLabel")
            self.slot_labels.append(label)
            labels.append(label)

        if count <= 3:
            for label in labels:
                self.slots_layout.addWidget(label)
        else:
            for i in range(0, count, 2):
                row = QHBoxLayout()
                row.setSpacing(12)
                row.addWidget(labels[i])
                if i + 1 < count:
                    row.addWidget(labels[i + 1])
                else:
                    spacer = QWidget()
                    spacer.setStyleSheet("background: transparent;")
                    spacer.setSizePolicy(
                        labels[i].sizePolicy().horizontalPolicy(),
                        labels[i].sizePolicy().verticalPolicy()
                    )
                    row.addWidget(spacer)
                self.slots_layout.addLayout(row)

    def load_card(self, card):
        self.current_card = card
        self.state = start_card(card)
        self.card_complete = False
        self.correct_this_card = 0
        self.answered_correctly = True

        self.front_label.setText(card["front"])
        self.build_slots(len(self.state["all_answers"]))

        self.answer_input.setDisabled(False)
        self.answer_input.clear()
        self.answer_input.setFocus()
        self.show_answers_button.setDisabled(False)

        self.next_button.setObjectName("PrimaryButton")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)

    def fill_next_slot(self, text):
        for label in self.slot_labels:
            if label.objectName() == "SlotLabel":
                label.setText(text)
                label.setObjectName("SlotLabelCorrect")
                label.style().unpolish(label)
                label.style().polish(label)
                return

    def on_check_clicked(self):
        if not self.current_card:
            return

        success, status, normalized = check_answer(
            self.answer_input.text(), self.state
        )

        self.answer_input.clear()
        self.answer_input.setFocus()

        if status == "empty":
            return

        if success:
            self.correct_this_card += 1
            self.fill_next_slot(normalized)

            if not self.state["remaining_answers"]:
                self.card_complete = True
                self.answer_input.clearFocus()
                self.next_button.setObjectName("ReadyButton")
                self.next_button.style().unpolish(self.next_button)
                self.next_button.style().polish(self.next_button)
            return

        if status == "wrong":
            self.answered_correctly = False
            self.show_wrong_answers()

    def show_wrong_answers(self):
        remaining = list(self.state["remaining_answers"])
        for label in self.slot_labels:
            if label.objectName() == "SlotLabel" and remaining:
                label.setText(remaining.pop(0))
                label.setObjectName("SlotLabelWrong")
                label.style().unpolish(label)
                label.style().polish(label)
        self.state["remaining_answers"].clear()
        self.card_complete = True
        self.answer_input.clearFocus()
        self.next_button.setObjectName("ReadyButton")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)

    def show_answers(self):
        if not self.current_card:
            return
        self.answered_correctly = False
        remaining = list(self.state["remaining_answers"])
        for label in self.slot_labels:
            if label.objectName() == "SlotLabel" and remaining:
                label.setText(remaining.pop(0))
                label.setObjectName("SlotLabelShown")
                label.style().unpolish(label)
                label.style().polish(label)
        self.state["remaining_answers"].clear()
        self.card_complete = True
        self.answer_input.clearFocus()
        self.next_button.setObjectName("ReadyButton")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)

    def next_card(self):
        # score vastleggen als de kaart afgerond is
        if self.card_complete:
            total = len(self.state["all_answers"])
            self.card_scores.append((self.correct_this_card, total))

            # alleen herhalen als NIET volledig correct beantwoord
            if self.repeat_incorrect and self.correct_this_card < total:
                self.queue.append(self.current_card)
        else:
            # onafgemaakte kaart altijd herhalen als repeat_incorrect aan staat
            if self.repeat_incorrect:
                self.queue.append(self.current_card)

        if not self.queue:
            self.show_deck_finished()
            return

        card = self.queue.pop(0)
        self.load_card(card)

    def show_deck_finished(self):
        if self.card_scores:
            score = sum(c / t for c, t in self.card_scores) / len(self.card_scores) * 10
            score_text = T["score_text"].format(score=score)
        else:
            score_text = T["deck_finished"]

        self.current_card = None
        self.state = None
        self.clear_slots()
        self.front_label.setText(score_text)
        self.answer_input.clear()
        self.answer_input.setDisabled(True)
        self.next_button.setDisabled(True)
        self.show_answers_button.setDisabled(True)

    def keyPressEvent(self, event):
        # Space = volgende kaart wanneer klaar (zoals je al had)
        if event.key() == Qt.Key.Key_Space:
            if self.card_complete:
                self.next_card()
            event.accept()
            return

        # Enter/Return: als de input focus heeft, alleen checken en NIET laten doorpropageren
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.answer_input and self.answer_input.hasFocus():
                self.on_check_clicked()
                event.accept()
                return

        super().keyPressEvent(event)


# ===== FLASHCARD DIALOG =====

class FlashcardDialog(QDialog):
    def __init__(self, cards: list, stylesheet: str = STYLESHEET_DARK, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T["window_flashcard"])
        self.resize(900, 600)
        self.setStyleSheet(stylesheet)

        self.cards = cards
        self.queue = []
        self.current_card = None
        self.showing_back = False

        self.setup_ui()
        self.start_session()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        self.card_frame = QFrame()
        card_layout = QVBoxLayout()
        card_layout.setSpacing(14)

        self.card_label = QLabel("")
        self.card_label.setObjectName("FrontLabel")
        self.card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_label.setWordWrap(True)
        card_layout.addWidget(self.card_label)

        self.card_frame.setLayout(card_layout)
        layout.addWidget(self.card_frame)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.flip_button = QPushButton(T["flip"])
        self.flip_button.clicked.connect(self.flip_card)
        self.flip_button.setObjectName("PrimaryButton")
        self.flip_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_layout.addWidget(self.flip_button)

        self.next_button = QPushButton(T["next_card"])
        self.next_button.clicked.connect(self.next_card)
        self.next_button.setDisabled(True)
        self.next_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_layout.addWidget(self.next_button)

        self.stop_button = QPushButton(T["stop"])
        self.stop_button.clicked.connect(self.reject)
        self.stop_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_layout.addWidget(self.stop_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def start_session(self):
        self.queue = list(self.cards)
        random.shuffle(self.queue)
        self.load_card(self.queue.pop(0))

    def load_card(self, card):
        self.current_card = card
        self.showing_back = False
        self.card_label.setText(card["front"])
        self.flip_button.setDisabled(False)
        self.next_button.setDisabled(True)
        self.next_button.setObjectName("")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)

    def flip_card(self):
        if not self.current_card:
            return
        if not self.showing_back:
            back_text = ",  ".join(self.current_card["back"])
            self.card_label.setText(back_text)
            self.showing_back = True
            self.flip_button.setDisabled(True)
            self.next_button.setDisabled(False)
            self.next_button.setObjectName("ReadyButton")
            self.next_button.style().unpolish(self.next_button)
            self.next_button.style().polish(self.next_button)

    def next_card(self):
        if not self.queue:
            self.card_label.setText(T["deck_finished"])
            self.flip_button.setDisabled(True)
            self.next_button.setDisabled(True)
            return
        self.load_card(self.queue.pop(0))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            if not self.showing_back:
                self.flip_card()
            else:
                self.next_card()
            event.accept()
        else:
            super().keyPressEvent(event)


# ===== EDIT CARDS DIALOG =====

class EditCardsDialog(QDialog):
    def __init__(self, cards: list, parent=None):
        super().__init__(parent)
        self.cards = cards
        self.setWindowTitle(T["window_edit"])
        self.resize(600, 500)
        # Sla originele staat op voor discard
        import copy
        self._original_cards = copy.deepcopy(cards)
        # { card_id -> {"front": QLineEdit, "answers": [DeletableLineEdit], "add_btn": QPushButton, "answers_layout": QVBoxLayout } }
        self.card_fields = {}

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.scroll_widget = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(16)
        self.scroll_widget.setLayout(self.cards_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.scroll_widget)
        self.main_layout.addWidget(scroll)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        save_btn = QPushButton(T["save_close"])
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        discard_btn = QPushButton(T["close"])
        discard_btn.clicked.connect(self.discard_and_close)
        btn_row.addWidget(discard_btn)

        self.main_layout.addLayout(btn_row)

        self.build_card_list()

    def _icon_color(self):
        p = self.parent()
        if p and hasattr(p, "dark_theme_action"):
            return "white" if p.dark_theme_action.isChecked() else "#111"
        return "white"

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            for card_id, fields in self.card_fields.items():
                all_fields = [fields["front"]] + fields["answers"]
                for i, field in enumerate(all_fields):
                    if field.hasFocus():
                        next_idx = i + 1
                        if next_idx < len(all_fields):
                            all_fields[next_idx].setFocus()
                        elif len(fields["answers"]) < 6:
                            self._add_answer_field(card_id)
                            fields["answers"][-1].setFocus()
                        event.accept()
                        return
            event.accept()
        else:
            super().keyPressEvent(event)

    def build_card_list(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.card_fields = {}

        for i, card in enumerate(self.cards):
            card_id = id(card)
            frame = QFrame()
            layout = QVBoxLayout()
            layout.setSpacing(4)
            layout.setContentsMargins(16, 16, 16, 16)

            number_label = QLabel(T["card_number"].format(n=i + 1))
            number_label.setStyleSheet("font-size: 18px; font-weight: 600; color: white;")
            layout.addWidget(number_label)
            layout.addSpacing(8)

            front_label = QLabel(T["front"])
            front_label.setStyleSheet("color: #9ca3af; font-size: 12px")
            layout.addWidget(front_label)
            layout.addSpacing(4)

            front_input = QLineEdit(card["front"])
            front_input.textChanged.connect(lambda text, c=card: c.update({"front": text}))
            layout.addWidget(front_input)
            layout.addSpacing(12)

            back_label = QLabel(T["answers"])
            back_label.setStyleSheet("color: #9ca3af; font-size: 12px")
            layout.addWidget(back_label)
            layout.addSpacing(4)

            answers_layout = QVBoxLayout()
            answers_layout.setSpacing(4)
            layout.addLayout(answers_layout)

            answer_fields = []
            for j, ans in enumerate(card["back"]):
                ans_input = DeletableLineEdit(
                    ans,
                    on_delete=lambda _, c=card, idx=j: self.delete_answer(c, idx),
                    icon_color=self._icon_color()
                )
                ans_input.setPlaceholderText(T["placeholder_answer"].format(n=j + 1))
                ans_input.textChanged.connect(lambda text, c=card, idx=j: c["back"].__setitem__(idx, text))
                answers_layout.addWidget(ans_input)
                answer_fields.append(ans_input)

            layout.addSpacing(8)
            add_ans_btn = QPushButton(T["add_answer"])
            add_ans_btn.setObjectName("SecondaryButton")
            add_ans_btn.clicked.connect(lambda _, cid=card_id: self._add_answer_field(cid))
            add_ans_btn.setDisabled(len(answer_fields) >= 6)
            layout.addWidget(add_ans_btn)

            layout.addSpacing(4)
            delete_btn = QPushButton(T["delete_card"])
            delete_btn.clicked.connect(lambda _, c=card: self.delete_card(c))
            layout.addWidget(delete_btn)

            frame.setLayout(layout)
            self.cards_layout.addWidget(frame)

            self.card_fields[card_id] = {
                "card": card,
                "front": front_input,
                "answers": answer_fields,
                "answers_layout": answers_layout,
                "add_btn": add_ans_btn,
            }

        self.cards_layout.addStretch()

    def _add_answer_field(self, card_id):
        fields = self.card_fields[card_id]
        card = fields["card"]
        if len(fields["answers"]) >= 6:
            return
        card["back"].append("")
        j = len(fields["answers"])
        ans_input = DeletableLineEdit(
            "",
            on_delete=lambda _, c=card, idx=j: self.delete_answer(c, idx),
            icon_color=self._icon_color()
        )
        ans_input.setPlaceholderText(T["placeholder_answer"].format(n=j + 1))
        ans_input.textChanged.connect(lambda text, c=card, idx=j: c["back"].__setitem__(idx, text))
        fields["answers_layout"].addWidget(ans_input)
        fields["answers"].append(ans_input)
        fields["add_btn"].setDisabled(len(fields["answers"]) >= 6)

    def delete_card(self, card):
        self.cards.remove(card)
        self.build_card_list()

    def add_answer(self, card):
        card["back"].append("")
        self.build_card_list()

    def delete_answer(self, card, idx):
        if len(card["back"]) > 1:
            card["back"].pop(idx)
            self.build_card_list()

    def discard_and_close(self):
        # Herstel originele kaartdata
        self.cards.clear()
        self.cards.extend(self._original_cards)
        self.reject()


# ===== ADD CARD DIALOG =====

class AddCardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(T["window_add"])
        self.resize(600, 300)
        self.back_inputs = []

        outer = QVBoxLayout()
        outer.setSpacing(0)

        # Kaartframe, identiek aan EditCardsDialog
        self.frame = QFrame()
        self.frame_layout = QVBoxLayout()
        self.frame_layout.setSpacing(4)
        self.frame_layout.setContentsMargins(16, 16, 16, 16)

        front_label = QLabel(T["front"])
        front_label.setStyleSheet("color: #9ca3af; font-size: 12px")
        self.frame_layout.addWidget(front_label)
        self.frame_layout.addSpacing(4)

        self.front_input = QLineEdit()
        self.front_input.setPlaceholderText(T["placeholder_front"])
        self.frame_layout.addWidget(self.front_input)
        self.frame_layout.addSpacing(12)

        self.answers_section_label = QLabel(T["answers"])
        self.answers_section_label.setStyleSheet("color: #9ca3af; font-size: 12px")
        self.frame_layout.addWidget(self.answers_section_label)
        self.frame_layout.addSpacing(4)

        self.answers_layout = QVBoxLayout()
        self.answers_layout.setSpacing(4)
        self.frame_layout.addLayout(self.answers_layout)

        self.frame_layout.addSpacing(8)
        self.add_answer_btn = QPushButton(T["add_answer"])
        self.add_answer_btn.setObjectName("SecondaryButton")
        self.add_answer_btn.clicked.connect(self.add_answer_field)
        self.frame_layout.addWidget(self.add_answer_btn)

        self.frame.setLayout(self.frame_layout)
        outer.addWidget(self.frame)
        outer.addSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        save_btn = QPushButton(T["save_close"])
        save_btn.setObjectName("PrimaryButton")
        save_btn.setAutoDefault(False)
        save_btn.setDefault(False)
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        discard_btn = QPushButton(T["close"])
        discard_btn.setAutoDefault(False)
        discard_btn.setDefault(False)
        discard_btn.clicked.connect(self.reject)
        btn_row.addWidget(discard_btn)

        outer.addLayout(btn_row)

        self.setLayout(outer)

        # Start met 1 antwoordveld
        self.add_answer_field()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Sprong naar volgend invoerveld, geen Ok
            all_fields = [self.front_input] + self.back_inputs
            for i, field in enumerate(all_fields):
                if field.hasFocus():
                    next_idx = i + 1
                    if next_idx < len(all_fields):
                        all_fields[next_idx].setFocus()
                    else:
                        # Laatste veld: voeg nieuw antwoord toe als mogelijk
                        if len(self.back_inputs) < 6:
                            self.add_answer_field()
                            self.back_inputs[-1].setFocus()
                    event.accept()
                    return
            event.accept()
        else:
            super().keyPressEvent(event)

    def _icon_color(self):
        p = self.parent()
        if p and hasattr(p, "dark_theme_action"):
            return "white" if p.dark_theme_action.isChecked() else "#111"
        return "white"

    def add_answer_field(self):
        if len(self.back_inputs) >= 6:
            return
        n = len(self.back_inputs) + 1
        field = DeletableLineEdit(
            "",
            on_delete=lambda _, idx=len(self.back_inputs): self.delete_answer_field(idx),
            icon_color=self._icon_color()
        )
        field.setPlaceholderText(T["placeholder_answer"].format(n=n))
        self.answers_layout.addWidget(field)
        self.back_inputs.append(field)
        self.adjustSize()
        self.add_answer_btn.setDisabled(len(self.back_inputs) >= 6)

    def delete_answer_field(self, idx):
        if len(self.back_inputs) <= 1:
            return
        field = self.back_inputs.pop(idx)
        self.answers_layout.removeWidget(field)
        field.setParent(None)
        # Hernoem placeholders
        for i, f in enumerate(self.back_inputs):
            f.setPlaceholderText(T["placeholder_answer"].format(n=i + 1))
        self.adjustSize()
        self.add_answer_btn.setDisabled(False)

    def get_data(self):
        front = self.front_input.text().strip()
        back = [f.text().strip() for f in self.back_inputs if f.text().strip()]
        return front, back