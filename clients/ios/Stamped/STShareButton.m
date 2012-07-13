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
  self = [super initWithNormalOffImage:[UIImage imageNamed:@"sDetailBar_btn_share"] offText:@"Share" andOnText:@"Shared"];
  if (self) {
    self.touchedOffImage = [UIImage imageNamed:@"sDetailBar_btn_share_active"];
    self.touchedOnImage= [UIImage imageNamed:@"sDetailBar_btn_share_active"];
    self.normalOffImage = [UIImage imageNamed:@"sDetailBar_btn_share"];
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
