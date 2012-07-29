//
//  STFacebook.h
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import <Foundation/Foundation.h>
#import "Facebook.h"

#define kFacebookUserIdentifier @"kFacebookUserIdentifier"

#define kFacebookAppID @"297022226980395"
#define kFacebookSecret @"17eb87d731f38bf68c7b40c45c35e52e"
#define kFacebookNameSpace @"stampedapp"

typedef void(^FacebookMeRequestHandler)(NSDictionary *);

@interface STFacebook : NSObject <FBSessionDelegate, FBRequestDelegate>

@property (nonatomic, retain) Facebook *facebook;
@property (nonatomic, retain) NSArray *permissions;
@property (nonatomic, retain) NSDictionary *userData;
@property (nonatomic, readonly, getter = isReloading) BOOL reloading;
@property (nonatomic, copy) FacebookMeRequestHandler handler;

+ (STFacebook*)sharedInstance;

- (void)auth;
- (void)reauth;
- (BOOL)connected;
- (BOOL)isSessionValid;
- (void)invalidate;

// requests
- (void)loadFriends;
- (void)loadMe;

- (void)showFacebookAlert;

@end
