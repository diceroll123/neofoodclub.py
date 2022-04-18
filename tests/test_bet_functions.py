from typing import Tuple

from neofoodclub.neofoodclub import Bets, NeoFoodClub


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
        == "/#round=7956&b=aukacfukycuulacauutcbukdc"
    )


def test_make_url(nfc_with_bet_amount: NeoFoodClub):
    bets = nfc_with_bet_amount.make_max_ter_bets()
    assert (
        bets.make_url(include_domain=False)
        == "/#round=7956&b=aukacfukycuulacauutcbukdc&a=CXSCXSCXSCXSCXSCXSCXSCXSCXSCXS"
    )


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


def test_bet_hash_encoding(nfc: NeoFoodClub, crazy_test_hash: str):
    assert nfc.make_bets_from_hash(crazy_test_hash).bets_hash == crazy_test_hash


def test_bet_indices_encoding(
    nfc: NeoFoodClub, crazy_test_indices: Tuple[Tuple[int, ...], ...]
):
    assert nfc.make_bets_from_indices(crazy_test_indices).indices == crazy_test_indices


def test_bet_binaries_encoding(nfc: NeoFoodClub, crazy_test_binaries: Tuple[int, ...]):
    assert (
        tuple(nfc.make_bets_from_binaries(*crazy_test_binaries)) == crazy_test_binaries
    )


def test_net_expected_equality_no_amount(crazy_bets: Bets):
    assert crazy_bets.net_expected == 0.0


def test_expected_ratio_equality(crazy_bets: Bets):
    # There's a discrepancy between what the website says vs what this says.
    # When it comes to expected ratio and net expected, the inconsistent
    # floating point accuracy across different programming languages shows.

    assert crazy_bets.expected_ratio == 4.749039403822004


def test_net_expected_equality_with_amount(
    nfc_with_bet_amount: NeoFoodClub, crazy_test_hash: str
):
    # There's a discrepancy between what the website says vs what this says.
    # When it comes to expected ratio and net expected, the inconsistent
    # floating point accuracy across different programming languages shows.

    crazy_bets = nfc_with_bet_amount.make_bets_from_hash(crazy_test_hash)
    assert crazy_bets.net_expected == -3632.7030091926185