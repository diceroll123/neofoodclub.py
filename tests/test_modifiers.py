import datetime

import pytest
from neofoodclub.neofoodclub import Modifier


def test_empty_modifer():
    m = Modifier()
    assert m.value == 0


def test_cc_perk_modifer():
    m = Modifier(cc_perk=True)
    assert m.cc_perk == True


def test_general_modifer():
    m = Modifier(Modifier.GENERAL)
    assert m.general == True


def test_opening_odds_modifer():
    m = Modifier(Modifier.OPENING)
    assert m.opening_odds == True


def test_reverse_modifer():
    m = Modifier(Modifier.REVERSE)
    assert m.reverse == True


def test_full_modifer():
    m = Modifier(Modifier.ALL_MODIFIERS)
    assert m.general == True
    assert m.opening_odds == True
    assert m.reverse == True


def test_from_type_modifer():
    m = Modifier.from_type(Modifier.LETTERS, cc_perk=True)
    assert m.general == True
    assert m.opening_odds == True
    assert m.reverse == True
    assert m.cc_perk == True


def test_modifer_letters_equality():
    m = Modifier.from_type(Modifier.LETTERS)
    m1 = Modifier(Modifier.ALL_MODIFIERS)
    assert m.letters == m1.letters


def test_modifer_custom_odds():
    m = Modifier()
    m.custom_odds = {1: 2}
    assert m.custom_odds == {1: 2}


def test_modifer_copy_equality():
    m = Modifier(
        Modifier.ALL_MODIFIERS,
        cc_perk=True,
        custom_odds={1: 2},
        custom_time=datetime.time(hour=12, minute=0),
    )

    assert m == m.copy()


def test_modifer_nfc(nfc):
    m = Modifier()
    m.nfc = nfc

    mnfc = m.nfc

    assert mnfc is not None
    assert mnfc.round == 7956


def test_modifer_time_typeerror():
    with pytest.raises(TypeError):
        m = Modifier()
        m.time = ""  # type: ignore


def test_modifer_cc_perk_typeerror():
    with pytest.raises(TypeError):
        m = Modifier()
        m.cc_perk = ""  # type: ignore


def test_modifer_custom_odds_typeerror():
    with pytest.raises(TypeError):
        m = Modifier()
        m.custom_odds = ""  # type: ignore


def test_modifer_nfc_typeerror():
    with pytest.raises(TypeError):
        m = Modifier()
        m.nfc = ""  # type: ignore
