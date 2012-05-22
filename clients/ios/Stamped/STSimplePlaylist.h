//
//  STSimplePlaylist.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STPlaylist.h"

@interface STSimplePlaylist : NSObject<STPlaylist, NSCoding>

@property (nonatomic, readwrite, retain) NSString* name;
@property (nonatomic, readwrite, assign) NSInteger overflow;
@property (nonatomic, readwrite, retain) NSArray<STPlaylistItem>* data;

+ (RKObjectMapping*)mapping;

@end
