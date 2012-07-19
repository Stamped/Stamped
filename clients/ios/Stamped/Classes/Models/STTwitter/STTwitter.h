//
//  STTwitter.h
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import <Foundation/Foundation.h>
#import <Accounts/Accounts.h>
#import <Twitter/Twitter.h>
#import "STCancellation.h"


extern NSString* const STTwitterErrorDomain;

typedef void(^STTwitterAccessHandler)(BOOL granted);
typedef void(^TwitterRequestHandler)(id, NSError*);

@interface STTwitter : NSObject {
    NSArray *_accounts;
    NSDictionary *_twitterUserAuth;
}

+ (STTwitter*)sharedInstance;

@property(nonatomic,assign) BOOL access;
@property(nonatomic,retain) ACAccountStore *accountStore;
@property(nonatomic,retain) NSDictionary *twitterUser;

/*
 * Twitter OAuth Methods
 */
- (void)auth;
- (void)handleOpenURL:(NSURL*)url;

/*
 * iOS 5 Methods
 */
- (void)reverseAuthWithAccount:(ACAccount*)account;
- (void)requestAccess:(STTwitterAccessHandler)handler;
- (ACAccount*)accountAtIndex:(NSInteger)index;
- (NSInteger)numberOfAccounts;
- (NSArray*)accounts;

/*
 * Valid for both after auth
 */
- (ACAccount*)currentAccount;
- (NSString*)twitterUsername;
- (NSString*)twitterToken;
- (NSString*)twitterTokenSecret;
- (BOOL)isSessionValid;
- (BOOL)canTweet;
- (void)getTwitterUser:(TwitterRequestHandler)handler;

- (STCancellation*)sendTweet:(NSString*)tweet withCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)sendTweets:(NSArray*)tweets withCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)addTwitterWithCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

- (STCancellation*)fullTwitterAuthWithAddAccount:(BOOL)shouldAddAccount 
                                     andCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block;

@end
