//
//  STSpotify.m
//  Stamped
//
//  Created by Landon Judkins on 6/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSpotify.h"
#include <stdint.h>
#include <stdlib.h>
#import "CocoaLibSpotify.h"
#import "STMenuController.h"
#import "Util.h"
#import "KeyChainItemWrapper.h"

// Test account
// 1235969194

NSString* const STSpotifyTrackEndedNotification = @"STSpotifyTrackEndedNotification";

static const uint8_t g_appkey[] = {
	0x01, 0xD2, 0x04, 0x53, 0x59, 0x3A, 0x72, 0x17, 0xB8, 0x32, 0xA1, 0x90, 0xA3, 0xD1, 0x21, 0x54,
	0x89, 0x1D, 0xD8, 0x7E, 0x1B, 0x12, 0x2E, 0x0A, 0xB0, 0xFE, 0xB6, 0xEB, 0x0B, 0x99, 0x6E, 0x61,
	0x03, 0x66, 0x09, 0x96, 0x85, 0x39, 0x8D, 0xEA, 0x60, 0x48, 0x56, 0x50, 0x99, 0xB8, 0x44, 0x4C,
	0xC1, 0x62, 0x3A, 0x75, 0xDD, 0x45, 0x15, 0x99, 0x04, 0x4B, 0xEE, 0xB4, 0x2A, 0x2E, 0xD1, 0x17,
	0x1F, 0x3F, 0x49, 0xC9, 0xA8, 0xA9, 0xC0, 0x0D, 0xCB, 0xB9, 0xC3, 0xDA, 0x52, 0x38, 0xD9, 0x91,
	0x72, 0x2B, 0x44, 0x78, 0xD5, 0x70, 0x23, 0xFA, 0x69, 0x4A, 0x02, 0x6D, 0xD0, 0x89, 0x56, 0xC0,
	0xFD, 0x9A, 0x0E, 0x37, 0xE3, 0x9D, 0x43, 0xEC, 0xF5, 0x75, 0xEC, 0x44, 0x4E, 0x5F, 0x05, 0x15,
	0x0A, 0xDE, 0x73, 0x21, 0xD5, 0x46, 0x13, 0x27, 0x10, 0xDE, 0x4E, 0x2B, 0xDE, 0xFD, 0x3F, 0xCD,
	0xA5, 0xB7, 0x58, 0x88, 0x4E, 0x32, 0x53, 0x84, 0x4D, 0x56, 0x17, 0x30, 0xCB, 0x3A, 0x0B, 0xA0,
	0x0D, 0x55, 0xBC, 0xA9, 0xFA, 0xC1, 0x89, 0x8F, 0x65, 0xE7, 0x42, 0xAE, 0x19, 0x2D, 0xE9, 0xCF,
	0x50, 0x31, 0xA6, 0x63, 0x3C, 0x1C, 0x57, 0xD2, 0xB0, 0xC7, 0x93, 0x9B, 0x40, 0x9C, 0xEF, 0xC6,
	0x31, 0x3D, 0xBE, 0x23, 0x7D, 0x59, 0xE9, 0x1C, 0x56, 0x70, 0x6C, 0xDA, 0xDD, 0x83, 0x13, 0xAA,
	0x78, 0x72, 0x48, 0x73, 0x61, 0x5B, 0x18, 0xC3, 0x35, 0x87, 0x88, 0xD4, 0x5A, 0xB8, 0x6C, 0x5A,
	0xE3, 0x8B, 0x30, 0x1E, 0xC2, 0xD7, 0x25, 0x01, 0x12, 0xBA, 0xE7, 0x2B, 0xFA, 0xC9, 0x38, 0xF6,
	0x8A, 0x32, 0x90, 0xAF, 0xE6, 0x05, 0x55, 0xBC, 0x83, 0xFB, 0x93, 0x95, 0xFA, 0x02, 0x83, 0x86,
	0x31, 0x48, 0x45, 0x80, 0xAA, 0x79, 0xFF, 0xCE, 0x28, 0x66, 0xCB, 0xE2, 0x78, 0x34, 0x22, 0x49,
	0xEF, 0xF7, 0xA0, 0xCC, 0x95, 0x51, 0xFD, 0xFE, 0xDA, 0xE6, 0xBB, 0x3D, 0x62, 0x50, 0xC4, 0xD6,
	0x87, 0x99, 0xA0, 0x70, 0x56, 0x98, 0xA6, 0x4B, 0x80, 0x12, 0x50, 0x4F, 0xBC, 0x98, 0x78, 0x5C,
	0x27, 0xAB, 0x38, 0x10, 0x73, 0x39, 0xDA, 0x10, 0x21, 0xF7, 0x8E, 0x90, 0x2A, 0xA5, 0xE3, 0xC6,
	0xEB, 0xFF, 0xCD, 0xDF, 0x3C, 0x92, 0x8F, 0x30, 0xD5, 0x2B, 0x5D, 0x82, 0xD6, 0xB3, 0x03, 0x4A,
	0x24,
};

