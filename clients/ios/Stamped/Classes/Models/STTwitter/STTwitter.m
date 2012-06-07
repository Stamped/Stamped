//
//  STTwitter.m
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import "STTwitter.h"
#import "STOAuth.h"
#import "EGOHTTPRequest.h"
#import "STAuth.h"
#import "JSON.h"

#define kTwitterConsumer @"kn1DLi7xqC6mb5PPwyXw"
#define kTwitterSecretApersand @"AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU&"
#define kTwitterSecret @"AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU"

static id __instance;

@implementation STTwitter
@synthesize access=_access;
@synthesize twitterUser;
@synthesize accountStore = _accountStore;

+ (STTwitter*)sharedInstance {
    
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        __instance = [[[self class] alloc] init];
    });
    
    return __instance;
    
}

- (id)init {
    if ((self = [super init])) {
        _access = NO;
    }
    return self;
}


#pragma mark - Request Signing

- (void)signRequest:(EGOHTTPRequest*)request params:(NSArray*)params token:(NSString*)token {
    
    NSMutableArray *authArray = [[NSMutableArray alloc] init];
    [STOAuth addParamValue:[STOAuth nonce] forName:@"oauth_nonce" toArray:authArray];
    [STOAuth addParamValue:@"HMAC-SHA1" forName:@"oauth_signature_method" toArray:authArray];
    [STOAuth addParamValue:[STOAuth timestamp] forName:@"oauth_timestamp" toArray:authArray];
    [STOAuth addParamValue:kTwitterConsumer forName:@"oauth_consumer_key" toArray:authArray];
    [STOAuth addParamValue:@"1.0" forName:@"oauth_version" toArray:authArray];
    
    for (NSDictionary *dic in params) {
        [STOAuth addParamValue:[[dic allValues] lastObject] forName:[[dic allKeys] lastObject] toArray:authArray];
    }
    
    NSString *signature = [STOAuth signatureForParams:authArray request:request token:token];
    [STOAuth addParamValue:signature forName:@"oauth_signature" toArray:authArray];
    
    NSMutableString *authString = [[NSMutableString alloc] initWithString:@"OAuth "];
    [authString appendString:[STOAuth paramStringForParams:authArray joiner:@", " shouldQuote:YES shouldSort:NO]];
    [request addRequestHeader:@"Authorization" value:authString];
    [authArray release];
    [authString release];
    
}


#pragma mark - Twitter Authentication

- (NSDictionary*)paramsForString:(NSString*)string {
    
    NSMutableDictionary *foundParameters = [[NSMutableDictionary alloc] initWithCapacity:10];
	if (string) {
        
		NSScanner *parameterScanner = [[NSScanner alloc] initWithString:string];
		NSString *name = nil;
		NSString *value = nil;
		
		while (![parameterScanner isAtEnd]) {
			name = nil;
			value = nil;
			
			[parameterScanner scanUpToString:@"=" intoString:&name];
			[parameterScanner scanString:@"=" intoString:NULL];
			[parameterScanner scanUpToString:@"&" intoString:&value];
			[parameterScanner scanString:@"&" intoString:NULL];		
			
			if (name && value) {
				[foundParameters setObject:[value stringByReplacingPercentEscapesUsingEncoding:NSUTF8StringEncoding] forKey:name];
			}
		}
		
        [parameterScanner release];
		parameterScanner=nil;
        
	}
    return [foundParameters autorelease];
    
}

- (void)handleOpenURL:(NSURL*)url {
    
    NSString *string = [url query];
    NSDictionary *params = [self paramsForString:string];
    if (params && [params objectForKey:@"oauth_token"] && [params objectForKey:@"oauth_verifier"]) {
        [self accessWithToken:[params objectForKey:@"oauth_token"] verifier:[params objectForKey:@"oauth_verifier"]];
    } else {
        [STEvents postEvent:EventTypeTwitterAuthFailed];
    }
    
}

- (void)accessWithToken:(NSString*)token verifier:(NSString*)verifier {
    
    __block EGOHTTPRequest *_request = [[EGOHTTPRequest alloc] initWithURL:[NSURL URLWithString:@"https://api.twitter.com/oauth/access_token"] completion:^(id request, NSError *error) {
        
        if ([request responseStatusCode] == 200) {
            
            NSDictionary *params = [self paramsForString:[_request responseString]];
            //[[GiftureSettings sharedSettings] setTwitterUserInfo:params];
            _twitterUserAuth = [params retain];
            [STEvents postEvent:EventTypeTwitterAuthFinished object:_twitterUserAuth];
            
        } else {
            
            [STEvents postEvent:EventTypeTwitterAuthFailed];
            
        }
        
    }];
    
    [_request setRequestMethod:@"POST"];
    NSMutableArray *array = [[NSMutableArray alloc] init];
    [array addObject:[NSDictionary dictionaryWithObject:token forKey:@"oauth_token"]];
    [array addObject:[NSDictionary dictionaryWithObject:verifier forKey:@"oauth_verifier"]];
    [self signRequest:_request params:array token:[NSString stringWithFormat:@"%@&%@", kTwitterConsumer, kTwitterSecret]];
    [array release];
    [_request startAsynchronous];
    [_request release];
    
}

