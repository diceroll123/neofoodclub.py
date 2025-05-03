from neofoodclub import NeoFoodClub


def test_arenas_get_pirate_by_id(nfc: NeoFoodClub) -> None:
    assert nfc.arenas.get_pirate_by_id(2).name == "Sproggie"  # type: ignore


def test_arenas_get_pirates_by_id(nfc: NeoFoodClub) -> None:
    pirates = nfc.arenas.get_pirates_by_id([2, 8, 14, 11])

    assert pirates == nfc.arenas[0].pirates


def test_arenas_all_pirates(nfc: NeoFoodClub) -> None:
    assert len(nfc.arenas.get_all_pirates_flat()) == 20


def test_arenas_get_pirates_from_binary(nfc: NeoFoodClub) -> None:
    names = ["Sproggie", "Tailhook", "Buck", "Orvinn", "Federismo"]
    assert names == [p.name for p in nfc.arenas.get_pirates_from_binary(0x88888)]


def test_arenas_pirates(nfc: NeoFoodClub) -> None:
    assert len(nfc.arenas.get_all_pirates()) == 5


def test_arenas_pirate_ids(nfc: NeoFoodClub) -> None:
    assert nfc.arenas.pirate_ids[0] == (2, 8, 14, 11)


def test_arenas_get_arena(nfc: NeoFoodClub) -> None:
    assert nfc.arenas.get_arena(0).name == "Shipwreck"


def test_arenas_iter(nfc: NeoFoodClub) -> None:
    assert len(list(nfc.arenas.arenas)) == 5


def test_arenas_get_pirate_by_id_wrong(nfc: NeoFoodClub) -> None:
    pirate = nfc.arenas.get_pirate_by_id(21)
    assert pirate is None


def test_arenas_length(nfc: NeoFoodClub) -> None:
    assert len(nfc.arenas) == 5


def test_arenas_iterator(nfc: NeoFoodClub) -> None:
    for arena in nfc.arenas:
        assert len(arena.pirates) == 4

    # testing using an iterator twice
    for arena in nfc.arenas:
        assert arena.winner_pirate is not None
