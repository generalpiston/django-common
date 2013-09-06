
from rest_framework import exceptions, status


__all__ = ['ActionMissingError', 'WrongActionError']


class ActionMissingError(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Missing action.'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail


class WrongActionError(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Missing action.'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail
