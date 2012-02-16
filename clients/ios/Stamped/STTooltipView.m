//
//  STTooltipView.m
//  Stamped
//
//  Created by Andrew Bonventre on 2/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTooltipView.h"

#import <QuartzCore/QuartzCore.h>

static const CGFloat kCornerRadius = 4.0;
static const CGFloat kTriangleHeight = 6.0;
static const CGFloat kTriangleWidth = 12.0;

@interface STTooltipView ()

- (UIBezierPath*)pathForRect:(CGRect)rect;
- (void)updatePath;

@property (nonatomic, retain) CAShapeLayer* shapeLayer;
@property (nonatomic, retain) CAShapeLayer* borderShapeLayer;
@end

@implementation STTooltipView

@synthesize textLabel = textLabel_;
@synthesize shapeLayer = shapeLayer_;
@synthesize borderShapeLayer = borderShapeLayer_;

- (id)initWithText:(NSString*)text {
  self = [super initWithFrame:CGRectZero];
  if (self) {
    self.layer.shadowOpacity = 0.4;
    self.layer.shadowRadius = 2.0;
    self.layer.shadowOffset = CGSizeMake(0, 2.0);
    self.backgroundColor = [UIColor clearColor];
    
    self.borderShapeLayer = [CAShapeLayer layer];
    CAGradientLayer* borderGradientLayer = [CAGradientLayer layer];
    borderGradientLayer.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.35 alpha:1.0].CGColor,
                                  (id)[UIColor colorWithWhite:0.15 alpha:1.0].CGColor, nil];
    borderGradientLayer.mask = borderShapeLayer_;
    [self.layer addSublayer:borderGradientLayer];
    
    self.shapeLayer = [CAShapeLayer layer];
    CAGradientLayer* gradientLayer = [CAGradientLayer layer];
    gradientLayer.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithWhite:0.35 alpha:0.95].CGColor,
                            (id)[UIColor colorWithWhite:0.15 alpha:0.95].CGColor, nil];
    gradientLayer.mask = shapeLayer_;
    [self.layer addSublayer:gradientLayer];

    textLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    textLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:11];
    textLabel_.backgroundColor = [UIColor clearColor];
    textLabel_.textColor = [UIColor whiteColor];
    textLabel_.shadowColor = [UIColor colorWithWhite:0 alpha:0.4];
    textLabel_.shadowOffset = CGSizeMake(0, -1);
    textLabel_.text = text;
    [textLabel_ sizeToFit];
    [self addSubview:textLabel_];
    [textLabel_ release];
    [self sizeToFit];
    gradientLayer.frame = CGRectMake(0, 0, 320, CGRectGetHeight(self.bounds));
    borderGradientLayer.frame = CGRectMake(0, 0, 320, CGRectGetHeight(self.bounds) + 1);
    [self updatePath];
  }
  return self;
}

- (void)dealloc {
  textLabel_ = nil;
  self.shapeLayer = nil;
  self.borderShapeLayer = nil;
  [super dealloc];
}

- (void)layoutSubviews {
  [super layoutSubviews];
  [textLabel_ sizeToFit];
  textLabel_.center = CGPointMake(CGRectGetMidX(self.bounds), CGRectGetMidY(self.bounds) - (kTriangleHeight / 2));
}

- (CGSize)sizeThatFits:(CGSize)size {
  return CGSizeMake(CGRectGetWidth(textLabel_.bounds) + 22, 32 + kTriangleHeight);
}

- (void)updatePath {
  CGRect rect = CGRectOffset(CGRectInset(self.bounds, 0, kTriangleHeight / 2), 0, -(kTriangleHeight / 2));
  shapeLayer_.path = [self pathForRect:CGRectInset(rect, 1, 1)].CGPath;
  UIGraphicsBeginImageContextWithOptions(self.bounds.size, YES, 0.0);
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  if (!ctx)
    return;
  CGContextAddPath(ctx, shapeLayer_.path);
  CGContextSetLineWidth(ctx, 1);
  CGContextReplacePathWithStrokedPath(ctx);
  CGPathRef strokePath = CGContextCopyPath(ctx);
  UIGraphicsEndImageContext();
  borderShapeLayer_.path = strokePath;
}

