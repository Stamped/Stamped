//
//  STViewContainer.m
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"
#import "STViewDelegateDependent.h"

@interface STViewContainer ()

@property (nonatomic, retain) NSMutableArray* children;
@property (nonatomic, retain) NSMutableSet* dependents;

@end

@implementation STViewContainer

@synthesize delegate = delegate_;
@synthesize children = children_;
@synthesize dependents = dependents_;

static int _count = 0;

- (id)initWithDelegate:(id<STViewDelegate>)delegate andFrame:(CGRect)frame
{
  self = [super initWithFrame:frame];
  if (self) {
    _count++;
    self.children = [NSMutableArray array];
    dependents_ = [[NSMutableSet alloc] init];
    self.delegate = delegate;
    self.backgroundColor = [UIColor clearColor];
    [delegate registerDependent:self];
  }
  return self;
}

- (void)dealloc {
  _count--;
  self.children = nil;
  self.delegate = nil;
  for (id<STViewDelegateDependent> dependent in self.dependents) {
    dependent.delegate = nil;
  }
  [dependents_ release];
  [super dealloc];
}

- (void)appendChildView:(UIView*)child {
  CGRect frame = child.frame;
  frame.origin.y = self.frame.size.height;
  child.frame = frame;
  frame = self.frame;
  frame.size.height += child.frame.size.height;
  self.frame = frame;
  [self.children addObject:child];
  [self addSubview:child];
}

- (void)didChooseAction:(id<STAction>)action {
  if (self.delegate && [self.delegate respondsToSelector:@selector(didChooseAction:)]) {
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
  if (self.delegate && [self.delegate respondsToSelector:@selector(childView:shouldChangeHeightBy:overDuration:)]) {
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
  if (self.delegate && [self.delegate respondsToSelector:@selector(didChooseSource:forAction:)]) {
    [self.delegate didChooseSource:source forAction:action];
  }
}

- (void)registerDependent:(id<STViewDelegateDependent>)dependent {
  [self.dependents addObject:dependent];
}

- (void)setDelegate:(id<STViewDelegate>)delegate {
  delegate_ = delegate;
}

@end
