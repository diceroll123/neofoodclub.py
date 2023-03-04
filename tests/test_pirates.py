from neofoodclub.nfc import NeoFoodClub
from neofoodclub.pirates import PartialPirate


def test_partialpirate() -> None:
    pirate = PartialPirate(1)  # Dan
    assert pirate.name == "Dan"
    assert pirate.id == 1
    assert pirate.image == "http://images.neopets.com/pirates/fc/fc_pirate_1.gif"


def test_pirate_fa(nfc: NeoFoodClub) -> None:
    assert nfc.arenas[0].pirates[0].fa == 3


def test_pirate_fa_cached(nfc: NeoFoodClub) -> None:
    # because it caches it the first time!
    first_pirate = nfc.arenas[0].pirates[0]
    assert first_pirate.fa == 3
    assert first_pirate.fa == 3


def test_pirate_arena_id(nfc: NeoFoodClub) -> None:
    assert nfc.arenas[0].pirates[0].arena == 0


def test_pirate_index(nfc: NeoFoodClub) -> None:
    assert nfc.arenas[0].pirates[0].index == 1


def test_pirate_opening_odds(nfc: NeoFoodClub) -> None:
    assert nfc.arenas[0].pirates[0].opening_odds == 2


def test_pirate_positive_foods(nfc: NeoFoodClub) -> None:
    assert nfc.arenas[0].pirates[0].positive_foods == (4, 1, 33, 7, 10)


def test_pirate_negative_foods(nfc: NeoFoodClub) -> None:
    assert nfc.arenas[0].pirates[0].negative_foods == (25, 11)


def test_pirate_std_and_er(nfc: NeoFoodClub) -> None:
    pirate = nfc.arenas[0].pirates[0]
    assert pirate.std == 0.47500000000000014
    assert pirate.er == 0.9500000000000003


def test_pirate_without_data(nfc_no_cache: NeoFoodClub) -> None:
    pirate = nfc_no_cache.arenas[0].pirates[0]
    assert pirate.std is None
    assert pirate.er is None


def test_pirate_without_foods(nfc_no_foods: NeoFoodClub) -> None:
    pirate = nfc_no_foods.arenas[0].pirates[0]
    assert pirate.positive_foods == ()
    assert pirate.negative_foods == ()


def test_pirate_won(nfc: NeoFoodClub) -> None:
    shipwreck = nfc.arenas[0]
    sproggie = shipwreck.pirates[0]
    puffo = shipwreck.pirates[1]
    fairfax = shipwreck.pirates[2]
    crossblades = shipwreck.pirates[3]

    assert sproggie.won is True
    assert puffo.won is False
    assert fairfax.won is False
    assert crossblades.won is False


def test_pirate_equality(nfc: NeoFoodClub) -> None:
    shipwreck = nfc.arenas[0]
    sproggie = shipwreck.pirates[0]
    puffo = shipwreck.pirates[1]

    assert sproggie != puffo
