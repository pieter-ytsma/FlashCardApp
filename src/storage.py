import json
from pathlib import Path


def save_deck(deck: dict, filepath: str):
    """
    Slaat een deck atomisch op als JSON.
    Schrijft eerst naar een tijdelijk bestand, dan pas replace() naar de echte locatie.
    Zo raakt de JSON nooit corrupt bij een crash tijdens schrijven.
    """
    path = Path(filepath)
    tmp = path.with_suffix(".tmp")

    # Zorg dat schema_version altijd aanwezig is
    if "schema_version" not in deck:
        deck["schema_version"] = 1

    with tmp.open("w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)

    tmp.replace(path)


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
    Striktere validatie van deck-structuur en inhoud.
    """

    if not isinstance(deck, dict):
        raise ValueError("Deck moet een dictionary zijn.")

    if "name" not in deck or not isinstance(deck["name"], str):
        raise ValueError("Deck mist geldige 'name'.")

    if "cards" not in deck or not isinstance(deck["cards"], list):
        raise ValueError("Deck mist geldige 'cards' lijst.")

    for i, card in enumerate(deck["cards"], start=1):

        if not isinstance(card, dict):
            raise ValueError(f"Kaart {i} is geen geldig object.")

        if "front" not in card or "back" not in card:
            raise ValueError(f"Kaart {i} mist 'front' of 'back'.")

        if not isinstance(card["front"], str):
            raise ValueError(f"Kaart {i}: 'front' moet tekst zijn.")

        if not isinstance(card["back"], list):
            raise ValueError(f"Kaart {i}: 'back' moet een lijst zijn.")

        if len(card["back"]) == 0:
            raise ValueError(f"Kaart {i} heeft geen antwoorden.")

        if len(card["back"]) > 6:
            raise ValueError(f"Kaart {i} heeft meer dan 6 antwoorden.")

        for j, answer in enumerate(card["back"], start=1):
            if not isinstance(answer, str):
                raise ValueError(f"Kaart {i}, antwoord {j} moet tekst zijn.")

            if not answer.strip():
                raise ValueError(f"Kaart {i}, antwoord {j} is leeg.")
