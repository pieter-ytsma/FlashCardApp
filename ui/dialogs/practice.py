from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit
)
from PySide6.QtCore import Qt
import random

from ..resources import T, STYLESHEET_DARK, STYLESHEET_LIGHT
from ..widgets import DeletableLineEdit  # als nodig
from helpers import start_card, check_answer

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
        self.card_index = 0
        self.total_cards = len(cards)
        self.cards_done = 0

        self.setup_ui()
        self.start_session()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Kaartframe
        self.card_frame = QFrame()
        card_layout = QVBoxLayout()
        self.card_layout = card_layout
        card_layout.setSpacing(14)

        counter_row = QHBoxLayout()
        counter_row.addStretch()
        self.counter_label = QLabel("")
        self.counter_label.setStyleSheet("font-size: 13px; color: #9ca3af; padding: 0px;")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        counter_row.addWidget(self.counter_label)
        card_layout.addLayout(counter_row)

        card_layout.addStretch()
        self.front_label = QLabel("")
        self.front_label.setObjectName("FrontLabel")
        self.front_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.front_label)
        card_layout.addStretch()

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

        self.show_answers_button = QPushButton(T["show_answers"] + "  (F1)")
        self.show_answers_button.clicked.connect(self.show_answers)
        btn_layout.addWidget(self.show_answers_button)

        self.next_button = QPushButton(T["next_card"] + "  ␣")
        self.next_button.clicked.connect(self.next_card)
        self.next_button.setObjectName("PrimaryButton")
        btn_layout.addWidget(self.next_button)

        self.stop_button = QPushButton(T["stop"] + "  (Esc)")
        self.stop_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.stop_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def start_session(self):
        self.queue = list(self.cards)
        random.shuffle(self.queue)
        self.card_index = 1
        self.total_cards = len(self.cards)
        self.cards_done = 0
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
        self.counter_label.setText(f"{self.cards_done + 1} / {self.total_cards}")
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
        self.show_answers_button.setDisabled(True)
        self.answer_input.clearFocus()
        self.next_button.setObjectName("ReadyButton")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)

    def next_card(self):
        if self.card_complete:
            total = len(self.state["all_answers"])
            self.card_scores.append((self.correct_this_card, total))

            if self.correct_this_card >= total:
                self.cards_done += 1
            elif self.repeat_incorrect:
                self.queue.append(self.current_card)
        else:
            if self.repeat_incorrect:
                self.queue.append(self.current_card)

        if not self.queue:
            self.show_deck_finished()
            return

        self.card_index += 1
        card = self.queue.pop(0)
        self.load_card(card)

    def show_deck_finished(self):
        if self.card_scores:
            score = sum(c / t for c, t in self.card_scores) / len(self.card_scores) * 100
            score_text = T["score_text"].format(score=score)
        else:
            score_text = T["deck_finished"]

        self.current_card = None
        self.state = None
        self.clear_slots()
        self.counter_label.setText("")
        self.front_label.setText(score_text)
        self.answer_input.clear()
        self.answer_input.setDisabled(True)
        self.next_button.setObjectName("PrimaryButton")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)
        self.next_button.setDisabled(True)
        self.show_answers_button.setDisabled(True)
        self.stop_button.setText(T["close_after_finish"])

    def keyPressEvent(self, event):
        # Space = volgende kaart wanneer klaar
        if event.key() == Qt.Key.Key_Space:
            if self.card_complete:
                self.next_card()
            event.accept()
            return

        # F1 = toon antwoorden
        if event.key() == Qt.Key.Key_F1:
            if self.show_answers_button.isEnabled():
                self.show_answers()
            event.accept()
            return

        # Enter/Return: als de input focus heeft, alleen checken en NIET laten doorpropageren
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.answer_input and self.answer_input.hasFocus():
                self.on_check_clicked()
                event.accept()
                return

        super().keyPressEvent(event)