import pytest

from neofoodclub import NeoFoodClub


@pytest.mark.parametrize("pirate_binary", [0x8, 0x88, 0x888])
def test_tenbet_generation_three_pirates(nfc: NeoFoodClub, pirate_binary: int) -> None:
    assert all(
        bet & pirate_binary == pirate_binary
        for bet in nfc.make_tenbet_bets(pirate_binary).binaries
    )


@pytest.mark.parametrize("pirate_binary", [0x0, 0x8888, 0x88888])
def test_tenbet_generation_zero_and_five_pirates(
    nfc: NeoFoodClub,
    pirate_binary: int,
) -> None:
    with pytest.raises(ValueError):
        nfc.make_tenbet_bets(pirate_binary)


def test_tenbet_generation(nfc: NeoFoodClub) -> None:
    assert nfc.make_tenbet_bets(0x888).bets_hash == "eggvgygfbgtggbgugfqgbgibg"


def test_tenbet_generation_with_bet_amount(nfc_with_bet_amount: NeoFoodClub) -> None:
    assert (
        nfc_with_bet_amount.make_tenbet_bets(0x888).bets_hash
        == "oghqglgjvgmgjqgvgivgjghbg"
    )
