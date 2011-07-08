//
//  StampEntity.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/7/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampEntity.h"

@implementation StampEntity

@synthesize userImage = userImage_;
@synthesize stampImage = stampImage_;
@synthesize name = name_;
@synthesize userName = userName_;
@synthesize comment = comment_;
@synthesize subEntities = subEntities_;
@synthesize type = type_;

- (id)init {
  self = [super init];
  if (self) {
    // Initialization code here.
  }

  return self;
}

@end
