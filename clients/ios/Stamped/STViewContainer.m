//
//  STViewContainer.m
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewContainer.h"
#import "STViewDelegateDependent.h"
#import "STActionManager.h"

@interface STViewContainer ()

@property (nonatomic, retain) NSMutableArray* children;
@property (nonatomic, retain) NSMutableSet* dependents;

@end

@implementation STViewContainer

@synthesize delegate = delegate_;
@synthesize children = children_;
@synthesize dependents = dependents_;

static int _count = 0;

- (id)initWithDelegate:(id<STViewDelegate>)delegate andFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    _count++;
    self.children = [NSMutableArray array];
    dependents_ = [[NSMutableSet alloc] init];
    self.delegate = delegate;
    self.backgroundColor = [UIColor clearColor];
    //self.backgroundColor = [UIColor colorWithRed:.1 green:0 blue:0 alpha:.1];
    if (delegate && [delegate respondsToSelector:@selector(registerDependent:)]) {
      [delegate registerDependent:self];
    }
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

- (void)appendChildView:(UIView*)child withAnimation:(BOOL)animation {
  if (self.superview && animation) {
    //TODO improve or remove
    CGRect childFrame = child.frame;
    CGFloat childHeight = childFrame.size.height;
    childFrame.origin.y += self.frame.size.height;
    childFrame.size.height = 0;
    child.frame = childFrame;
    BOOL childClipsToBounds = child.clipsToBounds;
    CGFloat childAlpha = child.alpha;
    child.clipsToBounds = YES;
    child.alpha = 0;
    [self.children addObject:child];
    [self addSubview:child];
    //Child has been set to clip, has alpha 0, has height 0, and has been configured as a child
    [self childView:child shouldChangeHeightBy:childHeight overDuration:.25];
    [UIView animateWithDuration:.25 animations:^{
      child.alpha = childAlpha;
    } completion:^(BOOL finished) {
      child.clipsToBounds = childClipsToBounds;
    }];
    return;
  }
  else {
    CGRect frame = child.frame;
    frame.origin.y += self.frame.size.height;
    child.frame = frame;
    frame = self.frame;
    frame.size.height = CGRectGetMaxY(child.frame);
    self.frame = frame;
    [self.children addObject:child];
    [self addSubview:child];
  }
}

- (void)appendChildView:(UIView*)child {
  [self appendChildView:child withAnimation:NO];
}

- (void)removeChildView:(UIView*)view withAnimation:(BOOL)animation {
  CGFloat seconds = .25;
  CGFloat delta = -view.frame.size.height;
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
      } completion:^(BOOL finished) {
        if (view2 == view) {
          [self.children removeObject:view];
          [view removeFromSuperview];
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

- (void)didChooseAction:(id<STAction>)action withContext:(STActionContext*)context {
  if (self.delegate && [self.delegate respondsToSelector:@selector(didChooseAction:)]) {
    [self.delegate didChooseAction:action withContext:context];
  }
  else {
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
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

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
  if (self.delegate && [self.delegate respondsToSelector:@selector(canHandleSource:forAction:)]) {
    return [self.delegate canHandleSource:source forAction:action withContext:context];
  }
  else {
    return [[STActionManager sharedActionManager] canHandleSource:source forAction:action withContext:context];
  }
  
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
  if (self.delegate && [self.delegate respondsToSelector:@selector(didChooseSource:forAction:)]) {
    [self.delegate didChooseSource:source forAction:action withContext:context];
  }
  else {
    [[STActionManager sharedActionManager] didChooseSource:source forAction:action withContext:context];
  }
}

- (void)registerDependent:(id<STViewDelegateDependent>)dependent {
  [self.dependents addObject:dependent];
}

- (void)setDelegate:(id<STViewDelegate>)delegate {
  delegate_ = delegate;
}

- (void)reloadStampedData {
  for (id view in self.subviews) {
    if ([view respondsToSelector:@selector(reloadStampedData)]) {
      [view reloadStampedData];
    }
  }
}

@end
