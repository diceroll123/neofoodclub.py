import datetime

import pytest
from neofoodclub.neofoodclub import Modifier, NeoFoodClub


def test_empty_modifier():
    m = Modifier()
    assert m.value == 0


def test_cc_perk_modifier():
    m = Modifier()
    m.cc_perk = True
    assert m.cc_perk == True


def test_cc_perk_modifier_from_init():
    m = Modifier(cc_perk=True)
    assert m.cc_perk == True


def test_general_modifier():
    m = Modifier(Modifier.GENERAL)
    assert m.general == True


def test_opening_odds_modifier():
    m = Modifier(Modifier.OPENING)
    assert m.opening_odds == True


def test_reverse_modifier():
    m = Modifier(Modifier.REVERSE)
    assert m.reverse == True


def test_full_modifier():
    m = Modifier(Modifier.ALL_MODIFIERS)
    assert m.general == True
    assert m.opening_odds == True
    assert m.reverse == True


def test_from_type_modifier():
    m = Modifier.from_type(Modifier.LETTERS, cc_perk=True)
    assert m.general == True
    assert m.opening_odds == True
    assert m.reverse == True
    assert m.cc_perk == True


def test_modifier_letters_equality():
    m = Modifier.from_type(Modifier.LETTERS)
    m1 = Modifier(Modifier.ALL_MODIFIERS)
    assert m.letters == m1.letters


def test_modifier_custom_odds():
    m = Modifier()
    m.custom_odds = {1: 2}
    assert m.custom_odds == {1: 2}


def test_modifier_copy_equality():
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
def test_modifier_custom_odds_error(pirate_id: int, pirate_odds: int):
    m = Modifier()
    with pytest.raises(ValueError):
        m.custom_odds = {pirate_id: pirate_odds}


def test_modifier_time_typeerror():
    with pytest.raises(TypeError):
        m = Modifier()
        m.time = ""  # type: ignore


def test_modifier_cc_perk_typeerror():
    with pytest.raises(TypeError):
        m = Modifier()
        m.cc_perk = ""  # type: ignore


def test_modifier_custom_odds_typeerror():
    with pytest.raises(TypeError):
        m = Modifier()
        m.custom_odds = ""  # type: ignore


def test_modifier_time_with_nfc(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier()
    new_nfc.modifier.time = datetime.time(hour=12, minute=0)

    assert new_nfc.modifier.time == datetime.time(hour=12, minute=0)


def test_modifier_with_none_time_and_reset(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier()
    new_nfc.soft_reset()

    assert new_nfc.modifier.time is None


def test_modifier_time_and_reset_no_start(nfc: NeoFoodClub):
    new_data = nfc.to_dict()
    # remove the start time of the round so we can have an indeterminate start time
    new_data.pop("start")
    new_nfc = NeoFoodClub(new_data)
    new_nfc.modifier = Modifier(custom_time=datetime.time(hour=12, minute=0))
    new_nfc.soft_reset()  # should hit the "None" return value from _get_round_time

    assert new_nfc.modifier.time == datetime.time(hour=12, minute=0)


def test_modifier_time_and_reset(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(custom_time=datetime.time(hour=12, minute=0))
    new_nfc.soft_reset()

    assert new_nfc.modifier.time == datetime.time(hour=12, minute=0)


def test_modifier_time(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier()
    new_nfc.modifier.time = datetime.time(hour=12, minute=0)

    assert new_nfc.modifier.time == datetime.time(hour=12, minute=0)


def test_modifier_time_rollback_changes(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(custom_time=datetime.time(hour=12, minute=0))

    assert new_nfc.custom_odds == new_nfc.opening_odds


def test_modifier_time_rollforward_changes(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier(
        custom_time=datetime.time(hour=23, minute=47, second=20)
    )

    assert new_nfc.custom_odds == new_nfc.current_odds


def test_modifier_custom_odds_reset(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    new_nfc.modifier = Modifier()
    new_nfc.modifier.custom_odds = {1: 2, 2: 2, 3: 2}

    assert new_nfc.custom_odds != new_nfc.opening_odds


def test_modifier_nfc(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    m = Modifier()
    assert m.nfc is None
    new_nfc.modifier = m
    assert m.nfc is new_nfc
