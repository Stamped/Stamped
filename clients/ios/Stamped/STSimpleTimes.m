//
//  STSimpleTimes.m
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleTimes.h"
#import "STSimpleHours.h"

@implementation STSimpleTimes

@synthesize sun = _sun;
@synthesize mon = _mon;
@synthesize tue = _tue;
@synthesize wed = _wed;
@synthesize thu = _thu;
@synthesize fri = _fri;
@synthesize sat = _sat;

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleTimes class]];
  
  RKObjectMapping* hoursMapping = [STSimpleHours mapping];
  
  NSArray* days = [NSArray arrayWithObjects:@"sun", @"mon", @"tue", @"wed", @"thu", @"fri" @"sat", nil];
  
  for (NSString* day in days) {
    [mapping mapRelationship:day withMapping:hoursMapping];
  }
  
  return mapping;
}

@end
