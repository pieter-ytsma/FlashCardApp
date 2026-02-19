from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QFileDialog,
    QDialog, QDialogButtonBox, QScrollArea
)

import random
from pathlib import Path
from storage import save_deck, load_deck
from PySide6.QtCore import Qt
from helpers import start_card, check_answer


STYLESHEET = """
    QWidget {
        background-color: #121212;
        color: white;
        font-family: Segoe UI;
    }
    QFrame {
        background-color: #1e1e1e;
        border-radius: 16px;
        padding: 24px;
    }
    QLabel#FrontLabel {
        font-size: 32px;
        padding: 8px;
    }
    QLabel#SlotLabelEmpty {
        font-size: 18px;
        padding: 10px;
        background-color: #1a1a1a;
        border-radius: 10px;
    }
    QLabel#SlotLabel {
        font-size: 18px;
        padding: 10px;
        background-color: #2a2a2a;
        border-radius: 10px;
    }
    QLabel#SlotLabelCorrect {
        font-size: 18px;
        padding: 10px;
        background-color: #14532d;
        border-radius: 10px;
    }
    QLabel#SlotLabelShown {
        font-size: 18px;
        padding: 10px;
        background-color: #2a2a2a;
        border-radius: 10px;
    }
    QLabel#SlotLabelWrong {
        font-size: 18px;
        padding: 10px;
        background-color: #7f1d1d;
        border-radius: 10px;
    }
    QLineEdit {
        padding: 12px;
        border-radius: 10px;
        background-color: #2d2d2d;
        border: none;
        font-size: 16px;
    }
    QPushButton {
        background-color: #2d2d2d;
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
"""

MAX_SLOTS = 6


class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_deck = None
        self.cards = []
        self.deck_path = None

        self.setup_ui()
        self.update_ui_for_no_deck()

    def setup_ui(self):
        self.setWindowTitle("Flashcard App")
        self.resize(600, 300)
        self.setStyleSheet(STYLESHEET)

        # ===== MENU =====
        self.menu = self.menuBar()
        self.deck_menu = self.menu.addMenu("Deck")

        self.new_action = self.deck_menu.addAction("Nieuw deck")
        self.new_action.triggered.connect(self.create_new_deck)

        self.open_action = self.deck_menu.addAction("Deck laden")
        self.open_action.triggered.connect(self.load_deck_dialog)

        self.save_action = self.deck_menu.addAction("Deck opslaan")
        self.save_action.triggered.connect(self.save_current_deck)

        # ===== LAYOUT =====
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        self.deck_label = QLabel("Geen deck geladen.")
        self.deck_label.setObjectName("FrontLabel")
        self.deck_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.deck_label)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        self.add_card_button = QPushButton("Nieuwe kaart")
        self.add_card_button.clicked.connect(self.add_card)
        left_layout.addWidget(self.add_card_button)

        self.edit_cards_button = QPushButton("Kaarten bewerken")
        self.edit_cards_button.clicked.connect(self.edit_cards)
        left_layout.addWidget(self.edit_cards_button)

        left_layout.addStretch()

        self.practice_button = QPushButton("Oefenen")
        self.practice_button.clicked.connect(self.start_practice)
        right_layout.addWidget(self.practice_button)

        right_layout.addStretch()

        bottom_layout.addLayout(left_layout, 1)
        bottom_layout.addLayout(right_layout, 1)

        main_layout.addLayout(bottom_layout)

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def update_ui_for_no_deck(self):
        self.deck_label.setText("Geen deck geladen.")
        self.practice_button.setDisabled(True)
        self.add_card_button.setDisabled(True)
        self.edit_cards_button.setDisabled(True)
        self.save_action.setEnabled(False)

    def update_ui_for_unsaved_deck(self):
        self.practice_button.setDisabled(True)
        self.add_card_button.setDisabled(False)
        self.edit_cards_button.setDisabled(False)
        self.save_action.setEnabled(True)

    def update_ui_for_saved_deck(self):
        self.practice_button.setDisabled(False)
        self.add_card_button.setDisabled(False)
        self.edit_cards_button.setDisabled(False)
        self.save_action.setEnabled(True)

    def set_active_deck(self, deck: dict):
        self.current_deck = deck
        self.cards = deck["cards"]
        self.deck_path = None
        self.deck_label.setText(f"Deck: {deck['name']}")
        self.update_ui_for_unsaved_deck()

    def create_new_deck(self):
        deck = {"name": "Nieuw deck", "cards": []}
        self.set_active_deck(deck)

    def save_current_deck(self):
        if not self.current_deck:
            return

        if not self.deck_path:
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Deck opslaan", "", "Deck files (*.json)"
            )
            if not filepath:
                return
            if not filepath.lower().endswith(".json"):
                filepath += ".json"
            self.deck_path = filepath

        save_deck(self.current_deck, self.deck_path)
        self.update_ui_for_saved_deck()
        self.deck_label.setText(f"Deck opgeslagen: {Path(self.deck_path).stem}")

    def load_deck_dialog(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Deck laden", "", "Deck files (*.json)"
        )
        if not filepath:
            return

        try:
            deck = load_deck(filepath)
        except Exception as e:
            self.deck_label.setText(f"Fout bij laden: {e}")
            return

        self.deck_path = filepath
        self.current_deck = deck
        self.cards = deck["cards"]
        self.deck_label.setText(f"Deck geladen: {Path(filepath).stem}")
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

    def edit_cards(self):
        if not self.current_deck:
            return
        dialog = EditCardsDialog(self.current_deck["cards"], self)
        dialog.exec()
        self.cards = self.current_deck["cards"]

    def start_practice(self):
        if not self.cards:
            return
        dialog = PracticeDialog(self.cards, self)
        dialog.exec()


