//
//  STAuth.m
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import "STAuth.h"
#import "STSimpleLoginResponse.h"
#import "STRestKitLoader.h"
#import "STDebug.h"

static id __instance;

@implementation STAuth

+ (id)sharedInstance {
    
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        __instance = [[[self class] alloc] init];
    });
    
    return __instance;
    
}

/*
 v0/account/create/facebook.json
 v0/account/create/twitter.json
 v0/oauth2/login/facebook.json
 v0/oauth2/login/twitter.json
 
 The names of the Facebook 'token' arguments have also been been changed for consistency.  Below are the expected args for each endpoint. 
 
 create_with_facebook.json:
 
 'name', 		basestring, required
 'screenname', 		basestring, required
 'user_token', 		basestring, required
 'email', 		basestring
 'phone', 		int
 'profile_image', 	basestring
 
 create/twitter.json:
 
 'name',                 basestring, required=True
 'screen_name',          basestring, required=True
 'user_token',           basestring, required=True
 'user_secret',          basestring, required=True
 'email',                basestring
 'phone',                int
 'profile_image',        basestring
 
 login/facebook.json:
 
 'user_token',           basestring, required=True
 
 login/twitter.json:
 
 'user_token',           basestring, required=True
 'user_secret',          basestring, required=True
 */

- (void)facebookSignupWithParams:(NSDictionary*)params {
    
    NSString *path = @"/account/create/facebook.json";
    [[STRestKitLoader sharedInstance] loadWithPath:path post:NO params:params mapping:[STSimpleLoginResponse mapping] andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
        
        if (error) {
            
            [[STDebug sharedInstance] log:[error localizedDescription]];
            [Util warnWithMessage:[NSString stringWithFormat:@"%@\n\n%@\n\n%@\n", [error localizedDescription], path, params] andBlock:nil];

        } else {
            
            [STEvents postEvent:EventTypeSignupFinished];
            
        }
                
    }];
    
}

- (void)twitterSignupWithParams:(NSDictionary*)params {
    
    NSString *path = @"/account/create/twitter.json";
    [[STRestKitLoader sharedInstance] loadWithPath:path post:YES params:params mapping:[STSimpleLoginResponse mapping] andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
        
        if (error) {
            
            [[STDebug sharedInstance] log:[error localizedDescription]];
            [Util warnWithMessage:[NSString stringWithFormat:@"%@\n\n%@\n\n%@\n", [error localizedDescription], path, params] andBlock:nil];
            
        } else {
            
            [STEvents postEvent:EventTypeSignupFinished];

            
        }
                
    }];
    
}

- (void)facebookAuthWithToken:(NSString*)token {
    
    NSString *path = @"/oauth2/login/facebook.json";
    NSDictionary *params = [NSDictionary dictionaryWithObjectsAndKeys:token, @"user_token", nil];
    
    [[STRestKitLoader sharedInstance] loadWithPath:path post:NO params:params mapping:[STSimpleLoginResponse mapping] andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
        
        if (error) {
            NSLog(@"error %@", [error localizedDescription]);
        }
        
        
    }];
    
}

- (void)twitterAuthWithToken:(NSString*)token secretToken:(NSString*)secretToken {
    
    NSString *path = @"/oauth2/login/twitter.json";
    NSDictionary *params = [NSDictionary dictionaryWithObjectsAndKeys:token, @"user_token", secretToken, @"user_secret", nil];
    
    [[STRestKitLoader sharedInstance] loadWithPath:path post:NO params:params mapping:[STSimpleLoginResponse mapping] andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
        
        if (error) {
            NSLog(@"error %@", [error localizedDescription]);
        }
        
        NSLog(@"result %@", results);
        
    }];
    
}


@end
