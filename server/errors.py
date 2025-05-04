class InvalidTokenException(Exception):
    pass


class UnauthorizedTokenException(Exception):
    pass


class BWSAPIRateLimitExceededException(Exception):
    pass


class MissingSecretException(Exception):
    pass


class UnknownKeyException(Exception):
    pass


class SendRequestException(Exception):
    pass


class UnknownOrgIdException(Exception):
    pass


class InvalidSecretIDException(Exception):
    pass


class NoDefaultOrgIdException(Exception):
    pass


class NoDefaultRegionException(Exception):
    pass
