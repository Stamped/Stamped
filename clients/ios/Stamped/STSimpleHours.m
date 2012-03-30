//
//  STSimpleHours.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleHours.h"

@implementation STSimpleHours

@synthesize open = _open;
@synthesize close = _close;
@synthesize desc = _desc;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleHours class]];
  
  [mapping mapAttributes:
   @"open",
   @"close",
   @"desc",
   nil];
  
  return mapping;
}

@end
