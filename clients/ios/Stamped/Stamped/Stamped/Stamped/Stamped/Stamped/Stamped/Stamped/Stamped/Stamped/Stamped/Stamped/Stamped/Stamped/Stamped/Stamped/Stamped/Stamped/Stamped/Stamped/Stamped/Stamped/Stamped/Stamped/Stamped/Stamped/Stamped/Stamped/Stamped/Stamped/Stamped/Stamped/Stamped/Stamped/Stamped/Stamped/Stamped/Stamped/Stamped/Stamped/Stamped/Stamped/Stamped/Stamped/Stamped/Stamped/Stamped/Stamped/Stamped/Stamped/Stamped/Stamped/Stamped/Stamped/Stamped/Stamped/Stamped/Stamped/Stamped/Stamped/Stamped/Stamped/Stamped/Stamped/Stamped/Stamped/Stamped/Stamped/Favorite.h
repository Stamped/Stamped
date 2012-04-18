//
//  Favorite.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class Entity;
@class Stamp;

@interface Favorite : NSManagedObject {
@private
}
@property (nonatomic, retain) NSString* favoriteID;
@property (nonatomic, retain) NSNumber* complete;
@property (nonatomic, retain) NSDate* created;
@property (nonatomic, retain) NSString* userID;
@property (nonatomic, retain) Entity* entityObject;
@property (nonatomic, retain) Stamp* stamp;

@end
