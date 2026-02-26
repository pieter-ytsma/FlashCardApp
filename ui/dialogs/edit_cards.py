from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QFileDialog, QWidget, QScrollArea
)
from PySide6.QtCore import Qt

from ..resources import T
from ..widgets import DeletableLineEdit
import copy

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

        save_btn = QPushButton(T["save_close"] + "  (Ctrl+S)")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        discard_btn = QPushButton(T["close"] + "  (Esc)")
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
        if event.key() == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.accept()
            event.accept()
            return
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
            number_label.setStyleSheet("font-size: 18px; font-weight: 600;")
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

    def accept(self):
        for card in self.cards:
            card["front"] = card["front"].strip()
            card["back"] = [
                a.strip()
                for a in card["back"]
                if isinstance(a, str) and a.strip()
            ]

        super().accept()