from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QLineEdit
)
from PySide6.QtCore import Qt

from ..resources import T
from ..widgets import DeletableLineEdit

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

        save_btn = QPushButton(T["save_close"] + "  (Ctrl+S)")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setAutoDefault(False)
        save_btn.setDefault(False)
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        discard_btn = QPushButton(T["close"] + "  (Esc)")
        discard_btn.setAutoDefault(False)
        discard_btn.setDefault(False)
        discard_btn.clicked.connect(self.reject)
        btn_row.addWidget(discard_btn)

        outer.addLayout(btn_row)

        self.setLayout(outer)

        # Start met 1 antwoordveld
        self.add_answer_field()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.accept()
            event.accept()
            return
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