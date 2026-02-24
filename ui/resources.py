TRANSLATIONS = {
    "nl": {
        "menu_deck": "&Deck",
        "menu_new_deck": "Nieuw deck",
        "menu_load_deck": "Deck laden",
        "menu_save_deck": "Deck opslaan",
        "menu_options": "&Opties",
        "menu_dark_theme": "Donker thema",
        "menu_repeat": "Fout beantwoorde kaarten herhalen",
        "menu_flip_cards": "Kaarten omdraaien",
        "menu_language": "&Taal",
        "no_deck": "Geen deck geladen",
        "new_card": "Nieuwe kaart",
        "edit_cards": "Kaarten bewerken",
        "flashcard": "Oefenen",
        "practice": "Invullen",
        "show_answers": "Toon antwoorden",
        "next_card": "Volgende kaart",
        "stop": "Stoppen",
        "flip": "Draaien",
        "deck_finished": "Deck doorgewerkt!",
        "score_text": "Deck doorgewerkt!  {score:.0f}% correct",
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
        "load_error": "Fout bij laden",
        "new_deck_name": "Nieuw deck",
        "unsaved_warning_title": "Niet opgeslagen wijzigingen",
        "unsaved_warning_text": "Het deck heeft niet-opgeslagen wijzigingen. Wil je opslaan voordat je afsluit?",
        "unsaved_save": "Opslaan",
        "unsaved_discard": "Afsluiten",
        "unsaved_cancel": "Annuleren",
        "close_after_finish": "Sluiten",
    },
    "en": {
        "menu_deck": "&Deck",
        "menu_new_deck": "New deck",
        "menu_load_deck": "Load deck",
        "menu_save_deck": "Save deck",
        "menu_options": "&Options",
        "menu_dark_theme": "Dark theme",
        "menu_repeat": "Repeat incorrectly answered cards",
        "menu_flip_cards": "Flip cards",
        "menu_language": "&Language",
        "no_deck": "No deck loaded",
        "new_card": "New card",
        "edit_cards": "Edit cards",
        "flashcard": "Study",
        "practice": "Test yourself",
        "show_answers": "Show answers",
        "next_card": "Next card",
        "stop": "Stop",
        "flip": "Flip",
        "deck_finished": "Deck completed!",
        "score_text": "Deck completed!  {score:.0f}% correct",
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
        "load_error": "Error loading",
        "new_deck_name": "New deck",
        "unsaved_warning_title": "Unsaved changes",
        "unsaved_warning_text": "The deck has unsaved changes. Do you want to save before quitting?",
        "unsaved_save": "&Save",
        "unsaved_discard": "&Quit",
        "unsaved_cancel": "&Cancel",
        "close_after_finish": "Close",
        
    }
}

T = TRANSLATIONS["nl"]  # actieve taal

STYLESHEET_DARK = """

    QMenuBar {
        background-color: #121212;
        color: white;
    }
    QMenuBar::item:selected {
        background-color: #2d2d2d;
    }
    QMenu {
        background-color: #1e1e1e;
        color: white;
        border: 1px solid #2a2a2a;
    }
    QMenu::item:selected {
        background-color: #2563eb;
    }
    QMenu::item:disabled {
        color: #555555;
    }
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
    QLabel#DeckLabel {
        font-size: 22px;
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

    QMenuBar {
        background-color: #f5f5f5;
        color: #111;
    }
    QMenuBar::item:selected {
        background-color: #d0d0d0;
    }
    QMenu {
        background-color: #ffffff;
        color: #111;
        border: 1px solid #ccc;
    }
    QMenu::item:selected {
        background-color: #2563eb;
        color: white;
    }
    QMenu::item:disabled {
        color: #aaaaaa;
    }
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
    QLabel#DeckLabel {
        font-size: 22px;
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