//
//  STPlayer.m
//  Stamped
//
//  Created by Landon Judkins on 6/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STPlayer.h"
#import "STRdio.h"
#import "Util.h"
#import "STConfiguration.h"
#import <AVFoundation/AVFoundation.h>
#import "STActionUtil.h"
#import "STSpotify.h"
#import "CocoaLibSpotify.h"

NSString* const STPlayerItemChangedNotification = @"STPlayerItemChangedNotification";
NSString* const STPlayerStateChangedNotification = @"STPlayerStateChangedNotification";
NSString* const STPlayerPlaylistChangedNotification = @"STPlayerPlaylistChangedNotification";

NSString* const STPlayerCummulativeKey = @"Player.cummulative";
NSString* const STPlayerRevertKey = @"Player.revert";
NSString* const STPlayerFullFooterKey = @"Player.fullFooter";

@interface STPlayer () <RDPlayerDelegate>

@property (nonatomic, readonly, retain) NSMutableArray<STPlaylistItem>* items;

@property (nonatomic, readwrite, assign) CGFloat currentItemLength;
@property (nonatomic, readwrite, assign) NSInteger currentItemIndex;

@property (nonatomic, readonly, retain) Rdio* rdio;
@property (nonatomic, readonly, retain) AVPlayer* previewPlayer;
@property (nonatomic, readwrite, retain) SPPlaybackManager* spotifyPlaybackManager;


@end

@implementation STPlayer

@synthesize paused = _paused;
@synthesize currentItemLength = _currentItemLength;
@synthesize currentItemIndex = _currentItemIndex;
@synthesize previewPlayer = _previewPlayer;

@synthesize items = _items;
@synthesize rdio = _rdio;
@synthesize spotifyPlaybackManager = _spotifyPlaybackManager;

static id _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STPlayer alloc] init];
}

+ (STPlayer*)sharedInstance {
    return _sharedInstance;
}

- (id)init {
    self = [super init];
    if (self) {
        _items = (id)[[NSMutableArray alloc] init];
        _paused = YES;
        _previewPlayer = [[AVPlayer alloc] init];
        [[NSNotificationCenter defaultCenter] addObserver:self 
                                                 selector:@selector(previewEnded:) 
                                                     name:AVPlayerItemDidPlayToEndTimeNotification
                                                   object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self 
                                                 selector:@selector(spotifyTrackEnded:) 
                                                     name:STSpotifyTrackEndedNotification
                                                   object:nil];
    }
    return self;
}

- (Rdio *)rdio {
    if (!_rdio) {
        _rdio = [[STRdio sharedRdio].rdio retain];
        _rdio.player.delegate = self;
    }
    return _rdio;
}

- (void)dealloc
{
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [_rdio release];
    [_items release];
    [_previewPlayer release];
    [_spotifyPlaybackManager release];
    [super dealloc];
}

- (STPlayerService)currentTrackService {
    if (self.items.count == 0) return STPlayerServiceNone;
    id<STPlaylistItem> item = [self.items objectAtIndex:self.currentItemIndex];
    return [self serviceForItem:item];
}

- (void)initializeSpotify {
    if (!self.spotifyPlaybackManager) {
        self.spotifyPlaybackManager = [[[SPPlaybackManager alloc] initWithPlaybackSession:[SPSession sharedSession]] autorelease];
    }
}

- (void)playKatyPerry {
    [self playSpotifyTrack:@"spotify:track:6OBK6xjgbwXapL375a02zf"];
}

- (void)playSpotifyTrack:(NSString*)key {
    void (^block)() = ^{
        [self initializeSpotify];
        
        NSURL *trackURL = [NSURL URLWithString:key];
        [[SPSession sharedSession] trackForURL:trackURL callback:^(SPTrack *track) {
            
            if (track != nil) {
                
                [SPAsyncLoading waitUntilLoaded:track timeout:kSPAsyncLoadingDefaultTimeout then:^(NSArray *tracks, NSArray *notLoadedTracks) {
                    [self.spotifyPlaybackManager playTrack:track callback:^(NSError *error) {
                        if (error) {
                            UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"Cannot Play Track"
                                                                            message:[error localizedDescription]
                                                                           delegate:nil
                                                                  cancelButtonTitle:@"OK"
                                                                  otherButtonTitles:nil] autorelease];
                            [alert show];
                        } else {
                            NSLog(@"playing with Spotify:%@", key);
                            // self.currentTrack = track;
                        }
                        
                    }];
                }];
            }
        }]; 
    };
    if ([STSpotify sharedInstance].loggedIn) {
        block();
    }
    else {
        [[STSpotify sharedInstance] loginWithCallback:^(BOOL success, NSError *error, STCancellation *cancellation) {
            if (success) {
                block();
            }
        }];
    }
}

