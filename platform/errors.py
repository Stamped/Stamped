#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

class Fail(Exception):
    pass

error_kinds = set([
    'stamped_error',
    'forbidden',
    'invalid_credentials',
    'bad_request',
    'illegal_action',
    'already_exists',
    'not_found',
    'internal_server_error',
    'third_party',
])

class StampedHTTPError(Exception):
    def __init__(self, code, kind=None, msg=None):
        Exception.__init__(self, msg)
        self.code = code
        self.msg  = msg
        self.kind = kind
        
        if msg is not None:
            logs.warning(msg)

# Schema Exceptions

class SchemaTypeError(TypeError):
    def __init__(self, msg=None, desc=None):
        TypeError.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

        if msg is not None:
            logs.warning(msg)

class SchemaKeyError(KeyError):
    def __init__(self, msg=None, desc=None):
        KeyError.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

        if msg is not None:
            logs.warning(msg)

class SchemaValidationError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

        if msg is not None:
            logs.warning(msg)

# Basic Stamped Exceptions

class StampedException(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

        if msg is not None:
            logs.warning(msg)


class StampedPermissionsError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedIllegalActionError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedInputError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedUnavailableError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedDuplicationError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedAuthError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc
        
        if msg is not None:
            logs.warning(msg)

class StampedInternalError(Exception):
    def __init__(self, msg=None, desc=None):
        Exception.__init__(self, msg)
        self.msg  = msg
        self.desc = desc

        if msg is not None:
            logs.warning(msg)


class StampedMissingParametersError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedNotLoggedInError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)


# Specific Stamped Exceptions

    # Database-related Errors
class StampedDocumentNotFoundError(StampedUnavailableError):
    def __init__(self, msg=None):
        StampedUnavailableError.__init__(self, msg)

class StampedInvalidObjectIdError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

    # Internal Errors
class StampedInvalidRelationshipError(StampedInternalError):
    def __init__(self, msg=None):
        StampedInternalError.__init__(self, msg)


    # Accounts
class StampedInvalidPasswordError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedInvalidScreenNameError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedInvalidEmailError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedInvalidWebsiteError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedInvalidStampColorsError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedDuplicateEmailError(StampedDuplicationError):
    def __init__(self, msg=None):
        StampedDuplicationError.__init__(self, msg)

class StampedDuplicateScreenNameError(StampedDuplicationError):
    def __init__(self, msg=None):
        StampedDuplicationError.__init__(self, msg)

class StampedAccountNotFoundError(StampedUnavailableError):
    def __init(self, msg=None):
        StampedUnavailableError.__init__(self, msg)

class StampedBlackListedScreenNameError(StampedIllegalActionError):
    def __init(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)

class StampedAlreadyStampedAuthError(StampedIllegalActionError):
    def __init(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)


        # Users
class StampedViewUserPermissionsError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)


    # Auth
class StampedInvalidClientError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedInvalidCredentialsError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)


    # Linked Accounts
class StampedLinkedAccountAlreadyExistsError(StampedIllegalActionError):
    def __init__(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)

class StampedLinkedAccountDoesNotExistError(StampedIllegalActionError):
    def __init__(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)

class StampedLinkedAccountError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)

class StampedMissingLinkedAccountTokenError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedNetflixNoInstantWatchError(StampedIllegalActionError):
    def __init(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)

class StampedLinkedAccountIsAuthError(StampedIllegalActionError):
    def __init(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)

class StampedNoSharingForLinkedAccountError(StampedIllegalActionError):
    def __init(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)

    # Third Party Errors

class StampedThirdPartyError(StampedInputError):
    def __init__(self, msg=None):
        StampedInputError.__init__(self, msg)

class StampedThirdPartyInvalidCredentialsError(StampedInvalidCredentialsError):
    def __init__(self, msg=None):
        StampedInvalidCredentialsError.__init__(self, msg)

    # Stamps
class StampedOutOfStampsError(StampedIllegalActionError):
    def __init__(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)

class StampedRemoveStampPermissionsError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)

class StampedViewStampPermissionsError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)

class StampedAddCommentPermissionsError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)

class StampedRemoveCommentPermissionsError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)

class StampedViewCommentPermissionsError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)

class StampedBlockedUserError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)

    # Friendships
class StampedInvalidFriendshipError(StampedIllegalActionError):
    def __init__(self, msg=None):
        StampedIllegalActionError.__init__(self, msg)

class StampedFriendshipCheckPermissionsError(StampedPermissionsError):
    def __init__(self, msg=None):
        StampedPermissionsError.__init__(self, msg)