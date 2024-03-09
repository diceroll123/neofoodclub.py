from neofoodclub import NeoFoodClub


def test_mer_bets_With_bet_amouunt(
    nfc_with_bet_amount_logit_model: NeoFoodClub,
) -> None:
    bets = nfc_with_bet_amount_logit_model.make_max_ter_bets()

    # this may break if the logit data changes!
    assert set(bets.binaries) == {
        0x408,
        0x88008,
        0x82008,
        0x80408,
        0x88108,
        0x80008,
        0x82108,
        0x80108,
        0x80018,
        0x80118,
    }
