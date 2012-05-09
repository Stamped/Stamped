//
//  STToolbarButton.m
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STToolbarButton.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"

@interface STToolbarButton ()

@property (nonatomic, readonly, retain) UIImageView* imageView;
@property (nonatomic, readonly, copy) UIView* onTextView;
@property (nonatomic, readonly, copy) UIView* offTextView;
@property (nonatomic, readwrite, assign) id target;
@property (nonatomic, readwrite, assign) SEL selector;
@property (nonatomic, readwrite, assign) BOOL touched;

- (void)updateLook;

@end

@implementation STToolbarButton

@synthesize imageView = _imageView;
@synthesize onTextView = _onTextView;
@synthesize offTextView = _offTextView;
@synthesize target = _target;
@synthesize selector = _selector;
@synthesize touched = _touched;

@synthesize on = _on;
@synthesize normalOffImage = _normalOffImage;
@synthesize normalOnImage = _normalOnImage;
@synthesize touchedOffImage = _touchedOffImage;
@synthesize touchedOnImage = _touchedOnImage;

- (id)initWithNormalOffImage:(UIImage*)normalOffImage offText:(NSString*)offText andOnText:(NSString*)onText
{
  CGRect imageFrame = CGRectMake(0, 0, 52, 56);
  self = [super initWithFrame:imageFrame];
  if (self) {
    _normalOffImage = [normalOffImage retain];
    //self.backgroundColor = [UIColor redColor];
    _imageView = [[UIImageView alloc] initWithImage:normalOffImage];
    _imageView.frame = [Util centeredAndBounded:_imageView.frame.size inFrame:imageFrame];
    [self addSubview:_imageView];
    /*

    UIFont* font = [UIFont stampedBoldFontWithSize:14];
    UIColor* color = [UIColor stampedGrayColor];  
     CGRect textFrame = CGRectMake(0, 33, 52, 25);
    _offTextView = [[Util viewWithText:offText font:font color:color mode:UILineBreakModeClip andMaxSize:textFrame.size] retain];
    _onTextView = [[Util viewWithText:onText font:font color:color mode:UILineBreakModeClip andMaxSize:textFrame.size] retain];
    _onTextView.hidden = YES;
    _offTextView.frame = [Util centeredAndBounded:_offTextView.frame.size inFrame:textFrame];
    _onTextView.frame = [Util centeredAndBounded:_onTextView.frame.size inFrame:textFrame];
    [self addSubview:_offTextView];
    [self addSubview:_onTextView];
     */
    [self setTarget:self withSelector:@selector(defaultHandler:)];
  }
  return self;
}

- (void)dealloc
{
  [_imageView release];
  [_onTextView release];
  [_offTextView release];
  [_normalOffImage release];
  [_normalOnImage release];
  [_touchedOnImage release];
  [_touchedOffImage release];
  [super dealloc];
}

- (void)setTarget:(id)target withSelector:(SEL)selector {
  self.target = target;
  self.selector = selector;
}


- (void)updateLook {
  //self.onTextView.hidden = !self.on;
 // self.offTextView.hidden = self.on;
  if (self.on) {
    if (self.touched) {
      self.imageView.image = self.touchedOnImage;
    }
    else {
      self.imageView.image = self.normalOnImage;
    }
  }
  else {
    if (self.touched) {
      self.imageView.image = self.touchedOffImage;
    }
    else {
      self.imageView.image = self.normalOffImage;
    }
  }
  [self setNeedsDisplay];
}

- (void)setOn:(BOOL)on {
  _on = on;
  [self updateLook];
}

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
  self.touched = YES;
  [self updateLook];
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {  
  self.touched = YES;
  [self updateLook];
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
  self.touched = NO;
  [self updateLook];
  //TODO fix for cancellation
  //UITouch* touch = [touches anyObject];
  //if (CGRectContainsPoint(self.frame, [touch locationInView:self])) {
  [self.target performSelector:self.selector withObject:self];
  //}
}

- (void)touchesMoved:(NSSet*)touches withEvent:(UIEvent*)event {}

- (void)defaultHandler:(id)myself {
  //override in subclass
}

@end
