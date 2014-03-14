"""Exceptions used all over the place"""


class HTTPError(Exception):
    """
    Exception representing an HTTP response error.

    .. attribute:: status_code

        HTTP status code

    .. attribute:: message

        Informative error message, if available
    """

    def __init__(self, status_code, message, original=None):
        self.status_code = status_code
        self.message = message
        self.original = original

    def __str__(self):
        return ("{0}({1!r}, {2!r}, original={3!r})"
                .format(self.__class__.__name__,
                        self.status_code, self.message, self.original))


class BadApiError(Exception):
    """Exception used to mark bad behavior from the API"""
    pass


class BadApiWarning(UserWarning):
    """Warning to mark bad behavior from the API"""
    pass


class OperationFailure(Exception):
    """Something went wrong // failed expectations somewhere.."""
    pass
