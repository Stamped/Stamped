//
//  STShareButton.m
//  Stamped
//
//  Created by Landon Judkins on 5/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STShareButton.h"

@implementation STShareButton

@synthesize block = block_;

- (id)initWithCallback:(void (^)(void))block {
  self = [super initWithNormalOffImage:[UIImage imageNamed:@"NEW_share"] offText:@"Share" andOnText:@"Shared"];
  if (self) {
    self.touchedOffImage = [UIImage imageNamed:@"NEW_share-white"];
    self.touchedOnImage= [UIImage imageNamed:@"NEW_share-white"];
    self.normalOffImage = [UIImage imageNamed:@"NEW_share"];
    self.block = block;
  }
  return self;
}

- (void)dealloc
{
  [block_ release];
  [super dealloc];
}


- (void)defaultHandler:(id)myself {
  if (self.block) {
      self.on = NO;
    self.block();
  }
}

@end
