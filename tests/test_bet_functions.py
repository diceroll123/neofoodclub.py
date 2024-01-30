from typing import Sequence, Tuple

import pytest

from neofoodclub import math
from neofoodclub.bets import Bets
from neofoodclub.errors import InvalidAmountHash, InvalidBetHash, InvalidData
from neofoodclub.nfc import NeoFoodClub


def test_odds_iter(nfc_with_bet_amount: NeoFoodClub) -> None:
    # bet amounts are NEEDED to make bustproof + guaranteed wins
    bets = nfc_with_bet_amount.make_bustproof_bets()
    assert len(list(bets.odds)) == 4


def test_guaranteed_win_true(nfc_with_bet_amount: NeoFoodClub) -> None:
    # bet amounts are NEEDED to make bustproof + guaranteed wins
    bets = nfc_with_bet_amount.make_bustproof_bets()
    assert bets.is_guaranteed_win is True


def test_guaranteed_win_false(nfc: NeoFoodClub) -> None:
    bets = nfc.make_max_ter_bets()  # max ter bets are not guaranteed, ever probably
    # don't we wish max ter was guaranteed
    assert bets.is_guaranteed_win is False


def test_make_url(nfc_with_bet_amount: NeoFoodClub) -> None:
    bets = nfc_with_bet_amount.make_bets_from_indices(
        (
            (0, 4, 4, 0, 2),
            (0, 4, 0, 0, 2),
            (1, 4, 4, 0, 2),
            (4, 4, 4, 0, 2),
            (0, 0, 4, 0, 2),
            (1, 4, 0, 0, 2),
            (0, 4, 3, 0, 2),
            (0, 4, 4, 3, 2),
            (3, 4, 4, 0, 2),
            (0, 4, 4, 4, 2),
        ),
        amounts_hash="CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS",
    )
    assert (
        bets.make_url(include_domain=True)
        == "https://neofood.club/#round=7956&b=eukucjuoycaulucepkyrtukyw&a=CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS"
    )


def test_short_hash(nfc: NeoFoodClub) -> None:
    bets = nfc.make_bets_from_hash("f")
    assert bets.bets_hash == "faa"


def test_bets_without_bet_amount(nfc: NeoFoodClub) -> None:
    # when bets have no amounts set, they default to -1000 for each bet.
    bets = nfc.make_max_ter_bets()
    assert bets.bet_amounts.sum() == -10000


def test_bets_set_bet_amount_below_50(nfc: NeoFoodClub) -> None:
    # set bets externally to -1000 for each amount
    # setting numerical values below 50 should min-max the amount to 50
    bets = nfc.make_max_ter_bets()
    bets.bet_amounts = [-1000] * 10
    assert bets.bet_amounts.sum() == 500


def test_bets_set_bet_amount_none(nfc: NeoFoodClub) -> None:
    bets = nfc.make_max_ter_bets()
    bets.bet_amounts = None
    assert bets.amounts_hash == ""


def test_bet_equivalence(
    nfc: NeoFoodClub,
    crazy_test_hash: str,
    crazy_test_indices: Tuple[Tuple[int, ...], ...],
    crazy_test_binaries: Tuple[int, ...],
) -> None:
    crazy_from_hash = nfc.make_bets_from_hash(crazy_test_hash)
    crazy_from_indices = nfc.make_bets_from_indices(crazy_test_indices)
    crazy_from_binaries = nfc.make_bets_from_binaries(*crazy_test_binaries)

    assert crazy_from_hash == crazy_from_indices
    assert crazy_from_hash == crazy_from_binaries


