//
//  Entity.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/20/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>

@class Stamp;

@interface Entity : NSManagedObject {
@private
}
@property (nonatomic, retain) NSString * category;
@property (nonatomic, retain) NSString * entityID;
@property (nonatomic, retain) NSString * subtitle;
@property (nonatomic, retain) NSString * title;
@property (nonatomic, retain) <<NIL>> *coordinates;
@property (nonatomic, retain) Stamp *stamp;

@end
