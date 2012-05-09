//
//  STSimpleActivityCount.m
//  Stamped
//
//  Created by Landon Judkins on 5/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleActivityCount.h"

@implementation STSimpleActivityCount

@synthesize numberUnread = numberUnread_;

- (void)dealloc
{
  [numberUnread_ release];
  [super dealloc];
}


+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleActivityCount class]];
  
  [mapping mapKeyPathsToAttributes: 
   @"num_unread", @"numberUnread",
   nil];
  
  return mapping;
}

@end
