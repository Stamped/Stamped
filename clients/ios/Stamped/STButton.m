//
//  STButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STButton.h"
#import "Util.h"

@interface STButton ()

@property (nonatomic, readonly, retain) UIView* normalView;
@property (nonatomic, readonly, retain) UIView* activeView;
@property (nonatomic, readonly, assign) id target;
@property (nonatomic, readonly, assign) SEL action;
@property (nonatomic, readonly, assign) BOOL touched;

@end

@implementation STButton

@synthesize normalView = normalView_;
@synthesize activeView = activeView_;
@synthesize target = target_;
@synthesize action = action_;
@synthesize enabled = enabled_;
@synthesize touched = touched_;

- (id)initWithFrame:(CGRect)frame 
         normalView:(UIView*)normalView 
         activeView:(UIView*)activeView 
             target:(id)target 
          andAction:(SEL)selector
{
    self = [super initWithFrame:frame];
    if (self) {
      normalView_ = [normalView retain];
      activeView_ = [activeView retain];
      target_ = target;
      action_ = selector;
      enabled_ = YES;
      [self addSubview:normalView];
      [self addSubview:activeView];
      activeView.hidden = YES;
    }
    return self;
}

- (void)dealloc
{
  [normalView_ release];
  [activeView_ release];
  [super dealloc];
}

- (void)setTouched:(BOOL)touched {
  if (touched != touched_) {
    touched_ = touched;
    if (touched_) {
      self.activeView.hidden = NO;
      self.normalView.hidden = YES;
    }
    else {
      self.normalView.hidden = NO;
      self.activeView.hidden = YES;
    }
  }
}

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
  self.touched = YES;
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {  
  self.touched = NO;
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
  self.touched = NO;
  //TODO fix for cancellation
  UITouch* touch = [touches anyObject];
  if (CGRectContainsPoint(CGRectMake(0, 0, self.frame.size.width, self.frame.size.height), [touch locationInView:self])) {
    [self.target performSelector:self.action withObject:self];
  }
}

- (void)touchesMoved:(NSSet*)touches withEvent:(UIEvent*)event {
  
}

@end
