from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt
import random

from ..resources import T, STYLESHEET_DARK, STYLESHEET_LIGHT

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
        self.card_index = 0
        self.total_cards = len(cards)

        self.setup_ui()
        self.start_session()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        self.card_frame = QFrame()
        card_layout = QVBoxLayout()
        card_layout.setSpacing(14)

        counter_row = QHBoxLayout()
        counter_row.addStretch()
        self.counter_label = QLabel("")
        self.counter_label.setStyleSheet("font-size: 13px; color: #9ca3af; padding: 0px;")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        counter_row.addWidget(self.counter_label)
        card_layout.addLayout(counter_row)

        card_layout.addStretch()
        self.card_label = QLabel("")
        self.card_label.setObjectName("FrontLabel")
        self.card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_label.setWordWrap(True)
        card_layout.addWidget(self.card_label)
        card_layout.addStretch()

        self.card_frame.setLayout(card_layout)
        layout.addWidget(self.card_frame)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.flip_button = QPushButton(T["flip"] + "  ␣")
        self.flip_button.clicked.connect(self.flip_card)
        self.flip_button.setObjectName("PrimaryButton")
        self.flip_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_layout.addWidget(self.flip_button)

        self.next_button = QPushButton(T["next_card"] + "  ␣")
        self.next_button.clicked.connect(self.next_card)
        self.next_button.setDisabled(True)
        self.next_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_layout.addWidget(self.next_button)

        self.stop_button = QPushButton(T["stop"] + "  (Esc)")
        self.stop_button.clicked.connect(self.reject)
        self.stop_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_layout.addWidget(self.stop_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def start_session(self):
        self.queue = list(self.cards)
        random.shuffle(self.queue)
        self.card_index = 1
        self.total_cards = len(self.cards)
        self.load_card(self.queue.pop(0))

    def load_card(self, card):
        self.current_card = card
        self.showing_back = False
        self.card_label.setText(card["front"])
        self.counter_label.setText(f"{self.card_index} / {self.total_cards}")
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
            self.counter_label.setText("")
            self.flip_button.setDisabled(True)
            self.next_button.setDisabled(True)
            self.stop_button.setText(T["close_after_finish"])
            return
        self.card_index += 1
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