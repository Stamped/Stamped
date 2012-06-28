//
//  STSimplePlaylistItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STPlaylistItem.h"

@interface STSimplePlaylistItem : NSObject<STPlaylistItem, NSCoding>

@property (nonatomic, readwrite, retain) NSString* name;
@property (nonatomic, readwrite, retain) NSString* subtitle;
@property (nonatomic, readwrite, assign) NSInteger length;
@property (nonatomic, readwrite, retain) NSString* icon;
@property (nonatomic, readwrite, retain) NSString* entityID;
@property (nonatomic, readwrite, retain) NSArray<STImage>* images;
@property (nonatomic, readwrite, retain) id<STAction> action;

+ (RKObjectMapping*)mapping;

+ (STSimplePlaylistItem*)playlistItemWithItem:(id<STPlaylistItem>)item;

@end
