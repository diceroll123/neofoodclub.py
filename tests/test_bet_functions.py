from typing import Tuple

import pytest
from neofoodclub.errors import InvalidData
from neofoodclub.neofoodclub import Bets, Modifier, NeoFoodClub


def test_odds_iter(nfc_with_bet_amount: NeoFoodClub):
    # bet amounts are NEEDED to make bustproof + guaranteed wins
    bets = nfc_with_bet_amount.make_bustproof_bets()
    assert len(list(bets.odds)) == 4


def test_guaranteed_win_true(nfc_with_bet_amount: NeoFoodClub):
    # bet amounts are NEEDED to make bustproof + guaranteed wins
    bets = nfc_with_bet_amount.make_bustproof_bets()
    assert bets.is_guaranteed_win is True


def test_guaranteed_win_false(nfc: NeoFoodClub):
    bets = nfc.make_max_ter_bets()  # max ter bets are not guaranteed, ever probably
    # don't we wish max ter was guaranteed
    assert bets.is_guaranteed_win is False


def test_make_url_no_bet_amount(nfc: NeoFoodClub):
    bets = nfc.make_max_ter_bets()
    assert (
        bets.make_url(include_domain=False)
        == "/#round=7956&b=eukucjuoycaulucepkyreynyc"
    )


def test_make_url(nfc_with_bet_amount: NeoFoodClub):
    bets = nfc_with_bet_amount.make_max_ter_bets()
    assert (
        bets.make_url(include_domain=False)
        == "/#round=7956&b=eukucjuoycaulucepkyrtukyw&a=CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS"
    )


def test_make_url_all_data(nfc: NeoFoodClub, test_max_ter_15_bets: str):
    new_nfc = NeoFoodClub(nfc.to_dict())
    new_nfc.modifier = Modifier(cc_perk=True)
    bets = new_nfc.make_max_ter_bets()
    assert bets.make_url(all_data=True) == f"https://neofood.club{test_max_ter_15_bets}"


def test_short_hash(nfc: NeoFoodClub):
    bets = nfc.make_bets_from_hash("f")
    assert bets.bets_hash == "faa"


def test_bets_without_bet_amount(nfc: NeoFoodClub):
    # when bets have no amounts set, they default to -1000 for each bet.
    bets = nfc.make_max_ter_bets()
    assert bets.bet_amounts.sum() == -10000


def test_bets_set_bet_amount_below_50(nfc: NeoFoodClub):
    # set bets externally to -1000 for each amount
    # setting numerical values below 50 should min-max the amount to 50
    bets = nfc.make_max_ter_bets()
    bets.bet_amounts = [-1000] * 10
    assert bets.bet_amounts.sum() == 500


def test_bets_set_bet_amount_none(nfc: NeoFoodClub):
    bets = nfc.make_max_ter_bets()
    bets.bet_amounts = None
    assert bets.amounts_hash == ""


def test_bet_equivalence(
    nfc: NeoFoodClub,
    crazy_test_hash: str,
    crazy_test_indices: Tuple[Tuple[int, ...], ...],
    crazy_test_binaries: Tuple[int, ...],
):
    crazy_from_hash = nfc.make_bets_from_hash(crazy_test_hash)
    crazy_from_indices = nfc.make_bets_from_indices(crazy_test_indices)
    crazy_from_binaries = nfc.make_bets_from_binaries(*crazy_test_binaries)

    assert crazy_from_hash == crazy_from_indices
    assert crazy_from_hash == crazy_from_binaries


def test_bet_equivalence_with_amount(
    nfc: NeoFoodClub,
):
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


def test_bet_hash_encoding(nfc: NeoFoodClub, crazy_test_hash: str):
    assert nfc.make_bets_from_hash(crazy_test_hash).bets_hash == crazy_test_hash


def test_bet_indices_encoding(
    nfc: NeoFoodClub, crazy_test_indices: Tuple[Tuple[int, ...], ...]
):
    assert nfc.make_bets_from_indices(crazy_test_indices).indices == crazy_test_indices


