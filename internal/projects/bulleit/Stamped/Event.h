//
//  Event.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/31/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class Stamp;
@class Entity;
@class User;

@interface Event : NSManagedObject

@property (nonatomic, retain) NSDate* created;
@property (nonatomic, retain) NSString* genre;
@property (nonatomic, retain) NSString* eventID;
@property (nonatomic, retain) NSNumber* benefit;
@property (nonatomic, retain) NSString* blurb;
@property (nonatomic, retain) NSString* subject;
@property (nonatomic, retain) NSString* URL;
@property (nonatomic, retain) Stamp* stamp;
@property (nonatomic, retain) User* user;
@property (nonatomic, retain) Entity* entityObject;

@end
