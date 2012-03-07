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

@interface STSimplePlaylistItem : NSObject<STPlaylistItem>

@property (nonatomic, readwrite, retain) NSString* name;
@property (nonatomic, readwrite, assign) NSInteger num;
@property (nonatomic, readwrite, assign) NSInteger length;
@property (nonatomic, readwrite, retain) NSString* icon;
@property (nonatomic, readwrite, retain) NSString* link;
@property (nonatomic, readwrite, retain) NSArray<STSource>* sources;

+ (RKObjectMapping*)mapping;

@end
