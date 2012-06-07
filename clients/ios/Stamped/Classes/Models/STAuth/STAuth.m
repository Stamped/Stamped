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
#import "ASIHTTPRequest.h"
#import "ASIS3ObjectRequest.h"
#import <RestKit/NSData+MD5.h>

// Amazon S3 Shit. -bons
static NSString* const kS3SecretAccessKey = @"4hqp3tVDt9ALgEFhDTqC4Y1P661uFNjtYqPVu2MW";
static NSString* const kS3AccessKeyID = @"AKIAIRLTXI62SD3BWAHQ";
static NSString* const kS3Bucket = @"stamped.com.static.temp";

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

- (void)facebookSignupWithParams:(NSDictionary*)params {
    
    NSString *path = @"/account/create/facebook.json";
    [[STRestKitLoader sharedInstance] loadWithPath:path post:NO authenticated:NO params:params mapping:[STSimpleLoginResponse mapping] andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
        
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


#pragma mark - Auth

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


#pragma mark - Updates

- (void)checkUserName:(NSString*)username completion:(STAuthRequestFinished)completion {
    
    NSString *path = @"/account/check.json";
    [[STRestKitLoader sharedInstance] loadWithPath:path post:NO authenticated:NO params:[NSDictionary dictionaryWithObject:username forKey:@"login"] mapping:[STSimpleLoginResponse mapping] andCallback:^(NSArray *results, NSError *error, STCancellation *cancellation) {
        
        completion(error);
        
    }];
    
}


/*
 GET /v0/account/check.json 
 Takes one field (login) and returns a 200 plus user object if it exists, otherwise returns a 404 if available and a 400 if invalid (e.g. if it's a blacklisted screen name).
 
 POST /v0/account/customize_stamp.json
 Takes two fields (color_primary and color_secondary) that are the hex values of the two colors. Returns the full user object.
 
 POST /v0/account/update_profile_image.json
 Takes one field (temp_image_url) that has the url of the image. Returns the full user object.
 */


#pragma mark - S3 Upload

- (void)s3UploadImageAtPath:(NSString*)path {
    if (!path) return;
    
    NSData *imageData = [NSData dataWithContentsOfFile:path];
    NSDate *now = [NSDate date];
    NSString *key = [NSString stringWithFormat:@"%@-%.0f.jpg", [imageData MD5], now.timeIntervalSince1970];
    ASIS3ObjectRequest *request = [ASIS3ObjectRequest PUTRequestForData:imageData withBucket:kS3Bucket key:key];
    request.secretAccessKey = kS3SecretAccessKey;
    request.delegate = self;
    request.uploadProgressDelegate = self;
    request.accessKey = kS3AccessKeyID;
    request.accessPolicy = ASIS3AccessPolicyPublicRead;
    request.timeOutSeconds = 30;
    request.numberOfTimesToRetryOnTimeout = 2;
    request.mimeType = @"image/jpeg";
    request.shouldAttemptPersistentConnection = NO;
    [ASIS3Request setShouldUpdateNetworkActivityIndicator:NO];
    [request startAsynchronous];
    //self.photoUploadRequest = request;
    //self.tempPhotoURL = [NSString stringWithFormat:@"http://s3.amazonaws.com/stamped.com.static.temp/%@", key];

}


#pragma mark - ASIRequestDelegate methods

- (void)requestFinished:(ASIHTTPRequest*)request {

}

- (void)requestFailed:(ASIHTTPRequest*)request {

}


@end
