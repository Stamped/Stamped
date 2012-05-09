//
//  STConsumptionToolbarItem.m
//  Stamped
//
//  Created by Landon Judkins on 5/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionToolbarItem.h"

@implementation STConsumptionToolbarItem

@synthesize name = name_;
@synthesize icon = icon_;
@synthesize backIcon = backIcon_;
@synthesize value = value_;
@synthesize parent = parent_;
@synthesize children = children_;
@synthesize type = type_;

- (id)init {
  self = [super init];
  if (self) {
    children_ = [[NSArray alloc] init];
  }
  return self;
}

- (void)dealloc
{
  [name_ release];
  [icon_ release];
  [backIcon_ release];
  [value_ release];
  [parent_ release];
  [children_ release];
  [type_ release];
  [super dealloc];
}

- (void)setChildren:(NSArray *)children {
  [children_ autorelease];
  children_ = [children copy];
  for (STConsumptionToolbarItem* child in children) {
    child.parent = self;
  }
}

@end
