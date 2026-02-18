import json
from pathlib import Path


def save_deck(deck: dict, filepath: str):
    """
    Slaat een deck op als JSON.
    """
    path = Path(filepath)

    with path.open("w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)


def load_deck(filepath: str) -> dict:
    """
    Laadt een deck uit JSON.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Bestand niet gevonden: {filepath}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    validate_deck(data)

    return data


def validate_deck(deck: dict):
    """
    Minimale validatie van deck-structuur.
    """
    if not isinstance(deck, dict):
        raise ValueError("Deck moet een dictionary zijn.")

    if "name" not in deck:
        raise ValueError("Deck mist 'name'.")

    if "cards" not in deck:
        raise ValueError("Deck mist 'cards'.")

    if not isinstance(deck["cards"], list):
        raise ValueError("'cards' moet een lijst zijn.")

    for card in deck["cards"]:
        if "front" not in card or "back" not in card:
            raise ValueError("Elke kaart moet 'front' en 'back' bevatten.")

        if not isinstance(card["back"], list):
            raise ValueError("'back' moet een lijst zijn.")
