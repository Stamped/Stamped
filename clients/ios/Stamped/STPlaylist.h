//
//  STPlaylist.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STPlaylistItem;

@protocol STPlaylist <NSObject>

@property (nonatomic, readonly, retain) NSString* name;
@property (nonatomic, readonly, assign) NSInteger overflow;
@property (nonatomic, readonly, retain) NSArray<STPlaylistItem>* data;

@end
