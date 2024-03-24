import datetime
import json

import orjson
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
    m = Modifier(custom_odds={1: 2})
    assert m.custom_odds == {1: 2}


def test_modifier_copy_equality() -> None:
    m = Modifier(
        Modifier.ALL_MODIFIERS,
        custom_odds={1: 2},
        custom_time=datetime.time(hour=12, minute=0).isoformat(),
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
    with pytest.raises(BaseException):
        Modifier(custom_odds={pirate_id: pirate_odds})


def test_modifier_time_with_nfc(nfc: NeoFoodClub) -> None:
    modifier = Modifier(
        custom_time=datetime.time(hour=12, minute=0).isoformat(),
    )
    new_nfc = nfc.copy(modifier=modifier)

    assert new_nfc.modifier.custom_time == datetime.time(hour=12, minute=0).isoformat()


def test_modifier_time_and_reset_no_start(nfc: NeoFoodClub) -> None:
    new_data = orjson.loads(nfc.to_json())
    # remove the start time of the round so we can have an indeterminate start time
    new_data.pop("start")
    modifier = Modifier(
        custom_time=datetime.time(hour=12, minute=0).isoformat(),
    )
    new_nfc = NeoFoodClub(json.dumps(new_data)).copy(modifier=modifier)

    assert new_nfc.modifier.custom_time == datetime.time(hour=12, minute=0).isoformat()


def test_modifier_time_and_reset(nfc: NeoFoodClub) -> None:
    modifier = Modifier(
        custom_time=datetime.time(hour=12, minute=0).isoformat(),
    )

    new_nfc = nfc.copy(modifier=modifier)
    assert new_nfc.modifier.custom_time == datetime.time(hour=12, minute=0).isoformat()


def test_modifier_time_rollback_changes(nfc: NeoFoodClub) -> None:
    modifier = Modifier(
        custom_time=datetime.time(hour=15, minute=47, second=42).isoformat(),
    )
    new_nfc = nfc.copy(modifier=modifier)

    assert new_nfc.custom_odds == new_nfc.opening_odds


def test_modifier_time_rollback_changes_with_modifier(nfc: NeoFoodClub) -> None:
    modifier = Modifier(
        custom_time=datetime.time(hour=15, minute=47, second=42).isoformat(),
    )
    new_nfc = nfc.copy()
    new_nfc.with_modifier(modifier=modifier)

    assert new_nfc.custom_odds == new_nfc.opening_odds


def test_modifier_time_rollforward_changes(nfc: NeoFoodClub) -> None:
    modifier = Modifier(
        custom_time=datetime.time(hour=15, minute=47, second=19).isoformat(),
    )
    new_nfc = nfc.copy(modifier=modifier)

    assert nfc.current_odds == new_nfc.custom_odds


def test_modifier_custom_odds_reset(nfc: NeoFoodClub) -> None:
    modifier = Modifier(custom_odds={1: 2, 2: 2, 3: 2})
    new_nfc = nfc.copy(modifier=modifier)

    assert new_nfc.current_odds != new_nfc.opening_odds
