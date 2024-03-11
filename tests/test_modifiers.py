import datetime

import pytest

from neofoodclub import Modifier, NeoFoodClub


def test_empty_modifier() -> None:
    m = Modifier(Modifier.EMPTY)
    assert m.value == 0


def test_is_charity_corner_modifier() -> None:
    m = Modifier(Modifier.CHARITY_CORNER)
    assert m.is_charity_corner is True


def test_general_modifier() -> None:
    m = Modifier(Modifier.GENERAL)
    assert m.is_general is True


def test_opening_odds_modifier() -> None:
    m = Modifier(Modifier.OPENING_ODDS)
    assert m.is_opening_odds is True


def test_reverse_modifier() -> None:
    m = Modifier(Modifier.REVERSE)
    assert m.is_reverse is True


def test_full_modifier() -> None:
    m = Modifier(Modifier.ALL_MODIFIERS)
    assert m.is_general is True
    assert m.is_opening_odds is True
    assert m.is_reverse is True
    assert m.is_charity_corner is True


def test_modifier_custom_odds() -> None:
    m = Modifier(Modifier.EMPTY, custom_odds={1: 2})
    assert m.custom_odds == {1: 2}


def test_modifier_copy_equality() -> None:
    m = Modifier(
        Modifier.ALL_MODIFIERS,
        custom_odds={1: 2},
        custom_time=datetime.time(hour=12, minute=0),
    )

    assert m == m.copy()


@pytest.mark.parametrize(
    ("pirate_id", "pirate_odds"),
    [
        (0, 2),  # out of bounds pirate_id
        (21, 2),  # out of bounds pirate_id
        (1, 1),  # out of bounds pirate_odds
        (1, 14),  # out of bounds pirate_odds
    ],
)
def test_modifier_custom_odds_error(pirate_id: int, pirate_odds: int) -> None:
    with pytest.raises(ValueError):
        Modifier(Modifier.EMPTY, custom_odds={pirate_id: pirate_odds})


def test_modifier_time_with_nfc(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(Modifier.EMPTY, time=datetime.time(hour=12, minute=0))

    assert new_nfc.modifier.time == datetime.time(hour=12, minute=0)


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
        custom_time=datetime.time(hour=23, minute=47, second=20),
    )

    assert new_nfc.custom_odds == new_nfc.current_odds


def test_modifier_custom_odds_reset(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(Modifier.EMPTY, custom_odds={1: 2, 2: 2, 3: 2})

    assert new_nfc.custom_odds != new_nfc.opening_odds
