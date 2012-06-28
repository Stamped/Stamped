//
//  STPlaylistItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STSource.h"
#import "STAction.h"
#import "STImage.h"

@protocol STPlaylistItem <NSObject>

@property (nonatomic, readonly, retain) NSString* name;
@property (nonatomic, readonly, retain) NSString* subtitle;
@property (nonatomic, readonly, assign) NSInteger length;
@property (nonatomic, readonly, retain) NSString* icon;
@property (nonatomic, readonly, retain) NSString* entityID;
@property (nonatomic, readonly, retain) NSArray<STImage>* images;
@property (nonatomic, readonly, retain) id<STAction> action;

@end
