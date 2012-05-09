//
//  STCommentButton.m
//  Stamped
//
//  Created by Landon Judkins on 5/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCommentButton.h"

@implementation STCommentButton

@synthesize block = block_;

- (id)initWithCallback:(void (^)(void))block {
  self = [super initWithNormalOffImage:[UIImage imageNamed:@"sDetailBar_btn_comment"] offText:@"Comment" andOnText:@"Comment"];
  if (self) {
    self.touchedOffImage = [UIImage imageNamed:@"sDetailBar_btn_comment_active"];
    self.touchedOnImage= [UIImage imageNamed:@"sDetailBar_btn_comment_active"];
    self.normalOffImage = [UIImage imageNamed:@"sDetailBar_btn_comment"];
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
    self.block();
  }
}
/*
// Only override drawRect: if you perform custom drawing.
// An empty implementation adversely affects performance during animation.
- (void)drawRect:(CGRect)rect
{
    // Drawing code
}
*/

@end
