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
- (NSString*)twitterUsername;
- (NSString*)twitterToken;
- (NSString*)twitterTokenSecret;
- (BOOL)isSessionValid;
- (void)getTwitterUser:(TwitterRequestHandler)handler;

@end
