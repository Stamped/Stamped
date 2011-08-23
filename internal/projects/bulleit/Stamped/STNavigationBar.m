//
//  STNavigationBar.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STNavigationBar.h"

#import <QuartzCore/QuartzCore.h>

NSString* const kMapViewButtonPressedNotification = @"kMapViewButtonPressedNotification";
NSString* const kListViewButtonPressedNotification = @"kListViewButtonPressedNotification";

@interface STNavigationBar ()
- (void)initialize;
- (void)auxiliaryButtonTapped;
@end

@implementation STNavigationBar

@synthesize hideLogo = hideLogo_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self)
    [self initialize];
  
  return self;
}

// Loaded from a nib.
- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self)
    [self initialize];
  
  return self;
}

- (void)drawRect:(CGRect)rect {
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSetFillColorWithColor(ctx, [UIColor blackColor].CGColor);
  CGContextFillRect(ctx, rect);
  if (hideLogo_)
    [[UIImage imageNamed:@"nav_bar_no_logo"] drawInRect:rect];
  else
    [[UIImage imageNamed:@"nav_bar"] drawInRect:rect];
}

- (void)initialize {
  self.layer.masksToBounds = NO;

  CGFloat ripplesY = CGRectGetMaxY(self.bounds);
  CALayer* ripplesLayer = [[CALayer alloc] init];
  ripplesLayer.frame = CGRectMake(0, ripplesY, 320, 3);
  ripplesLayer.contentsGravity = kCAGravityResizeAspect;
  ripplesLayer.contents = (id)[UIImage imageNamed:@"nav_bar_ripple"].CGImage;
  [self.layer addSublayer:ripplesLayer];
  [ripplesLayer release];

  mapLayer_ = [[CALayer alloc] init];
  mapLayer_.frame = CGRectMake(281, 7, 34, 30);
  mapLayer_.contentsGravity = kCAGravityResizeAspect;
  mapLayer_.contents = (id)[UIImage imageNamed:@"globe_button"].CGImage;
  mapLayer_.backgroundColor = [UIColor whiteColor].CGColor;
  mapLayer_.opacity = 0.0;
  [self.layer addSublayer:mapLayer_];
  [mapLayer_ release];
}

- (void)setButtonShown:(BOOL)shown {
  if (buttonShown_ == shown)
    return;

  buttonShown_ = shown;
  [UIView animateWithDuration:0.2
                   animations:^{ mapLayer_.opacity = shown ? 1.0 : 0.0; }];
}

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
  [super touchesBegan:touches withEvent:event];

  UITouch* touch = [touches anyObject];
  if (CGRectContainsPoint(mapLayer_.frame, [touch locationInView:self]))
    potentialButtonTap_ = YES;
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {
  [super touchesCancelled:touches withEvent:event];

  potentialButtonTap_ = NO;
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
  [super touchesEnded:touches withEvent:event];

  UITouch* touch = [touches anyObject];
  if (!potentialButtonTap_ || !buttonShown_)
    return;

  if (CGRectContainsPoint(mapLayer_.frame, [touch locationInView:self]))
    [self auxiliaryButtonTapped];
}

- (void)auxiliaryButtonTapped {
  if (listButtonShown_) {
    mapLayer_.contents = (id)[UIImage imageNamed:@"globe_button"].CGImage;
    [[NSNotificationCenter defaultCenter] postNotificationName:kListViewButtonPressedNotification
                                                        object:self];
  } else {
    mapLayer_.contents = (id)[UIImage imageNamed:@"list_button"].CGImage;
    [[NSNotificationCenter defaultCenter] postNotificationName:kMapViewButtonPressedNotification
                                                        object:self];
  }
  listButtonShown_ = !listButtonShown_;
}

- (void)dealloc {
  mapLayer_ = nil;
  [super dealloc];
}

@end
