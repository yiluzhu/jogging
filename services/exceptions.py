

class UnauthenticatedError(Exception):
    """Raise when the client must authenticate itself to get the requested response.
    """


class NoAccessError(Exception):
    """Raise when the client is known but has no access to the requested response.
    """


class UnknownUser(Exception):
    """Raise when the client tries to operate on a user that does not exist.
    """


class UnknownRecord(Exception):
    """Raise when the client tries to operate on a record id that does not exist.
    """


class DuplicateUser(Exception):
    """Raise when the there are duplicate users.
    """


class MissingInformation(Exception):
    """Raise when the request miss necessary information.
    """


class UserStillHasRecords(Exception):
    """Raise when the request tries to delete a user that still has records.
    """
