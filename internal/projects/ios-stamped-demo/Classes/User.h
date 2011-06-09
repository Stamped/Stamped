//
//  User.h
//  Stamped
//
//  Created by Kevin Palms on 2/6/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>


@interface User :  NSManagedObject  
{
}

+ (void)addUserWithId:(NSNumber *)userId withName:(NSString *)userName inManagedObjectContext:(NSManagedObjectContext *)context;
+ (User *)userWithId:(NSNumber *)userId inManagedObjectContext:(NSManagedObjectContext *)context;

- (NSArray *)usersStamps;
- (NSArray *)usersComments;

@property (nonatomic, retain) NSString * name;
@property (nonatomic, retain) NSNumber * userId;

@end