- (UIBezierPath*)pathForRect:(CGRect)rect {
  UIBezierPath* path = [UIBezierPath bezierPath];
  [path moveToPoint:CGPointMake(CGRectGetMidX(rect), CGRectGetMaxY(self.bounds))];
  [path addLineToPoint:CGPointMake(CGRectGetMidX(rect) - (kTriangleWidth / 2), CGRectGetMaxY(rect))];
  [path addLineToPoint:CGPointMake(CGRectGetMinX(rect) + kCornerRadius, CGRectGetMaxY(rect))];
  [path addArcWithCenter:CGPointMake(CGRectGetMinX(rect) + kCornerRadius, CGRectGetMaxY(rect) - kCornerRadius)
                  radius:kCornerRadius
              startAngle:M_PI_2
                endAngle:M_PI
               clockwise:YES];
  [path addLineToPoint:CGPointMake(CGRectGetMinX(rect), CGRectGetMinY(rect) + kCornerRadius)];
  [path addArcWithCenter:CGPointMake(CGRectGetMinX(rect) + kCornerRadius, CGRectGetMinY(rect) + kCornerRadius)
                  radius:kCornerRadius
              startAngle:M_PI
                endAngle:-M_PI_2
               clockwise:YES];
  [path addLineToPoint:CGPointMake(CGRectGetMaxX(rect) - kCornerRadius, CGRectGetMinY(rect))];
  [path addArcWithCenter:CGPointMake(CGRectGetMaxX(rect) - kCornerRadius, CGRectGetMinY(rect) + kCornerRadius)
                  radius:kCornerRadius
              startAngle:-M_PI_2
                endAngle:0
               clockwise:YES];
  [path addLineToPoint:CGPointMake(CGRectGetMaxX(rect), CGRectGetMaxY(rect) - kCornerRadius)];
  [path addArcWithCenter:CGPointMake(CGRectGetMaxX(rect) - kCornerRadius, CGRectGetMaxY(rect) - kCornerRadius)
                  radius:kCornerRadius
              startAngle:0
                endAngle:M_PI_2
               clockwise:YES];
  [path addLineToPoint:CGPointMake(CGRectGetMidX(rect) + (kTriangleWidth / 2), CGRectGetMaxY(rect))];
  [path closePath];
  return path;
}

- (void)setText:(NSString*)text animated:(BOOL)animated {
  if ([textLabel_.text isEqualToString:text])
    return;

  textLabel_.text = text;
  [self setNeedsLayout];
  [self layoutIfNeeded];
  if (!animated) {
    CGFloat oldWidth = CGRectGetWidth(self.bounds);
    [self sizeToFit];
    CGRect frame = self.frame;
    frame.origin.x -= (CGRectGetWidth(self.bounds) - oldWidth) / 2;
    self.frame = frame;
    [self updatePath];
    [self setNeedsDisplay];
    return;
  }
  self.layer.shadowPath = nil;
  
  CABasicAnimation* animation = [CABasicAnimation animationWithKeyPath:@"path"];
  animation.duration = 0.3;
  animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
  CABasicAnimation* borderAnimation = [CABasicAnimation animationWithKeyPath:@"path"];
  borderAnimation.duration = 0.3;
  borderAnimation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
  animation.fromValue = [(id)(shapeLayer_.presentationLayer) path];
  borderAnimation.fromValue = [(id)borderShapeLayer_.presentationLayer path];
  CGFloat oldWidth = CGRectGetWidth(self.bounds);
  [self sizeToFit];
  [self updatePath];
  animation.toValue = (id)shapeLayer_.path;
  borderAnimation.toValue = (id)borderShapeLayer_.path;
  [shapeLayer_ addAnimation:animation forKey:@"animatePath"];
  [borderShapeLayer_ addAnimation:borderAnimation forKey:@"animatePath"];
  CGRect frame = self.frame;
  frame.origin.x -= (CGRectGetWidth(self.bounds) - oldWidth) / 2;
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowAnimatedContent | UIViewAnimationOptionAllowUserInteraction
                   animations:^{ self.frame = frame; }
                   completion:nil];
}

@end
