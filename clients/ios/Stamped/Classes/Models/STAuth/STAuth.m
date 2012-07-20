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
#import "STStampedAPI.h"
#import "STSimpleUserDetail.h"
#import "STEvents.h"

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
 
 
 ADDITIONS
 
 cls.addProperty('bio',                              basestring)
 cls.addProperty('website',                          basestring)
 cls.addProperty('location',                         basestring)
 cls.addProperty('color_primary',                    basestring)
 cls.addProperty('color_secondary',                  basestring)
 
 */


/*
 
 - (STCancellation*)loginWithScreenName:(NSString*)screenName 
 password:(NSString*)password 
 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;
 
 - (STCancellation*)loginWithFacebookUserToken:(NSString*)userToken
 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;
 
 - (STCancellation*)loginWithTwitterUserToken:(NSString*)userToken 
 userSecret:(NSString*)userSecret
 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;
 
 - (STCancellation*)createAccountWithPassword:(NSString*)password
 accountParameters:(STAccountParameters*)accountParameters
 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;
 
 - (STCancellation*)createAccountWithFacebookUserToken:(NSString*)userToken 
 accountParameters:(STAccountParameters*)accountParameters
 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;
 
 - (STCancellation*)createAccountWithTwitterUserToken:(NSString*)userToken 
 userSecret:(NSString*)userSecret 
 accountParameters:(STAccountParameters*)accountParameters
 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;
 
 
 */


#pragma mark - Signup

- (void)signupWithPassword:(NSString*)password parameters:(STAccountParameters*)params {
    
    [[STStampedAPI sharedInstance] createAccountWithPassword:password accountParameters:params andCallback:^(id<STLoginResponse> response, NSError *error, STCancellation *cancellation) {
        if (error) {
            [STEvents postEvent:EventTypeSignupFailed identifier:nil object:error];
            [[STDebug sharedInstance] log:[error localizedDescription]];
            NSLog(@"email signup error %@", [error localizedDescription]);
        } else {
            [STEvents postEvent:EventTypeSignupFinished];
        }
    }];
    
}

- (void)facebookSignupWithToken:(NSString*)token params:(STAccountParameters*)params {
    
    [[STStampedAPI sharedInstance] createAccountWithFacebookUserToken:token accountParameters:params andCallback:^(id<STLoginResponse> response, NSError *error, STCancellation *cancellation) {
        
        if (error) {
            
            [STEvents postEvent:EventTypeSignupFailed identifier:nil object:error];
            [[STDebug sharedInstance] log:[error localizedDescription]];
            NSLog(@"facebook signup error %@", [error localizedDescription]);

        } else {
            
            [STEvents postEvent:EventTypeSignupFinished];
        }
                
    }];
    
}

- (void)twitterSignupWithToken:(NSString*)token secretToken:(NSString*)secretToken params:(STAccountParameters*)params {
        
    [[STStampedAPI sharedInstance] createAccountWithTwitterUserToken:token userSecret:secretToken accountParameters:params andCallback:^(id<STLoginResponse> response, NSError *error, STCancellation *cancellation) {
        
        if (error) {
            
            [STEvents postEvent:EventTypeSignupFailed];
            [[STDebug sharedInstance] log:[error localizedDescription]];
            NSLog(@"twitter signup error %@", [error localizedDescription]);

        } else {
            
            [STEvents postEvent:EventTypeSignupFinished];

        }
                
    }];
    
}


#pragma mark - Auth

- (void)facebookAuthWithToken:(NSString*)token completion:(STAuthRequestFinished)completion {
    
    [[STStampedAPI sharedInstance] loginWithFacebookUserToken:token andCallback:^(id<STLoginResponse> response, NSError *error, STCancellation *cancellation) {

        completion(error);
        
    }];
    
}

- (void)twitterAuthWithToken:(NSString*)token secretToken:(NSString*)secretToken completion:(STAuthRequestFinished)completion {
    
    [[STStampedAPI sharedInstance] loginWithTwitterUserToken:(NSString*)token userSecret:(NSString*)secretToken andCallback:^(id<STLoginResponse> response, NSError *error, STCancellation *cancellation) {
        
        completion(error);
        
    }];
    
}


#pragma mark - Updates

- (void)checkUserName:(NSString*)username completion:(STAuthRequestFinished)completion {
    
    /*
     GET /v0/account/check.json 
     Takes one field (login) and returns a 200 plus user object if it exists, otherwise returns a 404 if available and a 400 if invalid (e.g. if it's a blacklisted screen name).
     */
    
    NSString *path = @"/account/check.json";
    [[STRestKitLoader sharedInstance] loadWithPath:path post:NO authenticated:NO params:[NSDictionary dictionaryWithObject:username forKey:@"login"] mapping:[STSimpleLoginResponse mapping] andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
        
        completion(error);
        
    }];
    
}

- (void)updateStampWithPrimaryColor:(NSString*)primary secondary:(NSString*)secondary completion:(STAuthRequestFinished)completion {
    
    /*
     POST /v0/account/customize_stamp.json
     Takes two fields (color_primary and color_secondary) that are the hex values of the two colors. Returns the full user object.
     */
    NSString *path = @"/account/customize_stamp.json";
    NSDictionary *params = [NSDictionary dictionaryWithObjectsAndKeys:primary, @"color_primary", secondary, @"color_secondary", nil];
    [[STRestKitLoader sharedInstance] loadOneWithPath:path post:YES authenticated:YES params:params mapping:[STSimpleUserDetail mapping] andCallback:^(id result, NSError *error, STCancellation *cancellation) {
        
        completion(error);
        if (result) {
            id<STUserDetail> userDetail = result;
            if (userDetail) {
                [[STRestKitLoader sharedInstance] updateCurrentUser:userDetail];
            }
            
        }
    }];
    
}

- (void)updateProfileImageWithPath:(NSString*)tempPath completion:(STAuthRequestFinished)completion {
    
    /*
     POST /v0/account/update_profile_image.json
     Takes one field (temp_image_url) that has the url of the image. Returns the full user object.
     */
    
    NSString *path = @"/account/update.json";
    NSDictionary *params = [NSDictionary dictionaryWithObjectsAndKeys:tempPath, @"temp_image_url", nil];
    [[STRestKitLoader sharedInstance] loadWithPath:path post:YES authenticated:YES params:params mapping:[STSimpleLoginResponse mapping] andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
        
        completion(error);
        
    }];
    
}


@end
