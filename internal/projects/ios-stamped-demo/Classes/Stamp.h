//
//  Stamp.h
//  Stamped
//
//  Created by Kevin Palms on 2/6/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>


@interface Stamp :  NSManagedObject  
{
}

+ (void)addStampWithId:(NSNumber *)stampId fromUser:(NSNumber *)userId withData:(NSDictionary *)stampData inManagedObjectContext:(NSManagedObjectContext *)context;
+ (Stamp *)stampWithId:(NSNumber *)stampId inManagedObjectContext:(NSManagedObjectContext *)context;
+ (void)toggleStar:(NSNumber *)isStarred forStampId:(NSNumber *)stampId inManagedObjectContext:(NSManagedObjectContext *)context;

@property (nonatomic, retain) NSString * address;
@property (nonatomic, retain) NSString * author;
@property (nonatomic, retain) NSString * stampType;
@property (nonatomic, retain) NSDate * dateStamped;
@property (nonatomic, retain) NSDate * dateStarred;
@property (nonatomic, retain) NSString * title;
@property (nonatomic, retain) NSNumber * isStarred;
@property (nonatomic, retain) NSString * message;
@property (nonatomic, retain) NSDate * dateRead;
@property (nonatomic, retain) NSString * urlWebsite;
@property (nonatomic, retain) NSNumber * stampId;
@property (nonatomic, retain) NSNumber * userId;

@end