def test_bet_indices_with_amount(
    nfc: NeoFoodClub, crazy_test_indices: Tuple[Tuple[int, ...], ...]
):
    assert (
        nfc.make_bets_from_indices(crazy_test_indices, amount=8000).indices
        == crazy_test_indices
    )


def test_bet_binaries_encoding(nfc: NeoFoodClub, crazy_test_binaries: Tuple[int, ...]):
    assert (
        tuple(nfc.make_bets_from_binaries(*crazy_test_binaries)) == crazy_test_binaries
    )


def test_bet_binaries_with_amount(
    nfc: NeoFoodClub, crazy_test_binaries: Tuple[int, ...]
):
    assert (
        tuple(nfc.make_bets_from_binaries(*crazy_test_binaries, amount=8000))
        == crazy_test_binaries
    )


def test_net_expected_equality_no_amount(crazy_bets: Bets):
    assert crazy_bets.net_expected == 0.0


def test_expected_ratio_equality(crazy_bets: Bets):
    # There's a discrepancy between what the website says vs what this says.
    # When it comes to expected ratio and net expected, the inconsistent
    # floating point accuracy across different programming languages shows.

    assert crazy_bets.expected_ratio == 3.419054697690152


def test_net_expected_equality_with_amount(
    nfc_with_bet_amount: NeoFoodClub, crazy_test_hash: str
):
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
def test_bets_from_binary_error(nfc: NeoFoodClub, bet_binaries: Tuple[int, ...]):
    with pytest.raises(InvalidData):
        Bets.from_binary(*bet_binaries, nfc=nfc)


def test_repeating_bets_from_binary(nfc: NeoFoodClub):
    # duplicates are removed in from_binary, we're making sure of this
    repeating = Bets.from_binary(0x1, 0x1, 0x2, nfc=nfc)
    assert len(repeating) == 2


def test_random_bets(nfc: NeoFoodClub):
    bets = nfc.make_random_bets()
    assert len(bets) == 10


def test_random_gambit_bets(nfc: NeoFoodClub):
    bets = nfc.make_gambit_bets(random=True)
    assert bets.is_gambit is True
    assert len(bets) == 10


def test_gambit_bets_equivalence(nfc: NeoFoodClub):
    bets = nfc.make_gambit_bets(five_bet=0x88888)
    assert bets.bets_hash == "ggfgggbgbgbbggfaggaggffgf"


def test_unit_bets_empty(nfc: NeoFoodClub):
    bets = nfc.make_units_bets(400000)  # higher than possible
    assert len(bets) == 0


def test_unit_bets_equivalence(nfc: NeoFoodClub):
    bets = nfc.make_units_bets(20)  # higher than possible
    assert bets.bets_hash == "uukycjalewfxoamecokcsanfc"


def test_random_unit_bets(nfc: NeoFoodClub):
    bets = nfc.make_units_bets(20)
    assert len(bets) == 10


def test_bustproof_with_two_positives(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    # setting Buck to 4 sets arena to positive, giving us 2 positives
    new_nfc.modifier = Modifier(custom_odds={19: 4})
    bets = new_nfc.make_bustproof_bets()
    assert bets.is_bustproof is True


def test_bustproof_with_three_positives(nfc: NeoFoodClub):
    new_nfc = nfc.copy()
    # setting Buck to 4 sets arena to positive, giving us 2 positives
    # setting Crossblades to 12 sets arena to positive, giving us 3 positives
    new_nfc.modifier = Modifier(custom_odds={19: 4, 11: 12})
    bets = new_nfc.make_bustproof_bets()
    assert bets.is_bustproof is True


def test_bustproof_equivalence(nfc_with_bet_amount: NeoFoodClub):
    # bet amounts are NEEDED to make bustproof + guaranteed wins
    bets = nfc_with_bet_amount.make_bustproof_bets()
    assert bets.bets_hash == "aafacaapae"
