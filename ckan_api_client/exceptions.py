"""Exceptions used all over the place"""


class HTTPError(Exception):
    """
    Exception representing an HTTP response error.

    .. attribute:: status_code

        HTTP status code

    .. attribute:: message

        Informative error message, if available
    """

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return "HTTPError [{0}]: {1}".format(self.status_code, self.message)


class BadApiError(Exception):
    """Exception used to mark bad behavior from the API"""
    pass


class BadApiWarning(UserWarning):
    """Warning to mark bad behavior from the API"""
    pass


class OperationFailure(Exception):
    """Something went wrong // failed expectations somewhere.."""
    pass
