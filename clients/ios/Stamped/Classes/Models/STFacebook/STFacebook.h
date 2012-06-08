//
//  STFacebook.h
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import <Foundation/Foundation.h>
#import "Facebook.h"

typedef void(^FacebookMeRequestHandler)(NSDictionary *);

@interface STFacebook : NSObject <FBSessionDelegate, FBRequestDelegate>

@property (nonatomic, retain) Facebook *facebook;
@property (nonatomic, retain) NSArray *permissions;
@property (nonatomic, retain) NSDictionary *userData;
@property (nonatomic, readonly, getter = isReloading) BOOL reloading;
@property (nonatomic, copy) FacebookMeRequestHandler handler;

+ (id)sharedInstance;

- (void)auth;
- (BOOL)isSessionValid;
- (void)invalidate;

// requests
- (void)loadFriends;
- (void)loadMe;

@end