# ===== PRACTICE DIALOG =====

class PracticeDialog(QDialog):
    def __init__(self, cards: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Oefenen")
        self.resize(900, 600)
        self.setStyleSheet(STYLESHEET)

        self.cards = cards
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
        self.answer_input.setPlaceholderText("Typ een antwoord en druk Enter…")
        self.answer_input.returnPressed.connect(self.on_check_clicked)
        layout.addWidget(self.answer_input)

        # Knoppen
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.show_answers_button = QPushButton("Toon antwoorden")
        self.show_answers_button.clicked.connect(self.show_answers)
        btn_layout.addWidget(self.show_answers_button)

        self.next_button = QPushButton("Volgende kaart")
        self.next_button.clicked.connect(self.next_card)
        self.next_button.setObjectName("PrimaryButton")
        btn_layout.addWidget(self.next_button)

        self.stop_button = QPushButton("Stoppen")
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
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.slot_labels = []

    def build_slots(self, count):
        self.clear_slots()
        for i in range(MAX_SLOTS):
            label = QLabel("")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if i < count:
                label.setObjectName("SlotLabel")
                self.slot_labels.append(label)
            else:
                label.setObjectName("SlotLabelEmpty")
                label.setText("")
            self.slots_layout.addWidget(label)

    def load_card(self, card):
        self.current_card = card
        self.state = start_card(card)
        self.card_complete = False
        self.correct_this_card = 0

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
        if not self.card_complete:
            self.queue.append(self.current_card)
        else:
            total = len(self.state["all_answers"])
            self.card_scores.append((self.correct_this_card, total))

        if not self.queue:
            self.show_deck_finished()
            return

        card = self.queue.pop(0)
        self.load_card(card)

    def show_deck_finished(self):
        if self.card_scores:
            score = sum(c / t for c, t in self.card_scores) / len(self.card_scores) * 10
            score_text = f"Deck doorgewerkt!  {score:.1f} / 10"
        else:
            score_text = "Deck doorgewerkt!"

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


# ===== EDIT CARDS DIALOG =====

class EditCardsDialog(QDialog):
    def __init__(self, cards: list, parent=None):
        super().__init__(parent)
        self.cards = cards
        self.setWindowTitle("Kaarten bewerken")
        self.resize(600, 500)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.scroll_widget = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(10)
        self.scroll_widget.setLayout(self.cards_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.scroll_widget)
        self.main_layout.addWidget(scroll)

        close_btn = QPushButton("Sluiten")
        close_btn.clicked.connect(self.accept)
        self.main_layout.addWidget(close_btn)

        self.build_card_list()

    def build_card_list(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, card in enumerate(self.cards):
            frame = QFrame()
            layout = QVBoxLayout()
            layout.setSpacing(6)

            number_label = QLabel(f"Kaart {i + 1}")
            number_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
            layout.addWidget(number_label)

            front_label = QLabel("Voorkant")
            front_label.setStyleSheet("color: #888; font-size: 12px;")
            layout.addWidget(front_label)

            front_input = QLineEdit(card["front"])
            front_input.textChanged.connect(lambda text, c=card: c.update({"front": text}))
            layout.addWidget(front_input)

            back_label = QLabel("Antwoorden")
            back_label.setStyleSheet("color: #888; font-size: 12px; margin-top: 6px;")
            layout.addWidget(back_label)

            for j, ans in enumerate(card["back"]):
                ans_input = QLineEdit(ans)
                ans_input.setPlaceholderText(f"Antwoord {j+1}")
                ans_input.textChanged.connect(lambda text, c=card, idx=j: c["back"].__setitem__(idx, text))
                layout.addWidget(ans_input)

            delete_btn = QPushButton("Verwijderen")
            delete_btn.clicked.connect(lambda _, c=card: self.delete_card(c))
            layout.addWidget(delete_btn)

            frame.setLayout(layout)
            self.cards_layout.addWidget(frame)

        self.cards_layout.addStretch()

    def delete_card(self, card):
        self.cards.remove(card)
        self.build_card_list()


# ===== ADD CARD DIALOG =====

class AddCardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Kaart toevoegen")
        self.resize(400, 400)

        layout = QVBoxLayout()

        self.front_input = QLineEdit()
        self.front_input.setPlaceholderText("Voorkant")
        layout.addWidget(self.front_input)

        self.back_inputs = []

        for i in range(6):
            back = QLineEdit()
            back.setPlaceholderText(f"Antwoord {i+1}")
            layout.addWidget(back)
            self.back_inputs.append(back)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        front = self.front_input.text().strip()
        back = [f.text().strip() for f in self.back_inputs if f.text().strip()]
        return front, back
