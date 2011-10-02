//
//  Stamp.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/26/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "Stamp.h"
#import "Comment.h"
#import "Entity.h"
#import "Event.h"
#import "User.h"

NSString* kStampDidChangeNotification = @"StampDidChangeNotification";
NSString* kStampWasCreatedNotification = @"StampWasCreatedNotification";

@implementation Stamp

@dynamic blurb;
@dynamic created;
@dynamic modified;
@dynamic numComments;
@dynamic numLikes;
@dynamic isLiked;
@dynamic stampID;
@dynamic entityObject;
@dynamic user;
@dynamic comments;
@dynamic credits;
@dynamic event;
@dynamic favorites;
@dynamic temporary;
@dynamic image;
@dynamic imageURL;
@dynamic imageDimensions;
@dynamic URL;
@dynamic isFavorited;

@end
