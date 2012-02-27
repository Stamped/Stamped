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
@property (nonatomic, retain) CATextLayer* textLayer;
@property (nonatomic, readonly) UIImageView* highlightView;
@end

@implementation STTooltipView

@synthesize textLayer = textLayer_;
@synthesize shapeLayer = shapeLayer_;
@synthesize borderShapeLayer = borderShapeLayer_;
@synthesize highlightView = highlightView_;

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

    self.textLayer = [CATextLayer layer];
    textLayer_.alignmentMode = kCAAlignmentCenter;
    textLayer_.foregroundColor = [UIColor whiteColor].CGColor;
    textLayer_.shadowOffset = CGSizeMake(0, -1);
    textLayer_.contentsScale = [UIScreen mainScreen].scale;
    CGFontRef font = CGFontCreateWithFontName((CFStringRef)@"Helvetica-Bold");
    textLayer_.font = font;
    CGFontRelease(font);
    textLayer_.fontSize = 11;
    textLayer_.string = text;
    [self.layer addSublayer:textLayer_];
    
    UIImage* highlightImage = [[UIImage imageNamed:@"popup_innerShadow"] stretchableImageWithLeftCapWidth:3 topCapHeight:0];
    highlightView_ = [[UIImageView alloc] initWithImage:highlightImage];
    [self addSubview:highlightView_];
    [highlightView_ release];

    [self sizeToFit];
    gradientLayer.frame = CGRectMake(0, 0, 320, CGRectGetHeight(self.bounds));
    borderGradientLayer.frame = CGRectMake(0, 0, 320, CGRectGetHeight(self.bounds) + 1);
    [self updatePath];
  }
  return self;
}

- (void)dealloc {
  self.shapeLayer = nil;
  self.borderShapeLayer = nil;
  self.textLayer = nil;
  highlightView_ = nil;
  [super dealloc];
}

- (void)setBounds:(CGRect)bounds {
  [super setBounds:bounds];
  highlightView_.frame = CGRectMake(2, 1.5, CGRectGetWidth(self.bounds) - 4, 3);
}

- (void)setFrame:(CGRect)frame {
  [super setFrame:frame];
  highlightView_.frame = CGRectMake(2, 1.5, CGRectGetWidth(self.bounds) - 4, 3);
}

- (CGSize)sizeThatFits:(CGSize)size {
  return CGSizeMake([(NSString*)textLayer_.string sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:11]].width + 22,
                    kTriangleHeight + 32);
}

- (void)layoutSubviews {
  [super layoutSubviews];
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
  textLayer_.frame = CGRectOffset(rect, 0, 12);
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
  if ([(NSString*)textLayer_.string isEqualToString:text])
    return;

  textLayer_.string = text;
  CGSize size = CGSizeMake([(NSString*)textLayer_.string sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:11]].width + 22,
                           kTriangleHeight + 32);
  if (!animated) {
    [self sizeToFit];
    self.bounds = CGRectMake(0, 0, size.width, size.height);
    [self updatePath];
    [self setNeedsDisplay];
    return;
  }
  self.layer.shadowPath = nil;

  CABasicAnimation* animation = [CABasicAnimation animationWithKeyPath:@"path"];
  animation.duration = 0.2;
  animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
  CABasicAnimation* borderAnimation = [CABasicAnimation animationWithKeyPath:@"path"];
  borderAnimation.duration = 0.2;
  borderAnimation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
  animation.fromValue = [(id)shapeLayer_.presentationLayer path];
  borderAnimation.fromValue = [(id)borderShapeLayer_.presentationLayer path];
  [UIView animateWithDuration:0.2
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState | UIViewAnimationOptionAllowAnimatedContent | UIViewAnimationOptionAllowUserInteraction
                   animations:^{
                     self.bounds = CGRectMake(0, 0, size.width, size.height);
                   }
                   completion:nil];  
  [self updatePath];
  animation.toValue = (id)shapeLayer_.path;
  borderAnimation.toValue = (id)borderShapeLayer_.path;
  [shapeLayer_ addAnimation:animation forKey:@"animatePath"];
  [borderShapeLayer_ addAnimation:borderAnimation forKey:@"animatePath"];
}

@end