static const size_t g_appkey_size = sizeof(g_appkey);

static NSString* const _spotifyKeychainItemID = @"SpotifyCredentials";

@interface STSpotify () <SPSessionDelegate, SPLoginViewControllerDelegate, SPPlaylistDelegate>

@property (nonatomic, readwrite, assign) BOOL startedSession;
@property (nonatomic, readonly, retain) KeychainItemWrapper* keychainItem;
@property (nonatomic, readwrite, retain) STCancellation* cancellation;
@property (nonatomic, readwrite, copy) void (^block)(BOOL, NSError*, STCancellation*);
@property (nonatomic, readwrite, assign) BOOL loggedIn;

@end

@implementation STSpotify

@synthesize startedSession = _startedSession;
@synthesize keychainItem = _keychainItem;
@synthesize cancellation = _cancellation;
@synthesize block = _block;
@synthesize loggedIn = _loggedIn;

static id _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STSpotify alloc] init];
}

+ (STSpotify *)sharedInstance {
    return _sharedInstance;
}

- (id)init
{
    self = [super init];
    if (self) {
        _keychainItem = [[KeychainItemWrapper alloc] initWithIdentifier:_spotifyKeychainItemID];
    }
    return self;
}

- (void)dealloc
{
    [_keychainItem release];
    [_cancellation release];
    [_block release];
    [super dealloc];
}

- (BOOL)connected {
    NSString* account = [_keychainItem objectForKey:(id)kSecAttrAccount];
    return account && ![account isEqualToString:@""];
}

- (STCancellation*)loginWithCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block {
    if (self.loggedIn) {
        STCancellation* cancellation = [STCancellation cancellation];
        [Util executeOnMainThread:^{
            block(YES, nil, cancellation);
        }];
        return cancellation;
    }
    else if (self.cancellation) {
        STCancellation* cancellation = [STCancellation cancellation];
        [Util executeOnMainThread:^{
            block(NO, [NSError errorWithDomain:@"Stamped" code:0 userInfo:[NSDictionary dictionaryWithObject:@"Operation pending" forKey:NSLocalizedDescriptionKey]], cancellation);
        }];
        return cancellation;
    }
    else {
        self.cancellation = [STCancellation cancellation];
        self.block = block;
        [self startSession];
        if (self.connected) {
            NSString* userName = [_keychainItem objectForKey:(id)kSecAttrAccount];
            NSString* credential = [_keychainItem objectForKey:(id)kSecValueData];
            [[SPSession sharedSession] attemptLoginWithUserName:userName existingCredential:credential rememberCredentials:YES];
        }
        else {
            SPLoginViewController *controller = [SPLoginViewController loginControllerForSession:[SPSession sharedSession]];
            controller.loginDelegate = self;
            [[Util sharedMenuController] presentModalViewController:controller animated:YES];
        }
        return self.cancellation;
    }
}

- (STCancellation*)logoutWithCallback:(void (^)(BOOL success, NSError* error, STCancellation* cancellation))block {
    [self startSession];
    STCancellation* cancellation = [STCancellation cancellation];
    [[SPSession sharedSession] logout:^{
        [self.keychainItem resetKeychainItem];
        if (!cancellation.cancelled) {
            block(YES, nil, cancellation);
        }
    }];
    return cancellation;
}

- (void)startSession {    
    if (!self.startedSession) {
        [SPSession initializeSharedSessionWithApplicationKey:[NSData dataWithBytes:&g_appkey 
                                                                            length:g_appkey_size] 
                                                   userAgent:@"com.stamped.iOS" 
                                               loadingPolicy:SPAsyncLoadingManual
                                                       error:nil];
        [[SPSession sharedSession] setDelegate:self];
        self.startedSession = YES;
    }
}

