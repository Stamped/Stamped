//
//  Stamp.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/18/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreData/CoreData.h>


@interface Stamp : NSManagedObject

@property (nonatomic, retain) NSString* stampID;
@property (nonatomic, retain) NSString* title;
@property (nonatomic, retain) NSString* subtitle;
@property (nonatomic, retain) NSManagedObject* Account;

@end
