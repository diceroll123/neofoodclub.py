class FoodClubException(Exception):
    """Base exception class for neofoodclub.py"""

    pass


class InvalidData(FoodClubException):
    """An exception that is thrown when improper data is passed into creating NFC objects"""

    pass


class MissingData(FoodClubException):
    """An exception that is thrown when no relevant data is found when creating NFC objects"""

    pass
