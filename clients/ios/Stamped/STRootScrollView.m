//
//  STRootScrollView.m
//  Stamped
//
//  Created by Landon Judkins on 4/21/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRootScrollView.h"
#import "Util.h"
#import "STRootMenuView.h"

@interface STRootScrollView ()

@property (nonatomic, readonly, retain) UIViewController* controller;

@end

@implementation STRootScrollView

@synthesize controller = controller_;

- (id)initWithRootViewController:(UIViewController*)controller
{
  self = [super initWithFrame:CGRectMake(0, 0, 320, 480)];
  if (self) {
    self.contentSize = CGSizeMake(self.frame.size.width+400, self.frame.size.height);
    [Util reframeView:controller.view withDeltas:CGRectMake(200, 0, 0, 0)];
    [self addSubview:controller.view];
    controller_ = [controller retain];
  }
  return self;
}

- (void)touchesBegan:(NSSet *)touches withEvent:(UIEvent *)event {
  UITouch* touch = [touches anyObject];
  if (CGRectContainsPoint(self.controller.view.frame, [touch locationInView:self])) {
    [super touchesBegan:touches withEvent:event];
  }
  else {
    [[STRootMenuView sharedInstance] touchesBegan:touches withEvent:event];
  }
}

- (void)touchesCancelled:(NSSet *)touches withEvent:(UIEvent *)event {
  UITouch* touch = [touches anyObject];
  if (CGRectContainsPoint(self.controller.view.frame, [touch locationInView:self])) {
    [super touchesCancelled:touches withEvent:event];
  }
  else {
    [[STRootMenuView sharedInstance] touchesCancelled:touches withEvent:event];
  }
}

- (void)touchesEnded:(NSSet *)touches withEvent:(UIEvent *)event {
  UITouch* touch = [touches anyObject];
  if (CGRectContainsPoint(self.controller.view.frame, [touch locationInView:self])) {
    [super touchesEnded:touches withEvent:event];
  }
  else {
    [[STRootMenuView sharedInstance] touchesEnded:touches withEvent:event];
    //[self.nextResponder touchesEnded:touches withEvent:event];
  }
}

- (void)touchesMoved:(NSSet *)touches withEvent:(UIEvent *)event {
  [super touchesMoved:touches withEvent:event];
  UITouch* touch = [touches anyObject];
  if (CGRectContainsPoint(self.controller.view.frame, [touch locationInView:self])) {
  }
  else {
    [[STRootMenuView sharedInstance] touchesMoved:touches withEvent:event];
  }
}

@end
