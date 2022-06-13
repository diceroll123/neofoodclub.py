from typing import List, Tuple

from neofoodclub.nfc import NeoFoodClub


def test_first_arena_name_and_id(nfc: NeoFoodClub):
    assert nfc.arenas[0].name == "Shipwreck"
    assert nfc.arenas[0].id == 0


def test_first_arena_best(nfc: NeoFoodClub):
    best_in_first_arena: List[Tuple[str, int, int]] = [  # name, odds, binary
        ("Sproggie", 2, 0x80000),
        ("Fairfax", 3, 0x20000),
        ("Crossblades", 5, 0x10000),
        ("Puffo", 13, 0x40000),
    ]
    compare = [(p.name, p.odds, p.binary) for p in nfc.arenas[0].best]
    assert best_in_first_arena == compare


def test_first_arena_pirate_ids(nfc: NeoFoodClub):
    pirate_ids = (2, 8, 14, 11)  # Sproggie, Puffo, Fairfax, Crossblades
    assert pirate_ids == nfc.arenas[0].ids


def test_first_arena_odds(nfc: NeoFoodClub):
    assert 1.11025641025641 == nfc.arenas[0].odds


def test_first_arena_ratio(nfc: NeoFoodClub):
    assert -0.09930715935334855 == (nfc.arenas[0].ratio)


def test_first_arena_negative(nfc: NeoFoodClub):
    assert nfc.arenas[0].negative is True


def test_first_arena_foods(nfc: NeoFoodClub):
    assert nfc.arenas[0].foods == (26, 25, 4, 9, 21, 1, 33, 11, 7, 10)


def test_first_arena_get_pirate_using_getitem(nfc: NeoFoodClub):
    assert nfc.arenas[0][0].name == "Sproggie"


def test_arena_iter(nfc: NeoFoodClub):
    assert len(list(nfc.arenas[0])) == 4
