#!/usr/bin/env python
"""
    Account creation functions
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *
from errors             import *
from HTTPSchemas        import *
from Netflix            import *
from Facebook           import *

@handleHTTPRequest(requires_auth=False, 
                   requires_client=True, 
                   http_schema=HTTPAccountNew, 
                   conversion=HTTPAccountNew.convertToAccount,
                   upload='profile_image')
@require_http_methods(["POST"])
def create(request, client_id, http_schema, schema, **kwargs):
    logs.info('account schema passed in: %s' % schema)
    schema = stampedAPI.addAccount(schema, http_schema.profile_image)

    user   = HTTPUser().importAccount(schema)
    logs.user(user.user_id)
    
    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }
    
    return transformOutput(output)

@handleHTTPRequest(requires_auth=False,
                   #requires_client=True,
                   http_schema=HTTPFacebookAccountNew,
                   upload='profile_image')
@require_http_methods(["POST"])
def createUsingFacebook(request, client_id, http_schema, **kwargs):
    # using hte HTTPFacebookAccountNew object, we'll manually create a new Account object
    # first, grab all the information from Facebook using the passed in token
    fb = globalFacebook()
    user = fb.getUserInfo(http_schema.facebook_token)

    account = Account().dataImport(http_schema.dataExport(), overflow=True)
    logs.info(account)
    account.linked_accounts             = LinkedAccounts()
    fb_acct                             = FacebookAccountSchema()
    fb_acct.facebook_id                 = user['id']
    fb_acct.facebook_name               = user['name']
    fb_acct.facebook_screen_name        = user.pop('username', None)
    account.linked_accounts.facebook    = fb_acct
    account.email                       = user.pop('email', None)
    account.bio                         = user.pop('bio', None)
    account.website                     = user.pop('website', None)

    if 'location' in user:
        account.location                = user['location']['name']

    profile_image = 'http://graph.facebook.com/%s/picture?type=large' % user['id']

    account = stampedAPI.addAccount(account, profile_image)
    user   = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }

    return transformOutput(output)

@handleHTTPRequest()
@require_http_methods(["POST"])
def remove(request, authUserId, **kwargs):
    account = stampedAPI.removeAccount(authUserId)
    account = HTTPAccount().dataImport(account.dataExport())
    
    return transformOutput(account.dataExport())


@handleHTTPRequest(parse_request=False)
@require_http_methods(["POST", "GET"])
def settings(request, authUserId, **kwargs):
    if request.method == 'POST':
        ### TODO: Carve out password changes, require original password sent again?
        
        ### TEMP: Generate list of changes. Need to do something better eventually..
        schema = parseRequest(HTTPAccountSettings(), request)
        data   = schema.dataExport()
        
        for k, v in data.iteritems():
            if v == '':
                data[k] = None
        
        ### TODO: Verify email is valid
        account = stampedAPI.updateAccountSettings(authUserId, data)
    else:
        schema  = parseRequest(None, request)
        account = stampedAPI.getAccount(authUserId)
    
    account     = HTTPAccount().importAccount(account)
    
    return transformOutput(account.dataExport())


@handleHTTPRequest(http_schema=HTTPAccountProfile)
@require_http_methods(["POST"])
def update_profile(request, authUserId, data, **kwargs):
    ### TEMP: Generate list of changes. Need to do something better eventually...
    for k, v in data.iteritems():
        if v == '':
            data[k] = None
    
    account = stampedAPI.updateProfile(authUserId, data)
    user    = HTTPUser().importUser(account)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(http_schema=HTTPAccountProfileImage, upload='profile_image')
@require_http_methods(["POST"])
def update_profile_image(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.updateProfileImage(authUserId, http_schema)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(http_schema=HTTPCustomizeStamp)
@require_http_methods(["POST"])
def customize_stamp(request, authUserId, data, **kwargs):
    account = stampedAPI.customizeStamp(authUserId, data)
    user    = HTTPUser().importUser(account)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(requires_auth=False, 
                   requires_client=True, 
                   http_schema=HTTPAccountCheck)
@require_http_methods(["POST"])
def check(request, client_id, http_schema, **kwargs):
    try:
        user = stampedAPI.checkAccount(http_schema.login)
        user = HTTPUser().importUser(user)
        
        ### TODO: REMOVE THIS TEMPORARY CONVERSION!!!!
        try:
            if str(http_schema.login).lower() == str(user.screen_name).lower():
                user.screen_name = str(http_schema.login)
        except:
            pass
        
        return transformOutput(user.dataExport())
    except KeyError:
        response = HttpResponse("not_found")
        response.status_code = 404
        return response
    except Exception:
        response = HttpResponse("invalid_request")
        response.status_code = 400
        return response


@handleHTTPRequest(http_schema=HTTPLinkedAccounts)
@require_http_methods(["POST"])
def linked_accounts(request, authUserId, http_schema, **kwargs):
    linked          = http_schema.exportLinkedAccounts()
    twitterAuth     = http_schema.exportTwitterAuthSchema()
    facebookAuth    = http_schema.exportFacebookAuthSchema()
    netflixAuth     = http_schema.exportNetflixAuthSchema()

    data = {
        'twitter'       : linked.twitter, 
        'facebook'      : linked.facebook, 
        'twitterAuth'   : twitterAuth, 
        'facebookAuth'  : facebookAuth,
        'netflixAuth'   : netflixAuth,
    }
    stampedAPI.updateLinkedAccounts(authUserId, **data)
    
    return transformOutput(True)


@handleHTTPRequest()
@require_http_methods(["POST"])
def removeTwitter(request, authUserId, **kwargs):
    result = stampedAPI.removeLinkedAccount(authUserId, 'twitter')
    
    return transformOutput(True)



@handleHTTPRequest(requires_auth=False, http_schema=HTTPFacebookAuthResponse)
    #parse_request_kwargs={'allow_oauth_token': True})
@require_http_methods(["GET"])
def facebookLoginCallback(request, authUserId, http_schema, **kwargs):
    logs.info('\n### HIT facebookLoginCallback  request: %s  oauth_token: %s   secret: %s' % (request, http_schema.oauth_token, http_schema.secret))
    fb = globalFacebook()

    result = facebook.authorize(http_schema.oauth_token, http_schema.secret)

    logs.info('\n### request auth result: %s' % result)

    netflixAuth = NetflixAuthSchema()
    netflixAuth.netflix_token       = result['oauth_token']
    netflixAuth.netflix_secret      = result['oauth_token_secret']
    netflixAuth.netflix_user_id     = result['user_id']

    logs.info('\nnetflixAuth %s' % netflixAuth)

    stampedAPI.updateLinkedAccounts(http_schema.stamped_oauth_token, netflixAuth=netflixAuth)

    return createNetflixLoginResponse(authUserId)


@handleHTTPRequest()
@require_http_methods(["POST"])
def removeFacebook(request, authUserId, **kwargs):
    result = stampedAPI.removeLinkedAccount(authUserId, 'facebook')
    
    return transformOutput(True)


@handleHTTPRequest(http_schema=HTTPFindUser, 
                   parse_request_kwargs={'obfuscate':['q']})
@require_http_methods(["POST"])
def alertFollowersFromTwitter(request, authUserId, http_schema, **kwargs):
    q = http_schema.q.split(',')
    twitterIds = []

    for item in q:
        try:
            number = int(item)
            twitterIds.append(item)
        except:
            msg = 'Invalid twitter id: %s' % item
            logs.warning(msg)

    result = stampedAPI.alertFollowersFromTwitter(authUserId, twitterIds)
    
    return transformOutput(result)


@handleHTTPRequest(http_schema=HTTPFindUser, 
                   parse_request_kwargs={'obfuscate':['q']})
@require_http_methods(["POST"])
def alertFollowersFromFacebook(request, authUserId, http_schema, **kwargs):
    q = http_schema.q.split(',')
    facebookIds = []

    for item in q:
        try:
            number = int(item)
            facebookIds.append(item)
        except:
            msg = 'Invalid facebook id: %s' % item
            logs.warning(msg)

    result = stampedAPI.alertFollowersFromFacebook(authUserId, facebookIds)
    
    return transformOutput(result)

@handleHTTPRequest()
@require_http_methods(["POST"])
def removeTwitter(request, authUserId, **kwargs):
    result = stampedAPI.removeLinkedAccount(authUserId, 'twitter')

    return transformOutput(True)

def createNetflixLoginResponse(authUserId):
    netflix = globalNetflix()
    secret, url = netflix.getLoginUrl(authUserId)

    response                = HTTPEndpointResponse()
    source                  = HTTPActionSource()
    source.source           = 'netflix'
    source.link             = url
    #source.endpoint         = 'https://dev.stamped.com/v0/account/linked/netflix/login_callback.json'
    response.setAction('netflix_login', 'Login to Netflix', [source])

    return transformOutput(response.dataExport())

@handleHTTPRequest()
@require_http_methods(["GET"])
def netflixLogin(request, authUserId, http_schema, **kwargs):
    return createNetflixLoginResponse(authUserId)

@handleHTTPRequest(requires_auth=False, http_schema=HTTPNetflixAuthResponse,
                   parse_request_kwargs={'allow_oauth_token': True})
@require_http_methods(["GET"])
def netflixLoginCallback(request, authUserId, http_schema, **kwargs):
    logs.info('\n### HIT netflixLoginCallback  request: %s  oauth_token: %s   secret: %s' % (request, http_schema.oauth_token, http_schema.secret))
    netflix = globalNetflix()

    result = netflix.requestUserAuth(http_schema.oauth_token, http_schema.secret)
    logs.info('\n### request auth result: %s' % result)

    netflixAuth = NetflixAuthSchema()
    netflixAuth.netflix_token       = result['oauth_token']
    netflixAuth.netflix_secret      = result['oauth_token_secret']
    netflixAuth.netflix_user_id     = result['user_id']

    logs.info('\nnetflixAuth %s' % netflixAuth)

    stampedAPI.updateLinkedAccounts(http_schema.stamped_oauth_token, netflixAuth=netflixAuth)

    return createNetflixLoginResponse(authUserId)




@handleHTTPRequest(http_schema=HTTPNetflixId)
@require_http_methods(["POST"])
def addToNetflixInstant(request, authUserId, http_schema, **kwargs):
    logs.info('\n### ATTEMPTING TO ADD TO NETFLIX with netflix_id: %s' % http_schema.netflix_id)
    try:
        result = stampedAPI.addToNetflixInstant(authUserId, http_schema.netflix_id)
    except StampedHTTPError as e:
        if e.code == 401:
            return createNetflixLoginResponse(authUserId)
            # return login endpoint action
        else:
            raise e
    if result == None:
        return createNetflixLoginResponse(authUserId)

    logs.info('\n### SUCCESSFULLY ADDED TO NETFLIX INSTANT QUEUE')

    response = HTTPEndpointResponse()

    source                  = HTTPActionSource()
    source.source           = 'stamped_confirm'
    source.source_data      = 'We have added this item to your Netflix Queue.'
    #source.endpoint         = 'https://dev.stamped.com/v0/account/linked/netflix/login_callback.json'
    response.setAction('netflix_login', 'Login to Netflix', [source])
    #TODO throw status codes on error
    #TODO return an HTTPAction
    return transformOutput(response.dataExport())

@handleHTTPRequest(http_schema=HTTPNetflixId)
@require_http_methods(["POST"])
def removeFromNetflixInstant(request, authUserId, http_schema, **kwargs):
    try:
        result = stampedAPI.addToNetflixQueue(authUserId, http_schema.netflix_id)
    except StampedHTTPError as e:
        if e.code == 401:
            #redirect to sign in
            raise e
        else:
            raise e
    #TODO throw status codes on error
    #TODO return an HTTPAction
    return transformOutput(True)





@handleHTTPRequest(http_schema=HTTPAccountChangePassword, 
                   parse_request_kwargs={'obfuscate':['old_password', 'new_password']})
@require_http_methods(["POST"])
def change_password(request, authUserId, http_schema, **kwargs):
    new = http_schema.new_password
    old = http_schema.old_password
    
    stampedAuth.verifyPassword(authUserId, old)
    result = stampedAuth.updatePassword(authUserId, new)
    
    return transformOutput(True)


@handleHTTPRequest(requires_auth=False, http_schema=HTTPEmail)
@require_http_methods(["POST"])
def reset_password(request, client_id, http_schema, **kwargs):
    stampedAuth.resetPassword(http_schema.email)

    return transformOutput(True)


@handleHTTPRequest()
@require_http_methods(["GET"])
def show_alerts(request, authUserId, **kwargs):
    account  = stampedAPI.getAccount(authUserId)
    settings = HTTPAccountAlerts().importAccount(account)

    return transformOutput(settings.dataExport())


@handleHTTPRequest(http_schema=HTTPAccountAlerts)
@require_http_methods(["POST"])
def update_alerts(request, authUserId, http_schema, **kwargs):
    account  = stampedAPI.updateAlerts(authUserId, http_schema)
    settings = HTTPAccountAlerts().importAccount(account)

    return transformOutput(settings.dataExport())


@handleHTTPRequest(http_schema=HTTPAPNSToken)
@require_http_methods(["POST"])
def update_apns(request, authUserId, http_schema, **kwargs):
    if len(http_schema.token) != 64:
        raise StampedInputError('Invalid token length')
    
    stampedAPI.updateAPNSToken(authUserId, http_schema.token)
    return transformOutput(True)


@handleHTTPRequest(http_schema=HTTPAPNSToken)
@require_http_methods(["POST"])
def remove_apns(request, authUserId, http_schema, **kwargs):
    if len(http_schema.token) != 64:
        raise StampedInputError('Invalid token length')
    
    stampedAPI.removeAPNSTokenForUser(authUserId, http_schema.token)
    return transformOutput(True)