def test_bet_equivalence_with_amount(
    nfc: NeoFoodClub,
) -> None:
    mer_from_hash = nfc.make_bets_from_hash(
        "eukucjuoycaulucepkyrtukyw", amounts_hash="CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS"
    )
    mer_from_indices = nfc.make_bets_from_indices(
        (
            (0, 4, 4, 0, 2),
            (0, 4, 0, 0, 2),
            (1, 4, 4, 0, 2),
            (4, 4, 4, 0, 2),
            (0, 0, 4, 0, 2),
            (1, 4, 0, 0, 2),
            (0, 4, 3, 0, 2),
            (0, 4, 4, 3, 2),
            (3, 4, 4, 0, 2),
            (0, 4, 4, 4, 2),
        ),
        amounts_hash="CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS",
    )
    mer_from_binaries = nfc.make_bets_from_binaries(
        *(
            0x1104,
            0x1004,
            0x81104,
            0x11104,
            0x104,
            0x81004,
            0x1204,
            0x1124,
            0x21104,
            0x1114,
        ),
        amounts_hash="CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS",
    )

    mer_control = nfc.make_bets_from_hash(
        "eukucjuoycaulucepkyrtukyw", amounts=[8000] * 10
    )

    mer_control_two = nfc.make_bets_from_hash("eukucjuoycaulucepkyrtukyw", amount=8000)

    assert mer_control == mer_from_hash
    assert mer_control == mer_from_indices
    assert mer_control == mer_from_binaries
    assert mer_control == mer_control_two


def test_bet_hash_encoding(nfc: NeoFoodClub, crazy_test_hash: str) -> None:
    assert nfc.make_bets_from_hash(crazy_test_hash).bets_hash == crazy_test_hash


def test_bet_indices_encoding(
    nfc: NeoFoodClub, crazy_test_indices: Tuple[Tuple[int, ...], ...]
) -> None:
    assert nfc.make_bets_from_indices(crazy_test_indices).indices == crazy_test_indices


def test_bet_indices_with_amount(
    nfc: NeoFoodClub, crazy_test_indices: Tuple[Tuple[int, ...], ...]
) -> None:
    assert (
        nfc.make_bets_from_indices(crazy_test_indices, amount=8000).indices
        == crazy_test_indices
    )


def test_bet_binaries_encoding(
    nfc: NeoFoodClub, crazy_test_binaries: Tuple[int, ...]
) -> None:
    assert (
        tuple(nfc.make_bets_from_binaries(*crazy_test_binaries)) == crazy_test_binaries
    )


def test_bet_binaries_with_amount(
    nfc: NeoFoodClub, crazy_test_binaries: Tuple[int, ...]
) -> None:
    assert (
        tuple(nfc.make_bets_from_binaries(*crazy_test_binaries, amount=8000))
        == crazy_test_binaries
    )


def test_expected_ratio_equality(crazy_bets: Bets) -> None:
    # There's a discrepancy between what the website says vs what this says.
    # When it comes to expected ratio and net expected, the inconsistent
    # floating point accuracy across different programming languages shows.

    assert crazy_bets.expected_ratio == 3.419054697690152


def test_net_expected_equality_with_amount(
    nfc_with_bet_amount: NeoFoodClub, crazy_test_hash: str
) -> None:
    # There's a discrepancy between what the website says vs what this says.
    # When it comes to expected ratio and net expected, the inconsistent
    # floating point accuracy across different programming languages shows.

    crazy_bets = nfc_with_bet_amount.make_bets_from_hash(crazy_test_hash)
    assert crazy_bets.net_expected == -4742.560161024547


@pytest.mark.parametrize(
    "bet_binaries",
    [
        (0x3,),
        (0x1, 0x3, 0x4),
    ],
)
def test_bets_from_binary_error(
    nfc: NeoFoodClub, bet_binaries: Tuple[int, ...]
) -> None:
    with pytest.raises(InvalidData):
        Bets.from_binary(*bet_binaries, nfc=nfc)


def test_repeating_bets_from_binary(nfc: NeoFoodClub) -> None:
    # duplicates are removed in from_binary, we're making sure of this
    repeating = Bets.from_binary(0x1, 0x1, 0x2, nfc=nfc)
    assert len(repeating) == 2


def test_random_bets(nfc: NeoFoodClub) -> None:
    bets = nfc.make_random_bets()
    assert len(bets) == 10


def test_make_all_bets(nfc: NeoFoodClub) -> None:
    new_nfc = nfc.copy()
    new_nfc.bet_amount = 8000
    bets = new_nfc.make_all_bets(in_order=True)
    assert len(bets) == 3124


def test_make_all_bets_max_ter(nfc: NeoFoodClub) -> None:
    bets = nfc.make_all_bets(max_ter=True)
    assert len(bets) == 3124


def test_make_all_bets_valueerror(nfc: NeoFoodClub) -> None:
    with pytest.raises(ValueError):
        nfc.make_all_bets(max_ter=True, in_order=True)


