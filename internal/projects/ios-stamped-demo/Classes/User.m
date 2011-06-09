// 
//  User.m
//  Stamped
//
//  Created by Kevin Palms on 2/6/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "User.h"
#import "Stamp.h"

@implementation User 


+ (void)addUserWithId:(NSNumber *)userId withName:(NSString *)userName inManagedObjectContext:(NSManagedObjectContext *)context
{
	User *user = nil;
	
	NSFetchRequest *fetchRequest = [[NSFetchRequest alloc] init];
	fetchRequest.entity = [NSEntityDescription entityForName:@"User" inManagedObjectContext:context];
	fetchRequest.predicate = [NSPredicate predicateWithFormat:@"userId = %@", userId];
	
	NSError *error = nil;
	user = [[context executeFetchRequest:fetchRequest error:&error] lastObject];
	[fetchRequest release];
	
	if (!error && !user) {
		user = [NSEntityDescription insertNewObjectForEntityForName:@"User" inManagedObjectContext:context];
		user.userId = userId;
		user.name = userName;
		
		// TEMP
		NSLog(@"User added: %@", user);
		
		// Save?
	}
}

+ (User *)userWithId:(NSNumber *)userId inManagedObjectContext:(NSManagedObjectContext *)context
{
	User *user = nil;
	
	NSFetchRequest *fetchRequest = [[NSFetchRequest alloc] init];
	fetchRequest.entity = [NSEntityDescription entityForName:@"User" inManagedObjectContext:context];
	fetchRequest.predicate = [NSPredicate predicateWithFormat:@"userId = %@", userId];
	
	NSError *error = nil;
	user = [[context executeFetchRequest:fetchRequest error:&error] lastObject];
	[fetchRequest release];
	
	if (error || !user) {
		return nil;
	}
	
	return user;
}

- (NSArray *)usersStamps 
{
	return nil;
}

- (NSArray *)usersComments
{
	return nil;
}

@dynamic name;
@dynamic userId;

@end
