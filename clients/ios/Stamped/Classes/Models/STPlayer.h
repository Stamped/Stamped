//
//  STPlayer.h
//  Stamped
//
//  Created by Landon Judkins on 6/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STPlaylistItem.h"

extern NSString* const STPlayerItemChangedNotification;
extern NSString* const STPlayerStateChangedNotification;
extern NSString* const STPlayerPlaylistChangedNotification;

extern NSString* const STPlayerCummulativeKey;
extern NSString* const STPlayerRevertKey;
extern NSString* const STPlayerFullFooterKey;

@interface STPlayer : NSObject

+ (STPlayer*)sharedInstance;

- (void)seekToItemAtIndex:(NSInteger)index;
- (BOOL)addPlaylistItem:(id<STPlaylistItem>)item atIndex:(NSInteger)index;
- (id<STPlaylistItem>)itemAtIndex:(NSInteger)index;
- (void)removeItemAtIndex:(NSInteger)index;
- (void)moveItemAtIndex:(NSInteger)index toIndex:(NSInteger)destination;
- (NSInteger)currentItemIndex;
- (NSInteger)itemCount;
- (void)clear;
- (void)playKatyPerry;

@property (nonatomic, readwrite, assign) BOOL paused;

+ (void)setupConfigurations;

@end
