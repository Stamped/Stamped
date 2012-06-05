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

- (void)auth;
- (void)handleOpenURL:(NSURL*)url;
- (void)getTwitterUser:(TwitterRequestHandler)handler;
- (NSString*)twitterUsername;
- (NSString*)twitterToken;
- (NSString*)twitterTokenSecret;

@property(nonatomic,assign) BOOL access;
@property(nonatomic,retain) ACAccountStore *accountStore;
@property(nonatomic,retain) NSDictionary *twitterUser;

- (void)requestAccess:(STTwitterAccessHandler)handler;
- (ACAccount*)accountAtIndex:(NSInteger)index;
- (NSInteger)numberOfAccounts;

@end