- (void)seekToItemAtIndex:(NSInteger)index {
    [self _stopItem];
    [self _playItemAtIndex:index];
    self.currentItemIndex = index;
    self.paused = NO;
    [self fireStateChanged];
    [self fireItemChanged];
}

- (BOOL)addPlaylistItem:(id<STPlaylistItem>)item atIndex:(NSInteger)index {
    if ([self serviceForItem:item] != STPlayerServiceNone) {
        [self.items insertObject:item atIndex:index];
        if (index <= self.currentItemIndex && self.items.count > 1) {
            self.currentItemIndex = self.currentItemIndex + 1;
        }
        [self firePlaylistChanged];
        return YES;
    }
    return NO;
}

- (id<STPlaylistItem>)itemAtIndex:(NSInteger)index {
    return [[[self.items objectAtIndex:index] retain] autorelease];
}

- (void)removeItemAtIndex:(NSInteger)index {
    BOOL paused = self.paused;
    BOOL itemChanged = NO;
    id<STPlaylistItem> item = [self.items objectAtIndex:index];
    if (index == self.currentItemIndex) {
        if (!self.paused) {
            if ([self serviceForItem:item] == STPlayerServiceRdio) {
                [self.rdio.player stop];
            }
            if (index >= self.itemCount) {
                _paused = YES;
            }
        }
        if (index == self.itemCount - 1) {
            self.currentItemIndex = 0;
        }
        itemChanged = YES;
    }
    else if (index < self.currentItemIndex) {
        self.currentItemIndex = self.currentItemIndex - 1;
    }
    [self.items removeObjectAtIndex:index];
    if (paused != self.paused) {
        [self fireStateChanged];
    }
    [self firePlaylistChanged];
    if (itemChanged) {
        [self fireItemChanged];
    }
}

- (STPlayerService)serviceForItem:(id<STPlaylistItem>)item {
    BOOL spotifyConnect = [STSpotify sharedInstance].connected;
    BOOL rdioConnected = [STRdio sharedRdio].connected;
    NSString* spotifyID = [STActionUtil sourceIDForItem:item withSource:@"spotify"];
    NSString* rdioID = [STActionUtil sourceIDForItem:item withSource:@"rdio"];
    NSString* preview = [STActionUtil previewURLForItem:item];
    if ((spotifyID && spotifyConnect)) {
        return STPlayerServiceSpotify;
    }
    else if ((rdioID && rdioConnected)) {
        return STPlayerServiceRdio;
    }
    else if (preview) {
        return STPlayerServicePreview;
    }
    else {
        return STPlayerServiceNone;
    }
}

- (void)_stopItem {
    //if (self.items.count) {
        //id<STPlaylistItem> item = [self.items objectAtIndex:self.currentItemIndex];
        [self.previewPlayer pause]; //helps with Rdio login
        [self.rdio.player stop];
        [self.spotifyPlaybackManager setIsPlaying:NO];
        //  else if (STPlayerServicePreview == service) {
//            [self.previewPlayer pause];
//        }
    //}
}

- (void)_playItemAtIndex:(NSInteger)index {
    id<STPlaylistItem> item = [self.items objectAtIndex:index];
    STPlayerService service = [self serviceForItem:item];
    if (STPlayerServiceSpotify == service) {
        NSString* spotifyID = [STActionUtil sourceIDForItem:item withSource:@"spotify"];
        if (spotifyID) {
            [self playSpotifyTrack:spotifyID];
        }
    }
    else if (STPlayerServiceRdio == service) {
        NSString* rdioID = [STActionUtil sourceIDForItem:item withSource:@"rdio"];
        if (rdioID) {
            //NSLog(@"rdio play:%@", rdioID);
            [self.rdio.player playSource:rdioID];
        }
    }
    else if (STPlayerServicePreview == service) {
        NSURL* url = [NSURL URLWithString:[STActionUtil previewURLForItem:item]];
        [self.previewPlayer replaceCurrentItemWithPlayerItem:[AVPlayerItem playerItemWithURL:url]];
        [self.previewPlayer play];
    }
}

