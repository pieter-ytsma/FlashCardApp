from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame
)
from PySide6.QtCore import Qt
from helpers import start_card, check_answer


class FlashcardApp(QWidget):
    def __init__(self):
        super().__init__()

        # Tijdelijke demo-kaarten (in memory)
        self.current_deck = None
        self.cards = []

        self.current_index = 0
        self.current_card = None
        self.state = None
        self.slot_labels = []

        self.setup_ui()
        self.update_ui_for_no_deck()

    def setup_ui(self):
        self.setWindowTitle("Flashcard App")
        self.resize(650, 520)

        self.setStyleSheet("""
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
                font-size: 34px;
                padding: 8px;
            }
            QLabel#SlotLabel {
                font-size: 18px;
                padding: 10px;
                background-color: #2a2a2a;
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
        """)

        root = QVBoxLayout()
        root.setSpacing(16)

        # Card frame
        self.card_frame = QFrame()
        card_layout = QVBoxLayout()
        card_layout.setSpacing(14)

        self.front_label = QLabel("")
        self.front_label.setObjectName("FrontLabel")
        self.front_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.front_label)

        self.slots_layout = QVBoxLayout()
        self.slots_layout.setSpacing(10)
        card_layout.addLayout(self.slots_layout)

        self.card_frame.setLayout(card_layout)
        root.addWidget(self.card_frame)

        # Input
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Typ een antwoord en druk Enter…")
        self.answer_input.returnPressed.connect(self.on_check_clicked)
        root.addWidget(self.answer_input)

        # Feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.feedback_label)

        # Buttons
        self.check_button = QPushButton("Controleer")
        self.check_button.clicked.connect(self.on_check_clicked)
        root.addWidget(self.check_button)

        self.next_button = QPushButton("Volgende kaart")
        self.next_button.clicked.connect(self.next_card)
        root.addWidget(self.next_button)

        self.setLayout(root)

    def clear_slots(self):
        while self.slots_layout.count():
            item = self.slots_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.slot_labels = []

    def build_slots(self, count):
        self.clear_slots()
        for _ in range(count):
            label = QLabel("_____")
            label.setObjectName("SlotLabel")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.slots_layout.addWidget(label)
            self.slot_labels.append(label)

    def load_card(self, card):
        self.current_card = card
        self.state = start_card(card)

        self.front_label.setText(card["front"])
        self.build_slots(len(self.state["all_answers"]))

        self.feedback_label.setText("")
        self.answer_input.clear()
        self.answer_input.setFocus()

    def fill_next_slot(self, text):
        for label in self.slot_labels:
            if label.text() == "_____":
                label.setText(text)
                return

    def on_check_clicked(self):
        if not self.current_card:
            return

        success, status, normalized = check_answer(
            self.answer_input.text(),
            self.state
        )

        self.answer_input.clear()
        self.answer_input.setFocus()

        if status == "empty":
            self.feedback_label.setText("Typ iets.")
        elif success:
            self.fill_next_slot(normalized)
            self.feedback_label.setText("Correct ✓")

            if not self.state["remaining_answers"]:
                self.feedback_label.setText("Alles gevonden 🎉")
        else:
            self.feedback_label.setText("Fout ✗ (of al ingevuld)")

    def next_card(self):
        self.current_index += 1
        if self.current_index >= len(self.cards):
            self.current_index = 0

        self.load_card(self.cards[self.current_index])

    def update_ui_for_no_deck(self):
        self.front_label.setText("Geen deck geladen.")
        self.clear_slots()
        self.answer_input.setDisabled(True)
        self.check_button.setDisabled(True)
        self.next_button.setDisabled(True)

    def update_ui_for_active_deck(self):
        self.answer_input.setDisabled(False)
        self.check_button.setDisabled(False)
        self.next_button.setDisabled(False)

    def set_active_deck(self, deck: dict):
        self.current_deck = deck
        self.cards = deck["cards"]
        self.current_index = 0

        if self.cards:
            self.update_ui_for_active_deck()
            self.load_card(self.cards[self.current_index])
        else:
            self.front_label.setText("Deck is leeg.")
