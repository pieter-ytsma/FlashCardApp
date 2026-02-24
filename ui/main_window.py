from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QFileDialog,
    QDialog, QDialogButtonBox, QScrollArea, QToolButton
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







class FlashcardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icon.ico"))

        self.current_deck = None
        self.cards = []
        self.deck_path = None
        self._dirty = False

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
            name = Path(self.deck_path).stem if self.deck_path else self.current_deck["name"]
            dirty = " *" if self._dirty else ""
            self.setWindowTitle(f"Flashcard App - {name}{dirty}")
            self.deck_label.setText(name[:1].upper() + name[1:] if name else name)
        else:
            self.setWindowTitle("Flashcard App")
            self.deck_label.setText(T["no_deck"])

    def set_active_deck(self, deck: dict):
        self.current_deck = deck
        self.cards = deck["cards"]
        self.deck_path = None
        self._dirty = True
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

        filepath, _ = QFileDialog.getOpenFileName(
            self, T["load_dialog"], "", "Deck files (*.json)"
        )
        if not filepath:
            return

        try:
            deck = load_deck(filepath)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, T["load_error"], str(e))
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