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

typedef enum {
    STPlayerServiceNone,
    STPlayerServiceRdio,
} STPlayerService;

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

@end

@implementation STPlayer

@synthesize paused = _paused;
@synthesize currentItemLength = _currentItemLength;
@synthesize currentItemIndex = _currentItemIndex;

@synthesize items = _items;
@synthesize rdio = _rdio;

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
        _rdio = [[STRdio sharedRdio].rdio retain];
        _paused = YES;
        self.rdio.player.delegate = self;
    }
    return self;
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
                [_rdio.player stop];
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
    STPlayerService best = STPlayerServiceNone;
    if (item.action.sources.count) {
        for (id<STSource> source in item.action.sources) {
            if ([[source source] isEqualToString:@"rdio"]) {
                best = STPlayerServiceRdio;
            }
        }
    }
    return best;
}

- (void)_stopItem {
    if (self.items.count) {
        id<STPlaylistItem> item = [self.items objectAtIndex:self.currentItemIndex];
        if (STPlayerServiceRdio == [self serviceForItem:item]) {
            [self.rdio.player stop];
        }
    }
}

- (void)_playItemAtIndex:(NSInteger)index {
    id<STPlaylistItem> item = [self.items objectAtIndex:index];
    if (STPlayerServiceRdio == [self serviceForItem:item]) {
        NSString* rdioID = nil;
        for (id<STSource> source in item.action.sources) {
            if ([[source source] isEqualToString:@"rdio"]) {
                rdioID = [source sourceID];
            }
        }
        if (rdioID) {
            NSLog(@"rdio play:%@", rdioID);
            [self.rdio.player playSource:rdioID];
        }
    }
}

- (void)fireStateChanged {
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
            if (STPlayerServiceRdio == service) {
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
-(void)rdioPlayerChangedFromState:(RDPlayerState)oldState toState:(RDPlayerState)newState {
    NSAssert1([NSThread isMainThread], @"not main thread %@", [NSThread currentThread]);
    if (!self.paused) {
        if (oldState == RDPlayerStatePlaying && newState == RDPlayerStateStopped) {
            NSInteger next = self.currentItemIndex + 1;
            if (next < self.itemCount) {
                [self seekToItemAtIndex:next];
            }
            else {
                [self seekToItemAtIndex:0];
            }
        }
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
