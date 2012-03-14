//
//  STMetadataViewFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMetadataViewFactory.h"
#import "STViewContainer.h"
#import "Util.h"
#import <QuartzCore/QuartzCore.h>
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"

@interface MetadatumView : UIView

- (id)initWithDatum:(id<STMetadataItem>)datum;

@end

@implementation MetadatumView

- (id)initWithDatum:(id<STMetadataItem>)datum {
  self = [super init];
  if (self) {
    CGFloat maxWidth = 262;
    
    UIView* valueView = [Util viewWithText:datum.value
                                      font:[UIFont stampedFontWithSize:12]
                                     color:[UIColor stampedGrayColor]
                                      mode:UILineBreakModeWordWrap 
                                andMaxSize:CGSizeMake(maxWidth, CGFLOAT_MAX)];
    
    UIView* nameView = [Util viewWithText:datum.name
                                     font:[UIFont stampedBoldFontWithSize:12]
                                    color:[UIColor stampedDarkGrayColor]
                                     mode:UILineBreakModeTailTruncation
                               andMaxSize:CGSizeMake(maxWidth, CGFLOAT_MAX)];
    CGFloat minSpacing = 10;
    
    nameView.frame = CGRectOffset(nameView.frame, 14, 14);
    if (nameView.frame.size.width + valueView.frame.size.width > maxWidth - minSpacing) {
      valueView.frame = CGRectOffset(valueView.frame, 14 , 14 + CGRectGetMaxY(nameView.frame));
    }
    else {
      valueView.frame = CGRectOffset(valueView.frame, 290 - (valueView.frame.size.width + 14 ) , 14);
    }
    
    CGRect frame = CGRectMake(0, 0, 290, CGRectGetMaxY(valueView.frame)+14);
    self.frame = frame;
    self.backgroundColor = [UIColor clearColor];
    
    
    CAGradientLayer* gradient = [CAGradientLayer layer];
    gradient.anchorPoint = CGPointMake(0, 0);
    gradient.position = CGPointMake(0, 0);
    gradient.bounds = self.layer.bounds;
    gradient.cornerRadius = 2.0;
    gradient.colors = [NSMutableArray arrayWithObjects:
                       (id)[UIColor colorWithRed:1.0 green:1.0 blue:1.0 alpha:.8].CGColor,
                       (id)[UIColor colorWithRed:.95 green:.95 blue:.95 alpha:.6].CGColor,
                       nil];
    [self.layer addSublayer:gradient];
    
    [self addSubview:nameView];
    [self addSubview:valueView];
  }
  return self;
}

@end

@implementation STMetadataViewFactory

- (void)createWithEntityDetail:(id<STEntityDetail>)entity
                      delegate:(id<STViewDelegate>)delegate
                     withLabel:(id)label {
  STViewContainer* main = nil;
  if (entity && entity.metadata && [entity.metadata count] > 0) {
    main = [[STViewContainer alloc] initWithFrame:CGRectMake(0, 0, 320, 10)];
    main.delegate = delegate;
    STViewContainer* view = [[STViewContainer alloc] initWithFrame:CGRectMake(15, 0, 290, 0)];
    view.delegate = main;
    
    UIImage* image = [UIImage imageNamed:@"eDetailBox_line"];
    for (id<STMetadataItem> datum in entity.metadata) {
      UIView* item = [[MetadatumView alloc] initWithDatum:datum];
      [view appendChild:item];
      UIImageView* bar = [[UIImageView alloc] initWithImage:image];
      bar.backgroundColor = [UIColor clearColor];
      [view appendChild:bar];
      [item release];
      [bar release];
    }
    
    view.layer.cornerRadius = 2.0;
    view.layer.borderColor =[UIColor colorWithRed:.8 green:.8 blue:.8 alpha:.4].CGColor;
    view.layer.borderWidth = 1.0;
    view.layer.shadowColor = [UIColor blackColor].CGColor;
    view.layer.shadowOpacity = .05;
    view.layer.shadowRadius = 1.0;
    view.layer.shadowOffset = CGSizeMake(0, 1);
    
    [main appendChild:view];
    [view release];
    
    CGRect frame = main.frame;
    frame.size.height += 10;
    main.frame = frame;
    [main autorelease];
  }
  [delegate didLoad:main withLabel:label];
}

@end