#pragma mark SPSessionDelegate Methods

-(UIViewController *)viewControllerToPresentLoginViewForSession:(SPSession *)aSession {
	return nil;
}

-(void)session:(SPSession *)aSession didGenerateLoginCredentials:(NSString *)credential forUserName:(NSString *)userName {
    [self.keychainItem setObject:credential forKey:(id)kSecValueData];
    [self.keychainItem setObject:userName forKey:(id)kSecAttrAccount];
    if (self.block && self.cancellation) {
        if (!self.cancellation.cancelled) {
            self.block(YES, nil, self.cancellation);
        }
    }
    self.cancellation = nil;
    self.block = nil;
}

-(void)sessionDidLoginSuccessfully:(SPSession *)aSession {
	// Invoked by SPSession after a successful login.
    self.loggedIn = YES;
}

-(void)session:(SPSession *)aSession didFailToLoginWithError:(NSError *)error {
	// Invoked by SPSession after a failed login.
    if (self.block && self.cancellation) {
        if (!self.cancellation.cancelled) {
            self.block(NO, error, self.cancellation);
        }
    }
    self.cancellation = nil;
    self.block = nil;
}

-(void)sessionDidLogOut:(SPSession *)aSession {
    self.loggedIn = NO;
}

-(void)sessionDidEndPlayback:(id <SPSessionPlaybackProvider>)aSession {
    [[NSNotificationCenter defaultCenter] postNotificationName:STSpotifyTrackEndedNotification object:nil];
}

-(void)session:(SPSession *)aSession didEncounterNetworkError:(NSError *)error {}
-(void)session:(SPSession *)aSession didLogMessage:(NSString *)aMessage {}
-(void)sessionDidChangeMetadata:(SPSession *)aSession {}


-(void)session:(SPSession *)aSession recievedMessageForUser:(NSString *)aMessage {
	UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"Message from Spotify"
                                                     message:aMessage
                                                    delegate:nil
                                           cancelButtonTitle:@"OK"
                                           otherButtonTitles:nil] autorelease];
	[alert show];
}

#pragma mark LoginCallback


-(void)loginViewController:(SPLoginViewController *)controller didCompleteSuccessfully:(BOOL)didLogin {
    if (!didLogin) {
        if (self.block && self.cancellation) {
            if (!self.cancellation.cancelled) {
                self.block(NO, nil, self.cancellation);
            }
        }
        self.cancellation = nil;
        self.block = nil;
    }
}

static SPPlaylist* _playlist;

- (void)addToPlaylist {
    if (!_playlist) {
    [self loginWithCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
        [SPAsyncLoading waitUntilLoaded:[SPSession sharedSession] timeout:3 then:^(NSArray *loadedItems, NSArray *notLoadedItems) {
            [SPAsyncLoading waitUntilLoaded:[SPSession sharedSession].userPlaylists timeout:3 then:^(NSArray *loadedItems, NSArray *notLoadedItems) {
                [[SPSession sharedSession].userPlaylists createPlaylistWithName:@"Testing" callback:^(SPPlaylist *createdPlaylist) {
                    NSLog(@"created:%@", createdPlaylist); 
                }]; 
            }];
        }];
//        NSURL* url = [NSURL URLWithString:[NSString stringWithFormat:@"%@:playlist:3Yce2kjbMgTB8b0HOm8soi",[SPSession sharedSession].user.spotifyURL]];
//        NSLog(@"url:%@", url);
//        [SPPlaylist playlistWithPlaylistURL:[NSURL URLWithString:@"spotify:user:1239306334:playlist:4c6K1LxEm8p2VMhEmQHWhR"]
//                                  inSession:[SPSession sharedSession]
//                                   callback:^(SPPlaylist *playlist) {
//                                       if (playlist && !_playlist) {
//                                           _playlist = [playlist retain];
//                                           _playlist.delegate = self;
//                                       }
//                                   }];
        
    }];
    }
    if (_playlist) {
        NSLog(@"playlist:%@:%d", _playlist, _playlist.isLoaded);
        
        _playlist.name = @"Stamped";
    }
}

-(void)itemsInPlaylistDidUpdateMetadata:(SPPlaylist *)playlist {
    NSLog(@"playlist2:%@:%d", playlist, playlist.isLoaded);
}
@end
