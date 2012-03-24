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

- (id)initWithDelegate:(id<STViewDelegate>)delegate andFrame:(CGRect)frame
{
  self = [super initWithFrame:frame];
  if (self) {
    self.children = [NSMutableArray array];
    self.delegate = delegate;
    self.backgroundColor = [UIColor clearColor];
  }
  return self;
}

- (void)dealloc {
  self.children = nil;
  self.delegate = nil;
  [super dealloc];
}

- (void)appendChildView:(UIView*)child {
  CGRect frame = child.frame;
  frame.origin.y = self.frame.size.height;
  //NSLog(@"Child frame: %f,%f,%f,%f,%@",frame.origin.x,frame.origin.y,frame.size.width,frame.size.height,self);
  child.frame = frame;
  frame = self.frame;
  frame.size.height += child.frame.size.height;
  self.frame = frame;
  [self.children addObject:child];
  [self addSubview:child];
}

- (void)didChooseAction:(id<STAction>)action {
  if (self.delegate) {
    [self.delegate didChooseAction:action];
  }
}

- (void)childView:(UIView*)view shouldChangeHeightBy:(CGFloat)delta overDuration:(CGFloat)seconds {
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
  if (self.delegate) {
    [self.delegate childView:self shouldChangeHeightBy:delta overDuration:seconds];
  }
  else {
    [UIView animateWithDuration:seconds animations:^{
      CGRect frame = self.frame;
      frame.size.height += delta;
      self.frame = frame;
    }];
  }
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action {
  if (self.delegate) {
    [self.delegate didChooseSource:source forAction:action];
  }
}

@end
