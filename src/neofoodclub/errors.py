class FoodClubException(Exception):
    """Base exception class for neofoodclub.py"""

    pass


class InvalidData(FoodClubException):
    """An exception that is thrown when improper data is passed into creating NFC objects"""

    pass


class NoPositiveArenas(FoodClubException):
    """An exception that is thrown when there are no positive arenas while creating a bustproof set"""

    pass
