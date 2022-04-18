class FoodClubException(Exception):
    """Base exception class for neofoodclub.py"""

    pass


class InvalidData(FoodClubException):
    """An exception that is thrown when improper data is passed into creating NFC objects"""

    pass


class NoPositiveArenas(FoodClubException):
    """An exception that is thrown when there are no positive arenas while creating a bustproof set"""

    pass


class InvalidBetHash(FoodClubException):
    """An exception that is thrown when an improper string is used to create bets from a hash"""

    pass


class InvalidAmountHash(FoodClubException):
    """An exception that is thrown when an improper string is used to create bet amounts from a hash"""

    pass
