//
//  TooltipView.m
//  Stamped
//
//  Created by Jake Zien on 9/16/11.
//  Copyright 2011 RISD. All rights reserved.
//

#import "TooltipView.h"

@implementation TooltipView

- (id)initWithImage:(UIImage *)image {
  self = [super initWithImage:image];
  if (self) {
    self.userInteractionEnabled = YES;
  }
  return self;
}

- (void)touchesEnded:(NSSet *)touches withEvent:(UIEvent *)event {
  [UIView animateWithDuration:0.3 animations:^{self.alpha = 0.0;} completion:^(BOOL finished){self.hidden = YES;}];
}

@end
