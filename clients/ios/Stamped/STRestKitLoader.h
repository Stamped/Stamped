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

@interface STRestKitLoader : NSObject

- (STCancellation*)loadWithPath:(NSString*)path
                           post:(BOOL)post
                  authenticated:(BOOL)authenticated
                         params:(NSDictionary*)params 
                        mapping:(RKObjectMapping*)mapping 
                    andCallback:(void(^)(NSArray* results, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loadOneWithPath:(NSString*)path
                              post:(BOOL)post 
                     authenticated:(BOOL)authenticated
                            params:(NSDictionary*)params 
                           mapping:(RKObjectMapping*)mapping 
                       andCallback:(void(^)(id result, NSError* error, STCancellation* cancellation))block;

- (void)authenticate;

- (STCancellation*)loginWithScreenName:(NSString*)screenName 
                              password:(NSString*)password 
                           andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loginWithFacebookUserToken:(NSString*)userToken
                                  andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)loginWithTwitterUserToken:(NSString*)userToken 
                                  userSecret:(NSString*)userSecret
                                 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)createAccountWithPassword:(NSString*)password
                                  screenName:(NSString*)screenName
                                        name:(NSString*)name
                                       email:(NSString*)email
                                       phone:(NSString*)phone //optional
                                profileImage:(NSString*)profileImage //optional
                                 andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)createAccountWithFacebookUserToken:(NSString*)userToken 
                                           screenName:(NSString*)screenName
                                                 name:(NSString*)name
                                                email:(NSString*)email //optional
                                                phone:(NSString*)phone //optional
                                         profileImage:(NSString*)profileImage //optional
                                          andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)createAccountWithTwitterUserToken:(NSString*)userToken 
                                          userSecret:(NSString*)userSecret
                                          screenName:(NSString*)screenName
                                                name:(NSString*)name
                                               email:(NSString*)email //optional
                                               phone:(NSString*)phone //optional
                                        profileImage:(NSString*)profileImage //optional
                                         andCallback:(void (^)(id<STLoginResponse> response, NSError* error, STCancellation* cancellation))block;

- (void)refreshToken;
- (void)logout;

@property (nonatomic, readwrite, retain) id<STUserDetail> currentUser;

+ (STRestKitLoader*)sharedInstance;

@end
