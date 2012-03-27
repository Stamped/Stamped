//
//  STViewDelegateProxy.m
//  Stamped
//
//  Created by Landon Judkins on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewDelegateProxy.h"

@implementation STViewDelegateProxy

@synthesize delegate = _delegate;

- (void)didChooseAction:(id<STAction>)action {
  if (self.delegate && [self.delegate respondsToSelector:@selector(didChooseAction:)]) {
    [self.delegate didChooseAction:action];
  }
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action {
  if (self.delegate && [self.delegate respondsToSelector:@selector(didChooseSource:forAction:)]) {
    [self.delegate didChooseSource:source forAction:action];
  }
}

- (void)childView:(UIView*)view shouldChangeHeightBy:(CGFloat)delta overDuration:(CGFloat)seconds {
  if (self.delegate && [self.delegate respondsToSelector:@selector(childView:shouldChangeHeightBy:overDuration:)]) {
    [self.delegate childView:view shouldChangeHeightBy:delta overDuration:seconds];
  }
}

@end
