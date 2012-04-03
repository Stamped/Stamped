//
//  STStamp.h
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntity.h"
#import "User.h"

@protocol STStamp <NSObject>

@property (nonatomic, retain) NSString* blurb;
@property (nonatomic, retain) NSDate* created;
@property (nonatomic, retain) NSNumber* deleted;
@property (nonatomic, retain) NSString* imageDimensions;
@property (nonatomic, retain) NSString* imageURL;
@property (nonatomic, retain) NSNumber* isFavorited;
@property (nonatomic, retain) NSNumber* isLiked;
@property (nonatomic, retain) NSDate* modified;
@property (nonatomic, retain) NSNumber* numComments;
@property (nonatomic, retain) NSNumber* numLikes;
@property (nonatomic, retain) NSString* stampID;
@property (nonatomic, retain) NSString* URL;
@property (nonatomic, retain) NSString* via;
@property (nonatomic, retain) NSSet* comments;
@property (nonatomic, retain) NSSet* credits;
@property (nonatomic, retain) NSSet* events;
@property (nonatomic, retain) NSSet* favorites;

@property (nonatomic, readonly, retain) NSString* entityID;
@property (nonatomic, readonly, retain) NSString* userID;

@end
