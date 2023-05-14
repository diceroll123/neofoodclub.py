class FoodClubException(Exception):
    """Base exception class for neofoodclub.py."""



class InvalidData(FoodClubException):
    """An exception that is thrown when improper data is passed into creating NFC objects."""



class NoPositiveArenas(FoodClubException):
    """An exception that is thrown when there are no positive arenas while creating a bustproof set."""



class InvalidBetHash(FoodClubException):
    """An exception that is thrown when an improper string is used to create bets from a hash."""



class InvalidAmountHash(FoodClubException):
    """An exception that is thrown when an improper string is used to create bet amounts from a hash."""

