// 
//  Stamp.m
//  Stamped
//
//  Created by Kevin Palms on 2/6/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "Stamp.h"


@implementation Stamp 


+ (void)addStampWithId:(NSNumber *)stampId fromUser:(NSNumber *)userId withData:(NSDictionary *)stampData inManagedObjectContext:(NSManagedObjectContext *)context
{
	Stamp *stamp = nil;
	
	NSFetchRequest *fetchRequest = [[NSFetchRequest alloc] init];
	fetchRequest.entity = [NSEntityDescription entityForName:@"Stamp" inManagedObjectContext:context];
	fetchRequest.predicate = [NSPredicate predicateWithFormat:@"stampId = %@", stampId];
	
	NSError *error = nil;
	stamp = [[context executeFetchRequest:fetchRequest error:&error] lastObject];
	[fetchRequest release];
	
	if (!error && !stamp) {
		stamp = [NSEntityDescription insertNewObjectForEntityForName:@"Stamp" inManagedObjectContext:context];
		
		stamp.stampId	= stampId;
		stamp.userId	= userId;
		stamp.stampType	= [stampData objectForKey:@"stampType"];
		stamp.title		= [stampData objectForKey:@"title"];
		stamp.message	= [stampData objectForKey:@"message"];
		stamp.author	= [stampData objectForKey:@"author"];
		stamp.address	= [stampData objectForKey:@"address"];
		stamp.dateStamped	= [stampData objectForKey:@"dateStamped"];
		stamp.urlWebsite	= [stampData objectForKey:@"urlWebsite"];
		
		// TEMP
		NSLog(@"Stamp added: %@", stamp);
		
		// Save?
	}
}

+ (Stamp *)stampWithId:(NSNumber *)stampId inManagedObjectContext:(NSManagedObjectContext *)context
{
	Stamp *stamp = nil;
	
	NSFetchRequest *fetchRequest = [[NSFetchRequest alloc] init];
	fetchRequest.entity = [NSEntityDescription entityForName:@"Stamp" inManagedObjectContext:context];
	fetchRequest.predicate = [NSPredicate predicateWithFormat:@"stampId = %@", stampId];
	
	NSError *error = nil;
	stamp = [[context executeFetchRequest:fetchRequest error:&error] lastObject];
	[fetchRequest release];
	
	if (error || !stamp) {
		return nil;
	}
	
	return stamp;
}

+ (void)toggleStar:(NSNumber *)isStarred forStampId:(NSNumber *)stampId inManagedObjectContext:(NSManagedObjectContext *)context
{
	Stamp *stamp = nil;
	
	NSFetchRequest *fetchRequest = [[NSFetchRequest alloc] init];
	fetchRequest.entity = [NSEntityDescription entityForName:@"Stamp" inManagedObjectContext:context];
	fetchRequest.predicate = [NSPredicate predicateWithFormat:@"stampId = %@", stampId];
	
	NSError *error = nil;
	stamp = [[context executeFetchRequest:fetchRequest error:&error] lastObject];
	[fetchRequest release];
	
	stamp.isStarred = ([isStarred boolValue]) ? [NSNumber numberWithBool:YES] : [NSNumber numberWithBool:NO];
	NSLog(@"Stamp star: %@", isStarred);
	
}

@dynamic address;
@dynamic author;
@dynamic stampType;
@dynamic dateStamped;
@dynamic dateStarred;
@dynamic title;
@dynamic isStarred;
@dynamic message;
@dynamic dateRead;
@dynamic urlWebsite;
@dynamic stampId;
@dynamic userId;

@end