- (void)fireStateChanged {
    [[UIApplication sharedApplication] setIdleTimerDisabled:!self.paused];
    [[NSNotificationCenter defaultCenter] postNotificationName:STPlayerStateChangedNotification object:nil];
}

- (void)firePlaylistChanged {
    [[NSNotificationCenter defaultCenter] postNotificationName:STPlayerPlaylistChangedNotification object:nil];
}

- (void)fireItemChanged {
    [[NSNotificationCenter defaultCenter] postNotificationName:STPlayerItemChangedNotification object:nil];
}

- (NSInteger)itemCount {
    return self.items.count;
}

- (void)moveItemAtIndex:(NSInteger)index toIndex:(NSInteger)destination {
    if (index != destination) {
        id<STPlaylistItem> item = [self.items objectAtIndex:index];
        if (index == self.currentItemIndex) {
            self.currentItemIndex = destination;
        }
        else if (destination < index) {
            if (self.currentItemIndex < index && self.currentItemIndex >= destination) {
                self.currentItemIndex = self.currentItemIndex + 1;
            }
        }
        else if (index < destination) {
            if (self.currentItemIndex > index && self.currentItemIndex <= destination) {
                self.currentItemIndex = self.currentItemIndex - 1;
            }
        }
        [self.items removeObjectAtIndex:index];
        [self.items insertObject:item atIndex:destination];
        [self firePlaylistChanged];
    }
} 

- (void)setPaused:(BOOL)paused {
    if (paused != _paused) {
        _paused = paused;
        if (self.items.count) {
            id<STPlaylistItem> item = [self.items objectAtIndex:self.currentItemIndex];
            STPlayerService service = [self serviceForItem:item];
            if (STPlayerServiceSpotify == service) {
                [self.spotifyPlaybackManager setIsPlaying:!paused];
            }
            else if (STPlayerServiceRdio == service) {
                if (paused && self.rdio.player.state != RDPlayerStatePaused) {
                    [self.rdio.player togglePause];
                }
                if (!paused) {
                    if (self.rdio.player.trackKeys.count == 0) {
                        [self _playItemAtIndex:self.currentItemIndex];
                    }
                    else {
                        [self.rdio.player togglePause];
                    }
                }
            }
            else if (STPlayerServicePreview == service) {
                if (paused) {
                    [self.previewPlayer pause];
                }
                else {
                    [self.previewPlayer play];
                }
            }
        }
        [self fireStateChanged];
    }
}

-(BOOL)rdioIsPlayingElsewhere {
    return NO;
}

/**
 * Notification that the player has changed states. See <code>RDPlayerState</code>.
 */

- (void)seekToNext {
    NSInteger next = self.currentItemIndex + 1;
    if (next < self.itemCount) {
        [self seekToItemAtIndex:next];
    }
    else {
        self.paused = YES;
    }
}

-(void)rdioPlayerChangedFromState:(RDPlayerState)oldState toState:(RDPlayerState)newState {
    NSAssert1([NSThread isMainThread], @"not main thread %@", [NSThread currentThread]);
    if (!self.paused) {
        if (oldState == RDPlayerStatePlaying && newState == RDPlayerStateStopped) {
            [self seekToNext];
        }
    }
}

- (void)previewEnded:(NSNotification*)notifications {
    if (!self.paused) {
       // NSLog(@"itunes song");
        [self seekToNext];
    }
}

- (void)spotifyTrackEnded:(id)notImportant {
    if (!self.paused) {
        [self seekToNext];
    }
}

- (void)clear {
    _paused = YES;
    self.currentItemIndex = 0;
    [self.items removeAllObjects];
    [self.rdio.player stop];
    [self fireStateChanged];
    [self firePlaylistChanged];
    [self fireItemChanged];
}

+ (void)setupConfigurations {
    [STConfiguration addFlag:NO forKey:STPlayerCummulativeKey];
    [STConfiguration addFlag:NO forKey:STPlayerRevertKey];
    [STConfiguration addFlag:NO forKey:STPlayerFullFooterKey];
}

@end
