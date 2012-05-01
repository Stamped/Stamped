//
//  STScrollViewContainer.m
//  Stamped
//
//  Created by Landon Judkins on 3/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STScrollViewContainer.h"
#import "STActionManager.h"

@interface STScrollViewContainer()

@property (nonatomic, retain) NSMutableArray* children;
@property (nonatomic, retain) NSMutableSet* dependents;

@end

@implementation STScrollViewContainer

@synthesize delegate = delegate_;
@synthesize children = children_;
@synthesize dependents = dependents_;
@dynamic scrollDelegate;

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
    if (delegate && [delegate respondsToSelector:@selector(registerDependent:)]) {
      [delegate registerDependent:self];
    }
  self.contentSize = CGSizeMake(self.frame.size.width, 0);
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
  CGFloat offset = 0;
  if ([self.children count] > 0) {
    UIView* view = [self.children lastObject];
    offset = CGRectGetMaxY(view.frame);
  }
  CGRect frame = child.frame;
  frame.origin.y += offset;
  child.frame = frame;
  CGSize contentSize = self.contentSize;
  contentSize.height = MAX(CGRectGetMaxY(child.frame), self.frame.size.height+1);
  self.contentSize = contentSize;
  [self.children addObject:child];
  [self addSubview:child];
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
  CGFloat containerHeight = self.frame.size.height+1;
  for (UIView* view2 in self.children) {
    CGFloat childHeight = CGRectGetMaxY(view2.frame) + delta;
    containerHeight = MAX(containerHeight, childHeight);
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
  //TODO analyse underflow special case implementation
  if (self.contentSize.height + delta < self.frame.size.height) {
    delta = self.frame.size.height - self.contentSize.height;
  }
  [UIView animateWithDuration:seconds animations:^{
    CGSize size = self.contentSize;
    size.height = containerHeight;
    self.contentSize = size;
  }];
}

//TODO analyse or deprecate
- (void)removeChildView:(UIView*)view withAnimation:(BOOL)animation {
  CGFloat seconds = 0;
  if (animation) {
    seconds = .25;
  }
  CGFloat delta = -view.frame.size.height;
  CGFloat containerHeight = self.frame.size.height+1;
  for (UIView* view2 in self.children) {
    CGFloat childHeight = CGRectGetMaxY(view2.frame) + delta;
    containerHeight = MAX(containerHeight, childHeight);
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
        if (view == view2) {
          [children_ removeObject:view];
          [view removeFromSuperview];
        }
      }];
    }
  }
  if (self.contentSize.height + delta < self.frame.size.height) {
    delta = self.frame.size.height - self.contentSize.height;
  }
  [UIView animateWithDuration:seconds animations:^{
    CGSize size = self.contentSize;
    size.height = containerHeight;
    self.contentSize = size;
  }];
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

- (id<UIScrollViewDelegate>)scrollDelegate {
  return [super delegate];
}

- (void)setScrollDelegate:(id<UIScrollViewDelegate>)scrollDelegate {
  [super setDelegate:scrollDelegate];
}

- (void)reloadStampedData {
  for (id view in self.subviews) {
    if ([view respondsToSelector:@selector(reloadStampedData)]) {
      [view reloadStampedData];
    }
  }
}

- (void)updateContentSize {
  if (self.contentSize.height < self.frame.size.height) {
    self.contentSize = CGSizeMake(self.contentSize.width, self.frame.size.height);
  }
}

@end
