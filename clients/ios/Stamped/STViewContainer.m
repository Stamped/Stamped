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
@property (nonatomic, assign) id<STViewDelegate> delegate;

@end

@implementation STViewContainer

@dynamic asyncQueue;
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
  NSLog(@"dealloc STViewContainer");
  self.children = nil;
  self.delegate = nil;
  [super dealloc];
}

- (void)appendChild:(UIView*)child {
  CGRect frame = child.frame;
  frame.origin.y = self.frame.size.height;
  NSLog(@"Child frame: %f,%f,%f,%f,%@",frame.origin.x,frame.origin.y,frame.size.width,frame.size.height,self);
  child.frame = frame;
  frame = self.frame;
  frame.size.height += child.frame.size.height;
  self.frame = frame;
  [self.children addObject:child];
  [self addSubview:child];
}

- (void)didLoad:(id)object withLabel:(id)label {
  [self.delegate didLoad:object withLabel:label];
}

- (void)didChooseAction:(id<STAction>)action {
  [self.delegate didChooseAction:action];
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

- (NSOperationQueue*)asyncQueue {
  return self.delegate.asyncQueue;
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action {
  [self.delegate didChooseSource:source forAction:action];
}

@end