- (void)auth {
    
    __block EGOHTTPRequest *_request = [[EGOHTTPRequest alloc] initWithURL:[NSURL URLWithString:@"https://api.twitter.com/oauth/request_token"] completion:^(id request, NSError *error) {
        
        NSDictionary *params = [self paramsForString:[request responseString]];
        NSString *string = [NSString stringWithFormat:@"http://api.twitter.com/oauth/authorize?oauth_token=%@", [params objectForKey:@"oauth_token"]];
        [[UIApplication sharedApplication] openURL:[NSURL URLWithString:string]];

    }];
    
    [_request setRequestMethod:@"POST"];
    [self signRequest:_request params:[NSArray arrayWithObject:[NSDictionary dictionaryWithObject:@"stamped://twitter" forKey:@"oauth_callback"]] token:kTwitterSecretApersand];      
    [_request startAsynchronous];
    [_request release];
}


#pragma mark - Twitter Request Handling

- (void)twitterRequestWithPath:(NSString*)path completion:(TwitterRequestHandler)handler {
    
    __block EGOHTTPRequest *_request = [[EGOHTTPRequest alloc] initWithURL:[NSURL URLWithString:path] completion:^(id request, NSError *error) {
        
        if (error == nil && [request responseStatusCode] == 200) {
            
            NSError *_error = nil;
            id data = [[_request responseString] JSONValue];
            handler(data, _error);
            
        } else {
            
            handler(nil, error);
            
        }
        
    }];
    
    NSMutableArray *array = [[NSMutableArray alloc] init];
    [array addObject:[NSDictionary dictionaryWithObject:[self twitterToken] forKey:@"oauth_token"]];
    [self signRequest:_request params:array token:[self twitterTokenSecret]];
    [array release];
    [_request startAsynchronous];
    [_request release];
    
}


#pragma mark - Twitter Requests

- (void)loadFriends {
    
    [self twitterRequestWithPath:[NSString stringWithFormat:@"http://api.twitter.com/1/friends/ids.json?cursor=%i&screen_name=%@", -1, [self twitterUsername]] completion:^(id data, NSError *error) {
        [STEvents postEvent:EventTypeTwitterFriendsFinished object:data];
        
    }];
    
}

- (void)getFriendIds:(TwitterRequestHandler)handler {
    
    
}

- (void)getTwitterUser:(TwitterRequestHandler)handler {
    
    [self twitterRequestWithPath:[NSString stringWithFormat:@"https://api.twitter.com/1/users/show.json?screen_name=%@&include_entities=false", [self twitterUsername]] completion:handler];
    
}

- (void)getUsersForIds:(NSArray*)ids completion:(TwitterRequestHandler)handler {
    
    if ([ids count] > 0) {
        ids = [ids subarrayWithRange:NSMakeRange(0, 99)]; // max 100
    }
    
    NSString *path = [NSString stringWithFormat:@"https://api.twitter.com/1/users/lookup.json?user_id=%@&include_entities=false", [ids componentsJoinedByString:@","]];
    [self twitterRequestWithPath:path completion:handler];
    
}


#pragma mark - Getters

- (BOOL)isSessionValid {
    
    return (_twitterUserAuth!=nil);
    
}

- (NSDictionary*)userInfo {
    return _twitterUserAuth;
}

- (NSString*)twitterToken {
    
    if (_twitterUserAuth) {
        return [_twitterUserAuth objectForKey:@"oauth_token"];
    }
    
    return nil;
}

- (NSString*)twitterTokenSecret {
    
    if (_twitterUserAuth) {
        return [_twitterUserAuth objectForKey:@"oauth_token_secret"];
    }
    
    return nil;
}

- (NSString*)twitterID {
    
    if (_twitterUserAuth) {
        return [_twitterUserAuth objectForKey:@"user_id"];
    }
    
    return nil;
}

- (NSString*)twitterUsername {
    
    if (_twitterUserAuth) {
        return [_twitterUserAuth objectForKey:@"screen_name"];
    }
    
    return nil;
}



/*
 * iOS 5 Twitter Framework 
 */

#pragma mark - Access

