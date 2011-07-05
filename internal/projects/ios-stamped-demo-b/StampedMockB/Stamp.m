//
//  Stamp.m
//  StampedMockB
//
//  Created by Kevin Palms on 6/28/11.
//  Copyright (c) 2011 __MyCompanyName__. All rights reserved.
//

#import "Stamp.h"


@implementation Stamp

+ (void)addStampWithData:(NSDictionary *)stampData inManagedObjectContext:(NSManagedObjectContext *)context
{
  Stamp *stamp = nil;
  stamp = [NSEntityDescription insertNewObjectForEntityForName:@"Stamp" inManagedObjectContext:context];
  
  stamp.title = [stampData objectForKey:@"title"];
  stamp.subTitle = [stampData objectForKey:@"subTitle"];
  stamp.comment = [stampData objectForKey:@"comment"];
  stamp.avatar = [stampData objectForKey:@"avatar"];
  stamp.stampImage = [stampData objectForKey:@"stampImage"];
  stamp.hasPhoto = [stampData objectForKey:@"hasPhoto"];
  stamp.category = [stampData objectForKey:@"category"];
  stamp.color = [stampData objectForKey:@"color"];
  stamp.userName = [stampData objectForKey:@"userName"];
  
  NSLog(@"Stamp added: %@", stamp);
}

@dynamic title;
@dynamic subTitle;
@dynamic avatar;
@dynamic userID;
@dynamic stampImage;
@dynamic hasPhoto;
@dynamic hasMention;
@dynamic hasRestamp;
@dynamic comment;
@dynamic category;
@dynamic color;
@dynamic userName;

@end
