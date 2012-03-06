//
//  STPageControl.m
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 __MyCompanyName__. All rights reserved.
//

#import "STPageControl.h"

@implementation STPageControl

@synthesize currentPage = currentPage_;
@synthesize defersCurrentPageDisplay = defersCurrentPageDisplay_;
@synthesize hidesForSinglePage = hidesForSinglePage_;
@synthesize numberOfPages = numberOfPages_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.backgroundColor = [UIColor clearColor];
  }
  return self;
}


- (void)drawRect:(CGRect)rect {
  if (numberOfPages_ == 0)
    return;
  
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGRect dotFrame = CGRectMake(CGRectGetMidX(self.bounds), CGRectGetMidY(self.bounds), 3, 3);
  NSInteger n = -1;
  CGColorRef selectedColor = [UIColor colorWithWhite:0.35 alpha:1.0].CGColor;
  CGColorRef defaultColor = [UIColor colorWithWhite:0.75 alpha:1.0].CGColor;
  for (NSUInteger i = 0; i < numberOfPages_; ++i) {
    /*
    NSInteger offset = i > 0 ? 6 * (-1 * n) : 0;
    offset += (numDots_ % 2) == 0 ? 3 : 0;
    NSInteger pageNum = 1;
    if (numDots_ == 2) {
      pageNum = offset < 0 ? 1 : 2;
    } else if (numDots_ == 3) {
      pageNum = offset > 0 ? 3 : offset == 0 ? 2 : 1;
    }
    if (enabled_ && pageNum == selectedPage_) {
      CGContextSetFillColorWithColor(ctx, selectedColor);
    } else {
      CGContextSetFillColorWithColor(ctx, defaultColor);
    }
    CGContextFillEllipseInRect(ctx, CGRectOffset(dotFrame, offset, 0));
    n *= -1;
     */
  }
}

- (CGSize)  sizeForNumberOfPages:(NSInteger)pageCount {
  return CGSizeMake(20, 20);
}

- (void)    updateCurrentPageDisplay{
  
}


@end
