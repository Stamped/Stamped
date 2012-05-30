//
//  STPageControl.m
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 __MyCompanyName__. All rights reserved.
//

#import "STPageControl.h"

@interface STPageControl ()
- (void)commonInit;
- (void)reconfigure;
@end

@implementation STPageControl

@synthesize currentPage = currentPage_;
@synthesize hidesForSinglePage = hidesForSinglePage_;
@synthesize numberOfPages = numberOfPages_;
@synthesize spacing = spacing_;
@synthesize radius = radius_;
@synthesize selectedColor = selectedColor_;
@synthesize defaultColor = defaultColor_;

#pragma mark - Private Methods.

- (void)reconfigure {
  [self setNeedsDisplay];
}

- (void)commonInit {
  self.currentPage = 0;
  self.numberOfPages = 1;
  self.hidesForSinglePage = NO;
  self.selectedColor = [UIColor colorWithWhite:0.35 alpha:1.0];
  self.defaultColor = [UIColor colorWithWhite:0.75 alpha:1.0];
  self.radius = 1.5;
  self.spacing = 6;
  self.backgroundColor = [UIColor clearColor];
    self.contentMode = UIViewContentModeRedraw;
}

#pragma mark - Public Methods.

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    [self commonInit];
  }
  return self;
}

- (id)initWithCoder:(NSCoder*)aDecoder {
  self = [super initWithCoder:aDecoder];
  if (self) {
    [self commonInit];
  }
  return self;
}

- (void)dealloc {
  self.selectedColor = nil;
  self.defaultColor = nil;
  [super dealloc];
}

- (void)setNumberOfPages:(NSInteger)numberOfPages {
  numberOfPages_ = numberOfPages;
  [self reconfigure];
}

- (void)setSpacing:(CGFloat)spacing {
  spacing_ = spacing;
  [self reconfigure];
}

- (void)setRadius:(CGFloat)radius {
  radius_ = radius;
  [self reconfigure];
}

- (void)setHidesForSinglePage:(BOOL)hidesForSinglePage {
  hidesForSinglePage_ = hidesForSinglePage;
  [self reconfigure];
}

- (void)setSelectedColor:(UIColor*)selectedColor {
  if (selectedColor_) {
    [selectedColor_ release];
  }
  selectedColor_ = [selectedColor retain];
  [self setNeedsDisplay];
}

- (void)setDefaultColor:(UIColor*)defaultColor {
  if (defaultColor_) {
    [defaultColor_ release];
  }
  defaultColor_ = [defaultColor retain];
  [self setNeedsDisplay];
}

- (void)setCurrentPage:(NSInteger)currentPage {
    currentPage_ = currentPage;
    [self setNeedsDisplay];
}

- (void)drawRect:(CGRect)rect {
  // Fetch non-atomic state for basic-consistency even if volatile.
  NSInteger pages = numberOfPages_;
  NSInteger current = currentPage_;
  CGFloat spacing = spacing_;
  CGFloat radius = radius_;
  CGColorRef selectedColor = selectedColor_.CGColor;
  CGColorRef defaultColor = defaultColor_.CGColor;
  
  // Check for invalid or hidden states.
  if (pages <= 0)
    return;
  if (hidesForSinglePage_ && pages == 1)
    return;
  if (current >= pages || current < 0)
    return;
  if (radius <= 0)
    return;
  if (spacing <= 0)
    return;
  
  CGFloat firstOffset = -( spacing * ( ( pages - 1 ) / 2.0 ) ); 
  CGRect dotFrame = CGRectMake(CGRectGetMidX(self.bounds) + firstOffset - radius, CGRectGetMidY(self.bounds)-radius, 2*radius, 2*radius);
  
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  for (NSUInteger i = 0; i < pages; ++i) {
    if (i == current && self.enabled) {
      CGContextSetFillColorWithColor(ctx, selectedColor);
    } else {
      CGContextSetFillColorWithColor(ctx, defaultColor);
    }
    CGFloat offset = i * spacing;
    CGContextFillEllipseInRect(ctx, CGRectOffset(dotFrame, offset, 0));
  }
}

- (CGSize)sizeForNumberOfPages:(NSInteger)pageCount {
  // Fetch non-atomic state for basic-consistency even if volatile.
  NSInteger pages = pageCount;
  CGFloat radius = radius_;
  CGFloat spacing = spacing_;
  
  if (pages == 0)
    return CGSizeMake(0, 0);
  
  // Return bounding box padded with one radius on each side.
  return CGSizeMake((spacing*pages)+(radius*4), radius*4);
}

@end
