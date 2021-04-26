from neofoodclub import NeoFoodClub

if __name__ == "__main__":
    # if you happen to have a valid "loaded" NeoFoodClub URL handy,
    url = "/#round=8025&pirates=[[12,11,9,14],[6,7,10,20],[5,17,18,2],[13,3,16,4],[1,19,8,15]]&openingOdds=[[1,2,13,8,3],[1,4,4,13,2],[1,4,3,4,4],[1,11,13,2,5],[1,11,3,12,2]]&currentOdds=[[1,2,13,8,3],[1,4,4,13,2],[1,3,3,4,5],[1,13,13,2,7],[1,12,3,13,2]]&foods=[[27,26,39,15,4,2,33,25,12,10],[19,17,21,10,24,33,39,13,5,26],[4,5,40,12,22,24,37,26,11,15],[40,9,38,8,2,34,31,20,27,7],[28,27,21,19,24,7,31,5,16,39]]&timestamp=2021-04-26T19:22:16+00:00"

    # let's say you have an old account and can bet 15K per bet.
    amount = 15000

    # create a NeoFoodClub object using the URL
    nfc = NeoFoodClub.from_url(url, bet_amount=amount)

    # generate max TER bets tailored to your bet amount
    max_ter_bets = nfc.make_max_ter_set()

    print(nfc.make_url(max_ter_bets))

    # let's say Charity Corner (https://www.jellyneo.net/?go=charity_corner) is back up and you've got the FC perk!
    # we can generate 15 bets if you just tell the modifier to do so!
    nfc.modifier.cc_perk = True
    max_ter_bets = nfc.make_max_ter_set()

    print(nfc.make_url(max_ter_bets))
