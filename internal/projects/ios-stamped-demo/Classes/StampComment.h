//
//  StampComment.h
//  Stamped
//
//  Created by Kevin Palms on 2/6/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import <CoreData/CoreData.h>


@interface StampComment :  NSManagedObject  
{
}

@property (nonatomic, retain) NSDate * dateAdded;
@property (nonatomic, retain) NSNumber * stampId;
@property (nonatomic, retain) NSString * message;
@property (nonatomic, retain) NSNumber * userId;

@end



