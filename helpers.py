def norm(s: str) -> str:
    return s.strip()


def start_card(card: dict):
    """
    Initialiseert de sessiestatus voor een kaart.
    """
    all_answers = [norm(a) for a in card["back"] if norm(a)]
    remaining_answers = set(all_answers)

    return {
        "all_answers": all_answers,
        "remaining_answers": remaining_answers,
    }


def check_answer(user_input: str, state: dict):
    """
    Controleert of input correct is.
    Geeft terug: (success: bool, status: str, normalized_answer: str | None)
    """
    user = norm(user_input)

    if not user:
        return False, "empty", None

    if user in state["remaining_answers"]:
        state["remaining_answers"].remove(user)
        return True, "correct", user

    return False, "wrong", None