def test_too_many_bet_amounts_from_binaries(nfc: NeoFoodClub) -> None:
    with pytest.raises(InvalidData):
        nfc.make_bets_from_binaries(0x1, amounts=[50, 50])


def test_invalid_bet_amounts_from_binaries(nfc: NeoFoodClub) -> None:
    with pytest.raises(InvalidAmountHash):
        nfc.make_bets_from_binaries(0x1, amounts_hash="???")


def test_too_many_bet_amounts_from_indices(nfc: NeoFoodClub) -> None:
    with pytest.raises(InvalidData):
        nfc.make_bets_from_indices([(1, 0, 0, 0, 0)], amounts=[50, 50])


def test_invalid_bet_amounts_from_indices(nfc: NeoFoodClub) -> None:
    with pytest.raises(InvalidAmountHash):
        nfc.make_bets_from_indices([(1, 0, 0, 0, 0)], amounts_hash="???")


def test_too_many_bet_amounts_from_hash(nfc: NeoFoodClub) -> None:
    with pytest.raises(InvalidData):
        nfc.make_bets_from_hash("faa", amounts=[50, 50])


def test_invalid_bet_hash(nfc: NeoFoodClub) -> None:
    with pytest.raises(InvalidBetHash):
        nfc.make_bets_from_hash("faz")


def test_invalid_amounts_hash(nfc: NeoFoodClub) -> None:
    with pytest.raises(InvalidAmountHash):
        nfc.make_bets_from_hash("faa", amounts_hash="???")


def test_bet_get_win_units(nfc: NeoFoodClub) -> None:
    assert nfc.make_bets_from_hash("faa").get_win_units() == 2


def test_bet_get_win_np(nfc: NeoFoodClub) -> None:
    bets = nfc.make_bets_from_hash("faa")
    bets.bet_amounts = [8000]
    assert bets.get_win_np() == 16000


@pytest.mark.parametrize(
    ("bet_hash", "bet_indices"),
    [
        (
            "faafa",
            (
                (1, 0, 0, 0, 0),
                (0, 1, 0, 0, 0),
            ),
        ),
        (
            "vyrapsknfvmjbgedicpliqhyb",
            (
                (4, 1, 4, 4, 3),
                (2, 0, 0, 3, 0),
                (3, 3, 2, 0, 2),
                (3, 1, 0, 4, 1),
                (2, 2, 1, 4, 0),
                (1, 1, 1, 0, 4),
                (0, 3, 1, 3, 0),
                (2, 3, 0, 2, 1),
                (1, 3, 3, 1, 1),
                (2, 4, 4, 0, 1),
            ),
        ),
        (
            "ygavkmihfohgphhklexuqmlns",
            (
                (4, 4, 1, 1, 0),
                (0, 4, 1, 2, 0),
                (2, 2, 1, 3, 1),
                (2, 1, 0, 2, 4),
                (1, 2, 1, 1, 3),
                (0, 1, 2, 1, 2),
                (2, 0, 2, 1, 0),
                (4, 4, 3, 4, 0),
                (3, 1, 2, 2, 2),
                (1, 2, 3, 3, 3),
            ),
        ),
        (
            "tpntkpoqjraksvshxfnogctff",
            (
                (3, 4, 3, 0, 2),
                (3, 3, 4, 2, 0),
                (3, 0, 2, 4, 3),
                (1, 1, 4, 3, 2),
                (0, 0, 2, 0, 3),
                (3, 4, 1, 3, 3),
                (1, 2, 4, 3, 1),
                (0, 2, 3, 2, 4),
                (1, 1, 0, 2, 3),
                (4, 1, 0, 1, 0),
            ),
        ),
    ],
)
def test_indices_to_bet_hash(
    bet_hash: str, bet_indices: Sequence[Sequence[int]]
) -> None:
    assert math.bets_hash_value(bet_indices) == bet_hash


def test_bet_with_trailing_none_in_amounts(
    nfc: NeoFoodClub,
) -> None:
    nine_bets = nfc.make_bets_from_hash(
        "abaakaebapkddapudaaqkbaaa", amounts_hash="EmxCoKCoKCglDKUCYqEXkByWBpqzGO"
    )
    assert len(nine_bets) == 9
    assert len(nine_bets.bet_amounts) == 9
