//
//  STSimpleStamp.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStamp.h"
#import <RestKit/RestKit.h>

@interface STSimpleStamp : NSObject

@property (nonatomic, readwrite, copy) NSString* blurb;
@property (nonatomic, readwrite, copy) NSDate* created;
@property (nonatomic, readwrite, copy) NSNumber* deleted;
@property (nonatomic, readwrite, copy) NSString* imageDimensions;
@property (nonatomic, readwrite, copy) NSString* imageURL;
@property (nonatomic, readwrite, copy) NSNumber* isFavorited;
@property (nonatomic, readwrite, copy) NSNumber* isLiked;
@property (nonatomic, readwrite, copy) NSDate* modified;
@property (nonatomic, readwrite, copy) NSNumber* numComments;
@property (nonatomic, readwrite, copy) NSNumber* numLikes;
@property (nonatomic, readwrite, copy) NSString* stampID;
@property (nonatomic, readwrite, copy) NSString* URL;
@property (nonatomic, readwrite, copy) NSString* via;

@property (nonatomic, readwrite, copy) id<STEntity> entity;
@property (nonatomic, readwrite, copy) id<STUser> user;
@property (nonatomic, readwrite, copy) NSArray<STComment>* commentsPreview;
@property (nonatomic, readwrite, copy) NSArray<STMention>* mentions;
@property (nonatomic, readwrite, copy) NSArray<STCredit>* credits;

+ (RKObjectMapping*)mapping;

@end
