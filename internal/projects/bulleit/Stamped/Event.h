//
//  Event.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class Comment, Stamp, User;

@interface Event : NSManagedObject

@property (nonatomic, retain) NSDate* created;
@property (nonatomic, retain) NSString* genre;
@property (nonatomic, retain) Comment* comment;
@property (nonatomic, retain) Stamp* stamp;
@property (nonatomic, retain) User* user;

@end
