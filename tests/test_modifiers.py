import datetime

import pytest

from neofoodclub.modifier import Modifier
from neofoodclub.nfc import NeoFoodClub


def test_empty_modifier() -> None:
    m = Modifier()
    assert m.value == 0


def test_cc_perk_modifier() -> None:
    m = Modifier()
    m.cc_perk = True
    assert m.cc_perk is True


def test_cc_perk_modifier_from_init() -> None:
    m = Modifier(cc_perk=True)
    assert m.cc_perk is True


def test_general_modifier() -> None:
    m = Modifier(Modifier.GENERAL)
    assert m.general is True


def test_opening_odds_modifier() -> None:
    m = Modifier(Modifier.OPENING)
    assert m.opening_odds is True


def test_reverse_modifier() -> None:
    m = Modifier(Modifier.REVERSE)
    assert m.reverse is True


def test_full_modifier() -> None:
    m = Modifier(Modifier.ALL_MODIFIERS)
    assert m.general is True
    assert m.opening_odds is True
    assert m.reverse is True


def test_from_type_modifier() -> None:
    m = Modifier.from_type(Modifier.LETTERS, cc_perk=True)
    assert m.general is True
    assert m.opening_odds is True
    assert m.reverse is True
    assert m.cc_perk is True


def test_modifier_letters_equality() -> None:
    m = Modifier.from_type(Modifier.LETTERS)
    m1 = Modifier(Modifier.ALL_MODIFIERS)
    assert m.letters == m1.letters


def test_modifier_custom_odds() -> None:
    m = Modifier()
    m.custom_odds = {1: 2}
    assert m.custom_odds == {1: 2}


def test_modifier_copy_equality() -> None:
    m = Modifier(
        Modifier.ALL_MODIFIERS,
        cc_perk=True,
        custom_odds={1: 2},
        custom_time=datetime.time(hour=12, minute=0),
    )

    assert m == m.copy()


@pytest.mark.parametrize(
    "pirate_id,pirate_odds",
    [
        (0, 2),  # out of bounds pirate_id
        (21, 2),  # out of bounds pirate_id
        (1, 1),  # out of bounds pirate_odds
        (1, 14),  # out of bounds pirate_odds
    ],
)
def test_modifier_custom_odds_error(pirate_id: int, pirate_odds: int) -> None:
    m = Modifier()
    with pytest.raises(ValueError):
        m.custom_odds = {pirate_id: pirate_odds}


def test_modifier_time_typeerror() -> None:
    with pytest.raises(TypeError):
        m = Modifier()
        m.time = ""  # type: ignore


def test_modifier_cc_perk_typeerror() -> None:
    with pytest.raises(TypeError):
        m = Modifier()
        m.cc_perk = ""  # type: ignore


def test_modifier_custom_odds_typeerror() -> None:
    with pytest.raises(TypeError):
        m = Modifier()
        m.custom_odds = ""  # type: ignore


def test_modifier_time_with_nfc(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier()
    new_nfc.modifier.time = datetime.time(hour=12, minute=0)

    assert new_nfc.modifier.time == datetime.time(hour=12, minute=0)


def test_modifier_with_none_time_and_reset(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier()
    new_nfc.soft_reset()

    assert new_nfc.modifier.time is None


def test_modifier_time_and_reset_no_start(nfc: NeoFoodClub) -> None:
    new_data = nfc.to_dict()
    # remove the start time of the round so we can have an indeterminate start time
    new_data.pop("start")
    new_nfc = NeoFoodClub(new_data)
    new_nfc.modifier = Modifier(custom_time=datetime.time(hour=12, minute=0))
    new_nfc.soft_reset()  # should hit the "None" return value from _get_round_time

    assert new_nfc.modifier.time == datetime.time(hour=12, minute=0)


def test_modifier_time_and_reset(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(custom_time=datetime.time(hour=12, minute=0))
    new_nfc.soft_reset()

    assert new_nfc.modifier.time == datetime.time(hour=12, minute=0)


def test_modifier_time(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier()
    new_nfc.modifier.time = datetime.time(hour=12, minute=0)

    assert new_nfc.modifier.time == datetime.time(hour=12, minute=0)


def test_modifier_time_rollback_changes(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(custom_time=datetime.time(hour=12, minute=0))

    assert new_nfc.custom_odds == new_nfc.opening_odds


def test_modifier_time_rollforward_changes(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(
        custom_time=datetime.time(hour=23, minute=47, second=20)
    )

    assert new_nfc.custom_odds == new_nfc.current_odds


def test_modifier_custom_odds_reset(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier()
    new_nfc.modifier.custom_odds = {1: 2, 2: 2, 3: 2}

    assert new_nfc.custom_odds != new_nfc.opening_odds


def test_modifier_nfc(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    m = Modifier()
    assert m.nfc is None
    new_nfc.modifier = m
    assert m.nfc is new_nfc
