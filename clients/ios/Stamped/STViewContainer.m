//
//  STViewContainer.m
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"

@interface STViewContainer ()

@property (nonatomic, retain) NSMutableArray* children;

@end

@implementation STViewContainer

@synthesize delegate = delegate_;
@synthesize children = children_;

- (id)initWithFrame:(CGRect)frame
{
    self = [super initWithFrame:frame];
    if (self) {
      children_ = [[NSMutableArray alloc] init];
      self.backgroundColor = [UIColor clearColor];
    }
    return self;
}

- (void)dealloc {
  [children_ release];
  self.delegate = nil;
  [super dealloc];
}

- (void)appendChild:(UIView*)child {
  CGRect frame = child.frame;
  frame.origin.y = CGRectGetMaxY(self.frame);
  child.frame = frame;
  frame = self.frame;
  frame.size.height += child.frame.size.height;
  self.frame = frame;
  [self.children addObject:child];
  [self addSubview:child];
}

- (void)didLoad:(id)object withLabel:(id)label {
  if (self.delegate) {
    [self.delegate didLoad:object withLabel:label];
  }
}

- (void)view:(UIView*)view didChooseAction:(id<STAction>)action {
  if (self.delegate) {
    [self.delegate view:view didChooseAction:action];
  }
}

- (void)view:(UIView*)view willChangeHeightBy:(CGFloat)delta over:(CGFloat)seconds {
  for (UIView* view2 in self.children) {
    if (view2 == view || CGRectGetMinY(view2.frame) > CGRectGetMinY(view.frame)) {
      [UIView animateWithDuration:seconds animations:^{
        if (view2 == view) {
          CGRect frame = view2.frame;
          frame.size.height += delta;
          view2.frame = frame;
        }
        else {
          view2.frame = CGRectOffset(view2.frame, 0, delta);
        }
      }];
    }
  }
  [self.delegate view:self willChangeHeightBy:delta over:seconds];
}


@end
