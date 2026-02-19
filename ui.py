from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QFileDialog,
    QDialog, QDialogButtonBox
)


from storage import save_deck, load_deck
from PySide6.QtCore import Qt
from helpers import start_card, check_answer


class FlashcardApp(QMainWindow):
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
        self.deck_path = None  # Pas gevuld na opslaan

    def setup_ui(self):
        self.setWindowTitle("Flashcard App")
        self.resize(900, 600)

        # ===== MENU =====
        self.menu = self.menuBar()
        self.deck_menu = self.menu.addMenu("Deck")

        self.new_action = self.deck_menu.addAction("Nieuw deck")
        self.new_action.triggered.connect(self.create_new_deck)

        self.open_action = self.deck_menu.addAction("Deck laden")
        self.open_action.triggered.connect(self.load_deck_dialog)

        self.save_action = self.deck_menu.addAction("Deck opslaan")
        self.save_action.triggered.connect(self.save_current_deck)

        # ===== STYLE =====
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
                font-size: 32px;
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

        # ===== HOOFDLAYOUT (VERTICAAL) =====
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # ===== KAART (FULL WIDTH) =====
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
        main_layout.addWidget(self.card_frame)

        # ===== INPUT (FULL WIDTH) =====
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Typ een antwoord en druk Enter…")
        self.answer_input.returnPressed.connect(self.on_check_clicked)
        main_layout.addWidget(self.answer_input)

        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.feedback_label)

        # ===== ONDERSTE GEDEELTE 50/50 =====
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # ---- LINKS: BEWERKEN ----
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.add_card_button = QPushButton("Nieuwe kaart")
        self.add_card_button.clicked.connect(self.add_card)
        left_layout.addWidget(self.add_card_button)

        self.edit_cards_button = QPushButton("Kaarten bewerken")
        left_layout.addWidget(self.edit_cards_button)

        left_layout.addStretch()

        # ---- RECHTS: STUDY ACTIES ----
        self.show_answers_button = QPushButton("Toon antwoorden")
        self.show_answers_button.clicked.connect(self.show_answers)
        right_layout.addWidget(self.show_answers_button)

        self.next_button = QPushButton("Volgende kaart")
        self.next_button.clicked.connect(self.next_card)
        right_layout.addWidget(self.next_button)

        right_layout.addStretch()

        bottom_layout.addLayout(left_layout, 1)
        bottom_layout.addLayout(right_layout, 1)

        main_layout.addLayout(bottom_layout)

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)



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
        self.next_button.setDisabled(True)
        self.save_action.setEnabled(False)
        self.status_label.setText("Geen deck geladen.")

    def set_active_deck(self, deck: dict):
        self.current_deck = deck
        self.cards = deck["cards"]
        self.current_index = 0
        self.deck_path = None  # nieuw deck is nog niet opgeslagen
        self.status_label.setText("Nieuw deck aangemaakt. Eerst opslaan.")

        if self.cards:
            self.load_card(self.cards[self.current_index])
        else:
            self.front_label.setText("Deck is leeg.")

        # Study pas na opslaan:
        self.update_ui_for_unsaved_deck()


    def update_ui_for_unsaved_deck(self):
        self.answer_input.setDisabled(True)
        self.next_button.setDisabled(True)
        self.save_action.setEnabled(True)

    def update_ui_for_saved_deck(self):
        self.answer_input.setDisabled(False)
        self.next_button.setDisabled(False)
        self.save_action.setEnabled(True)

    def create_new_deck(self):
        deck = {"name": "Nieuw deck", "cards": []}
        self.set_active_deck(deck)

    def save_current_deck(self):
        if not self.current_deck:
            return

        if not self.deck_path:
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Deck opslaan",
                "",
                "Deck files (*.json)"
            )
            if not filepath:
                return

            if not filepath.lower().endswith(".json"):
                filepath += ".json"

            self.deck_path = filepath

        save_deck(self.current_deck, self.deck_path)

        self.update_ui_for_saved_deck()

        if self.cards:
            self.current_index = 0
            self.load_card(self.cards[self.current_index])
        else:
            self.front_label.setText("Deck is leeg.")

    def add_card(self):
        if not self.current_deck:
            return

        dialog = AddCardDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            front, back = dialog.get_data()

            if not front or not back:
                self.status_label.setText("Voorkant en minstens één antwoord vereist.")
                return

            card = {
                "front": front,
                "back": back
            }

            self.current_deck["cards"].append(card)
            self.cards = self.current_deck["cards"]

            self.status_label.setText("Kaart toegevoegd.")

    def load_deck_dialog(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Deck laden",
            "",
            "Deck files (*.json)"
        )

        if not filepath:
            return  # gebruiker annuleert

        try:
            deck = load_deck(filepath)
        except Exception as e:
            self.status_label.setText(f"Fout bij laden: {e}")
            return

        self.deck_path = filepath
        self.set_active_deck(deck)
        self.update_ui_for_saved_deck()

        if self.cards:
            self.current_index = 0
            self.load_card(self.cards[self.current_index])
        else:
            self.front_label.setText("Deck is leeg.")

        self.status_label.setText("Deck geladen.")
    
    def show_answers(self):
        if not self.current_card:
            return

        answers = ", ".join(self.current_card["back"])
        self.feedback_label.setText(f"Antwoorden: {answers}")





class AddCardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Kaart toevoegen")
        self.resize(400, 300)

        layout = QVBoxLayout()

        self.front_input = QLineEdit()
        self.front_input.setPlaceholderText("Voorkant")
        layout.addWidget(self.front_input)

        self.back_inputs = []

        # Standaard 3 antwoordvelden
        for i in range(3):
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
        back = [
            field.text().strip()
            for field in self.back_inputs
            if field.text().strip()
        ]

        return front, back
