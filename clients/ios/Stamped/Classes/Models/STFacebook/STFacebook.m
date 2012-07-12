//
//  STFacebook.m
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import "STFacebook.h"
#import "FBConnect.h"
#import "STEvents.h"
#import "STRestKitLoader.h"
#import "STSimpleBooleanResponse.h"
#import "STSettingsViewController.h"
#import "Util.h"

static id __instance;

@interface STFacebook () <UIAlertViewDelegate>

@end

@implementation STFacebook

@synthesize facebook;
@synthesize permissions;
@synthesize reloading;
@synthesize handler;
@synthesize userData;

+ (STFacebook*)sharedInstance {
    
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        __instance = [[[self class] alloc] init];
    });
    
    return __instance;
    
}

- (id)init {
    if ((self = [super init])) {
        
        facebook = [[Facebook alloc] initWithAppId:kFacebookAppID andDelegate:(id<FBSessionDelegate>)self];
        NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
        [STEvents addObserver:self selector:@selector(facebookBack:) event:EventTypeFacebookCameBack];
        
        if ([defaults objectForKey:@"FBAccessTokenKey"] && [defaults objectForKey:@"FBExpirationDateKey"]) {
            facebook.accessToken = [defaults objectForKey:@"FBAccessTokenKey"];
            facebook.expirationDate = [defaults objectForKey:@"FBExpirationDateKey"];
        }
        
    }
    return self;    
}

- (void)auth {
    
    if (![self.facebook isSessionValid]) {
        
        if ([self.facebook shouldExtendAccessToken]) {
            [self.facebook extendAccessToken];
        }
        else {

            [self.facebook authorize:[NSArray arrayWithObjects:@"user_about_me", @"user_location", @"email", @"publish_stream", @"publish_actions", nil]];
        }
        
    } else {
        if ([STRestKitLoader sharedInstance].loggedIn) {
            [self updateLinkedAccount];
        }
        else {
            [STEvents postEvent:EventTypeFacebookAuthFinished];   
        }
    }
    
}

- (void)invalidate {
    [self.facebook logout];
}

- (void)facebookBack:(NSNotification*)notification {
    
    if (![self.facebook isSessionValid]) {
        [STEvents postEvent:EventTypeFacebookAuthFailed];
    }
    
}

#pragma mark - FBSessionDelegate

- (void)updateLinkedAccount {
    if (self.facebook.accessToken) {
        NSMutableDictionary* params = [NSMutableDictionary dictionary];
        [params setObject:self.facebook.accessToken forKey:@"token"];
        [[STRestKitLoader sharedInstance] loadOneWithPath:@"/account/linked/facebook/add.json"
                                                     post:YES
                                            authenticated:YES
                                                   params:params
                                                  mapping:[STSimpleBooleanResponse mapping]
                                              andCallback:^(id result, NSError *error, STCancellation *cancellation) {
                                                  [STEvents postEvent:EventTypeFacebookAuthFinished];
                                              }];
    }
}

- (void)fbDidLogin {
    
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    [defaults setObject:[facebook accessToken] forKey:@"FBAccessTokenKey"];
    [defaults setObject:[facebook expirationDate] forKey:@"FBExpirationDateKey"];
    [defaults synchronize];
    
    if ([STRestKitLoader sharedInstance].loggedIn) {
        [self updateLinkedAccount];
    }
    else {
        [STEvents postEvent:EventTypeFacebookAuthFinished];
    }
}

- (void)fbDidNotLogin:(BOOL)cancelled {
    [STEvents postEvent:EventTypeFacebookAuthFailed];
}

- (void)fbDidExtendToken:(NSString*)accessToken  expiresAt:(NSDate*)expiresAt {
    
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    [defaults setObject:accessToken forKey:@"FBAccessTokenKey"];
    [defaults setObject:expiresAt forKey:@"FBExpirationDateKey"];
    [defaults synchronize];
    
    if ([STRestKitLoader sharedInstance].loggedIn) {
        [self updateLinkedAccount];
    }
    else {
        [STEvents postEvent:EventTypeFacebookAuthFinished];
    }
    
}

- (void)fbDidLogout {
    
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    [defaults removeObjectForKey:@"FBAccessTokenKey"];
    [defaults removeObjectForKey:@"FBExpirationDateKey"];
    [defaults synchronize];
    
    [STEvents postEvent:EventTypeFacebookLoggedOut];
}

- (void)fbSessionInvalidated {
    
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    [defaults removeObjectForKey:@"FBAccessTokenKey"];
    [defaults removeObjectForKey:@"FBExpirationDateKey"];
    [defaults synchronize];
    
}


#pragma mark - FBRequestDelegate

- (void)request:(FBRequest *)request didLoad:(id)result {
    
    if ([[request url] hasSuffix:@"friends"]) {
        
        // [Events postEvent:EventTypeFacebookFriendsFinished object:result];
        
    } else if ([[request url] hasSuffix:@"me"]) {
        if ([result objectForKey:@"id"]) {
            [[NSUserDefaults standardUserDefaults] setObject:[result objectForKey:@"id"] forKey:kFacebookUserIdentifier];
            [[NSUserDefaults standardUserDefaults] synchronize];
        }
        
        self.userData = result;
        
        if (self.handler) {
            self.handler(result);
        }
        self.handler = nil;
        //[Events postEvent:EventTypeFacebookUserFinished object:result];
        
    } 
    
}

- (void)request:(FBRequest *)request didFailWithError:(NSError *)error {
    
    //NSLog(@"facebook error : %@", [error localizedDescription]);
    
}


#pragma mark - Getters

- (BOOL)isSessionValid {
    return [self.facebook isSessionValid];
}

- (NSString*)userIdentifier {
    
    if ([[NSUserDefaults standardUserDefaults] objectForKey:kFacebookUserIdentifier]) {
        return [[NSUserDefaults standardUserDefaults] objectForKey:kFacebookUserIdentifier];
    }
    
    return nil;
    
}


#pragma mark - Requests

- (void)loadFriends {
    
    [facebook requestWithGraphPath:@"me/friends" andDelegate:self];
    
}

- (void)loadMe {
    
    [facebook requestWithGraphPath:@"me" andDelegate:self];
    
}


- (void)showFacebookAlert {
    UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Stamped added to your Facebook Timeline."
                                                     message:@"You can now share Stamped activity to your Facebook Timeline. Tap \"Settings\" to change sharing preferences."
                                                    delegate:self
                                           cancelButtonTitle:nil
                                           otherButtonTitles:@"Settings" , @"Dismiss", nil] autorelease];
    [alert show];
}

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex {
    if (buttonIndex == 0) {
        STSettingsViewController* controller = [[[STSettingsViewController alloc] init] autorelease];
        [Util pushController:controller modal:NO animated:YES];
    }
}



@end