- (void)requestAccess:(STTwitterAccessHandler)handler {
    
    if (!self.accountStore) {
        self.accountStore = [[ACAccountStore alloc] init];
    }
    
    ACAccountType *accountType = [_accountStore accountTypeWithAccountTypeIdentifier:ACAccountTypeIdentifierTwitter];
    [_accountStore requestAccessToAccountsWithType:accountType withCompletionHandler:^(BOOL granted, NSError *error) {
        
        _access = granted;
        if (granted) {
            
        } else {
            
            _access = NO;
            dispatch_async(dispatch_get_main_queue(), ^{
                UIAlertView *alert = [[UIAlertView alloc] initWithTitle:@"Twitter Account" message:@"Access to your Twitter account must be enabled, you can enable it in settings." delegate:(id<UIAlertViewDelegate>)self cancelButtonTitle:@"OK" otherButtonTitles:@"Settings", nil];
                [alert show];
                [alert release];
            });
            
        }
        
        dispatch_async(dispatch_get_main_queue(), ^{
            handler(_access);
        });
        
    }];
    
}


#pragma mark - Requests

- (void)reverseAuthWithAccount:(ACAccount*)account {
    
    __block EGOHTTPRequest *_request = [[EGOHTTPRequest alloc] initWithURL:[NSURL URLWithString:@"https://api.twitter.com/oauth/request_token"] completion:^(id request, NSError *error) {
        
        if (error == nil && [request responseStatusCode] == 200) {
            
            NSDictionary *params = [[NSMutableDictionary alloc] init];
            [params setValue:kTwitterConsumerKey forKey:@"x_reverse_auth_target"];
            [params setValue:[request responseString] forKey:@"x_reverse_auth_parameters"];
            
            NSURL *url = [NSURL URLWithString:@"https://api.twitter.com/oauth/access_token"];
            TWRequest *twRequest = [[TWRequest alloc] initWithURL:url parameters:params requestMethod:TWRequestMethodPOST];
            [twRequest setAccount:account];
            [twRequest performRequestWithHandler:^(NSData *responseData, NSHTTPURLResponse *urlResponse, NSError *error) {
                
                NSString *responseStr = [[NSString alloc] initWithData:responseData encoding:NSUTF8StringEncoding];
                NSDictionary *params = [self paramsForString:responseStr];
                _twitterUserAuth = [params retain];
                [STEvents postEvent:EventTypeTwitterAuthFinished object:_twitterUserAuth];
                [responseStr release];

                NSLog(@"login info %@", _twitterUserAuth);
                
            }];
            
            [params release];
            [twRequest release];

        } else {
            
            NSLog(@"revers oauth failed");
            [STEvents postEvent:EventTypeTwitterAuthFailed object:_twitterUserAuth];
            
        }
        
    }];
    
    [_request setRequestMethod:@"POST"];
    NSArray *array = [[NSArray alloc] initWithObjects:[NSDictionary dictionaryWithObject:@"reverse_auth" forKey:@"x_auth_mode"], nil];
    [self signRequest:_request params:array token:[NSString stringWithFormat:@"%@&", kTwitterSecret]];
    [array release];
    
    NSString *authBody = [@"x_auth_mode=reverse_auth" stringByAddingPercentEscapesUsingEncoding:NSUTF8StringEncoding];
    [_request setRequestBody:[authBody dataUsingEncoding:NSUTF8StringEncoding]]; 

    [_request startAsynchronous];
    [_request release];
    
}

- (void)requestToken {
    
   
    
}


#pragma mark - Accounts DataSource

- (NSInteger)numberOfAccounts {
    
    ACAccountType *accountType = [_accountStore accountTypeWithAccountTypeIdentifier:ACAccountTypeIdentifierTwitter];
    NSArray *accounts = [_accountStore accountsWithAccountType:accountType];
    return [accounts count];
    
}

- (ACAccount*)accountAtIndex:(NSInteger)index {
    
    ACAccountType *accountType = [_accountStore accountTypeWithAccountTypeIdentifier:ACAccountTypeIdentifierTwitter];
    NSArray *accounts = [_accountStore accountsWithAccountType:accountType];
    return [accounts objectAtIndex:index];

}

- (NSArray*)accounts {
    
    ACAccountType *accountType = [_accountStore accountTypeWithAccountTypeIdentifier:ACAccountTypeIdentifierTwitter];
    NSArray *accounts = [_accountStore accountsWithAccountType:accountType];
    return accounts;

}


#pragma mark - UIAlertViewDelegate

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (buttonIndex == alertView.cancelButtonIndex) return;
    
    // open settings.app
    [[UIApplication sharedApplication] openURL:[NSURL URLWithString:@"prefs://"]];
    
}

@end
