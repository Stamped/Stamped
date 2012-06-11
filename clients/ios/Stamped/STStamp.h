//
//  STStamp.h
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntity.h"
#import "STUser.h"
#import "STComment.h"
#import "STMention.h"
#import "STBadge.h"
#import "STContentItem.h"
#import "STPreviews.h"
#import "STDatum.h"

@protocol STStamp <STDatum>

@required

@property (nonatomic, readonly, copy) NSString* blurb;
@property (nonatomic, readonly, copy) NSDate* created;
@property (nonatomic, readonly, copy) NSNumber* deleted;
@property (nonatomic, readonly, copy) NSString* imageDimensions;
@property (nonatomic, readonly, copy) NSString* imageURL;
@property (nonatomic, readonly, copy) NSNumber* isTodod;
@property (nonatomic, readonly, copy) NSNumber* isLiked;
@property (nonatomic, readonly, copy) NSDate* modified;
@property (nonatomic, readonly, copy) NSDate* stamped;
@property (nonatomic, readonly, copy) NSNumber* numComments;
@property (nonatomic, readonly, copy) NSNumber* numLikes;
@property (nonatomic, readonly, copy) NSString* stampID;
@property (nonatomic, readonly, copy) NSString* URL;
@property (nonatomic, readonly, copy) NSString* via;

@property (nonatomic, readonly, retain) id<STEntity> entity;
@property (nonatomic, readonly, retain) id<STUser> user;
@property (nonatomic, readonly, retain) id<STPreviews> previews;
@property (nonatomic, readonly, copy) NSArray<STMention>* mentions;
@property (nonatomic, readonly, copy) NSArray<STStampPreview>* credits;
@property (nonatomic, readonly, copy) NSArray<STBadge>* badges;
@property (nonatomic, readonly, copy) NSArray<STContentItem>* contents;

@end
