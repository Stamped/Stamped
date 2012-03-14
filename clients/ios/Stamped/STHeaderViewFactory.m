//
//  STHeaderViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STHeaderViewFactory.h"
#import "Util.h"
#import <QuartzCore/QuartzCore.h>
#import <CoreText/CoreText.h>
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"

@interface STHeaderViewFactory ()

@end

@implementation STHeaderViewFactory

- (void)createWithEntityDetail:(id<STEntityDetail>)entity
                      delegate:(id<STViewDelegate>)delegate
                     withLabel:(id)label {
  UIView* view = nil;
  if (entity) {
    CGFloat padding_h = 15;
    CGFloat maxWidth = 200;
    CGFloat maxImageWidth = 320 - (maxWidth + 3 * padding_h);
    UIView* imageView = [Util imageViewWithURL:[NSURL URLWithString:entity.image] andFrame:CGRectNull];
    CGRect imageFrame = imageView.frame;
    if (imageFrame.size.width > maxImageWidth) {
      CGFloat factor = maxImageWidth / imageFrame.size.width;
      imageFrame.size.width = maxImageWidth;
      imageFrame.size.height *= factor;
    }
    
    CGFloat padding = 10;
    CGFloat paddingBetween = 5;
    UIFont* titleFont = [UIFont stampedBoldFontWithSize:20];
    UIFont* captionFont = [UIFont stampedFontWithSize:12];
    
    UIView* titleView = [Util viewWithText:entity.title
                                      font:titleFont
                                     color:[UIColor stampedDarkGrayColor]
                                      mode:UILineBreakModeWordWrap
                                andMaxSize:CGSizeMake(maxWidth, CGFLOAT_MAX)];
    
    UIView* captionView = [Util viewWithText:entity.caption
                                        font:captionFont
                                       color:[UIColor stampedGrayColor]
                                        mode:UILineBreakModeWordWrap
                                  andMaxSize:CGSizeMake(maxWidth, CGFLOAT_MAX)];
    CGFloat combinedHeight = titleView.frame.size.height + paddingBetween + captionView.frame.size.height;
    CGFloat height = combinedHeight;
    if (imageFrame.size.height > combinedHeight) {
      height = imageFrame.size.height;
    }
    
    CGFloat offset = (height - combinedHeight) / 2 + padding;
    
    
    CGRect titleFrame = titleView.frame;
    titleFrame.origin = CGPointMake(padding_h, offset);
    titleView.frame = titleFrame;
    CGRect captionFrame = captionView.frame;
    captionFrame.origin = CGPointMake(padding_h, CGRectGetMaxY(titleFrame) + paddingBetween);
    captionView.frame = captionFrame;
    
    CGFloat imageOffset = (height - imageFrame.size.height) / 2 + padding;
    imageFrame.origin = CGPointMake(320 - (imageFrame.size.width + padding_h), imageOffset);
    imageView.frame = imageFrame;
    
    imageView.layer.shadowColor = [UIColor blackColor].CGColor;
    imageView.layer.shadowOpacity = .2;
    imageView.layer.shadowRadius = 2.0;
    imageView.layer.shadowOffset = CGSizeMake(0, 2);
    
    CGRect frame = CGRectMake(0, 0, 320, 0);
    frame.size.height = height + 2 * padding;
    view = [[UIView alloc] initWithFrame:frame];
    view.backgroundColor = [UIColor clearColor];
    [view addSubview:titleView];
    [view addSubview:captionView];
    [view addSubview:imageView];
    
    [view autorelease];
  }
  [delegate didLoad:view withLabel:label];
}

@end
