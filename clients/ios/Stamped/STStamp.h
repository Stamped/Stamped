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
#import "STCredit.h"

@protocol STStamp <NSObject>

@property (nonatomic, readonly, copy) NSString* blurb;
@property (nonatomic, readonly, copy) NSDate* created;
@property (nonatomic, readonly, copy) NSNumber* deleted;
@property (nonatomic, readonly, copy) NSString* imageDimensions;
@property (nonatomic, readonly, copy) NSString* imageURL;
@property (nonatomic, readonly, copy) NSNumber* isFavorited;
@property (nonatomic, readonly, copy) NSNumber* isLiked;
@property (nonatomic, readonly, copy) NSDate* modified;
@property (nonatomic, readonly, copy) NSNumber* numComments;
@property (nonatomic, readonly, copy) NSNumber* numLikes;
@property (nonatomic, readonly, copy) NSString* stampID;
@property (nonatomic, readonly, copy) NSString* URL;
@property (nonatomic, readonly, copy) NSString* via;

@property (nonatomic, readonly, copy) id<STEntity> entity;
@property (nonatomic, readonly, copy) id<STUser> user;
@property (nonatomic, readonly, copy) NSArray<STComment>* commentsPreview;
@property (nonatomic, readonly, copy) NSArray<STMention>* mentions;
@property (nonatomic, readonly, copy) NSArray<STCredit>* credits;

@end
