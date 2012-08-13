//
//  STRestKitLoader.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STCancellation.h"
#import "STLoginResponse.h"
#import "STAccountParameters.h"

typedef enum {
    //Auth queue
    STRestKitAuthPolicyStampedAuth,
    //Shared queue
    STRestKitAuthPolicyOptional,
    STRestKitAuthPolicyNone,
    STRestKitAuthPolicyFail,
    //Wait queue
    STRestKitAuthPolicyWait,
} STRestKitAuthPolicy;

typedef enum {
    STRestKitLoaderErrorRefreshing,
    STRestKitLoaderErrorLoggedOut,
    STRestKitLoaderErrorNotConnected,
    STRestKitLoaderErrorTimeout,
    STRestKitLoaderErrorFailedLogin,
} STRestKitLoaderError;

extern NSString* const STRestKitLoaderErrorDomain;
extern NSString* const STRestKitErrorIDKey;

@interface STRestKitLoader : NSObject

- (BOOL)isOffline;

- (STCancellation*)loadWithPath:(NSString*)path
                           post:(BOOL)post
                  authenticated:(BOOL)authenticated
                         params:(NSDictionary*)params 
                        mapping:(RKObjectMapping*)mapping 
                    andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block __attribute__ ((deprecated));

- (STCancellation*)loadOneWithPath:(NSString*)path
                              post:(BOOL)post 
                     authenticated:(BOOL)authenticated
                            params:(NSDictionary*)params 
                           mapping:(RKObjectMapping*)mapping 
                       andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block __attribute__ ((deprecated));

- (STCancellation*)loadWithPath:(NSString*)path
                           post:(BOOL)post
                     authPolicy:(STRestKitAuthPolicy)policy
                         params:(NSDictionary*)params 
                        mapping:(RKObjectMapping*)mapping 
                    andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loadOneWithPath:(NSString*)path
                              post:(BOOL)post 
                        authPolicy:(STRestKitAuthPolicy)policy
                            params:(NSDictionary*)params 
                           mapping:(RKObjectMapping*)mapping 
                       andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)authenticateWithCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

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

- (void)refreshToken;
- (void)logout;
- (void)updateCurrentUser:(id<STUserDetail>)currentUser;

@property (nonatomic, readonly, assign) BOOL loggedIn;
@property (nonatomic, readonly, retain) id<STUserDetail> currentUser;

+ (STRestKitLoader*)sharedInstance;

@end
