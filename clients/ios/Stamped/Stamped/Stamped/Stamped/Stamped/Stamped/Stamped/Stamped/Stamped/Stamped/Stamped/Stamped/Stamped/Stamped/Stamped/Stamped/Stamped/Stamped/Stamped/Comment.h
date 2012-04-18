//
//  Comment.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/20/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class User;

@interface Comment : NSManagedObject

@property (nonatomic, retain) NSString* blurb;
@property (nonatomic, retain) NSString* commentID;
@property (nonatomic, retain) NSString* stampID;
@property (nonatomic, retain) NSString* restampID;
@property (nonatomic, retain) NSDate* created;
@property (nonatomic, retain) User* user;

@end
