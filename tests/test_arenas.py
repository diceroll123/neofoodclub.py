from neofoodclub.neofoodclub import NeoFoodClub


def test_arenas_get_pirate_by_id(nfc: NeoFoodClub):
    assert nfc.arenas.get_pirate_by_id(2).name == "Sproggie"


def test_arenas_get_pirates_by_id(nfc: NeoFoodClub):
    pirates = nfc.arenas.get_pirates_by_id(2, 8, 14, 11)

    assert pirates == nfc.arenas[0].pirates


def test_arenas_all_pirates(nfc: NeoFoodClub):
    assert len(nfc.arenas.all_pirates) == 20


def test_arenas_get_pirates_from_binary(nfc: NeoFoodClub):
    names = ["Sproggie", "Tailhook", "Buck", "Orvinn", "Federismo"]
    assert names == [p.name for p in nfc.arenas.get_pirates_from_binary(0x88888)]


def test_arenas_pirates(nfc: NeoFoodClub):
    assert len(nfc.arenas.pirates) == 5


def test_arenas_pirate_ids(nfc: NeoFoodClub):
    assert nfc.arenas.pirate_ids[0] == [2, 8, 14, 11]


def test_arenas_get_arena(nfc: NeoFoodClub):
    assert nfc.arenas.get_arena(0).name == "Shipwreck"


def test_arenas_iter(nfc: NeoFoodClub):
    assert len(list(nfc.arenas)) == 5
