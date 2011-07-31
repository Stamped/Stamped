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
#import "User.h"

NSString* kStampDidChangeNotification = @"StampDidChangeNotification";
NSString* kStampWasCreatedNotification = @"StampWasCreatedNotification";

@implementation Stamp

@dynamic blurb;
@dynamic created;
@dynamic numComments;
@dynamic stampID;
@dynamic entityObject;
@dynamic user;
@dynamic comments;

@end
