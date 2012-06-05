//
//  STStampDetailHeaderView.m
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailHeaderView.h"

#import <QuartzCore/QuartzCore.h>

#import <CoreText/CoreText.h>

#import "STStamp.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "STStampedActions.h"
#import "STActionManager.h"

@interface STStampDetailHeaderView ()

- (void)clicked:(id)msg;

@property (nonatomic, readonly, retain) id<STStamp> stamp;
@property (nonatomic, readonly, retain) id<STEntity> entity;

@end

@implementation STStampDetailHeaderView

@synthesize stamp = _stamp;
@synthesize entity = entity_;

- (void)commonInit {
  UIView* titleView = [Util viewWithText:self.entity.title
                                    font:[UIFont stampedTitleFont]
                                   color:[UIColor stampedDarkGrayColor] 
                                    mode:UILineBreakModeWordWrap 
                              andMaxSize:CGSizeMake(280, CGFLOAT_MAX)];
  UIView* subtitleView = [Util viewWithText:self.entity.subtitle
                                       font:[UIFont stampedSubtitleFont]
                                      color:[UIColor stampedGrayColor]
                                       mode:UILineBreakModeWordWrap 
                                 andMaxSize:CGSizeMake(280, CGFLOAT_MAX)];
  CGFloat padding = 10;
  titleView.frame = CGRectOffset(titleView.frame, padding, padding);
  [self appendChildView:titleView];
  
  UIImage* categoryImage = [Util imageForCategory:self.stamp.entity.category];
  UIImageView* categoryView = [[[UIImageView alloc] initWithImage:categoryImage] autorelease];
  CGFloat subtitleXOffset = padding + categoryView.frame.size.width + 5;
  subtitleView.frame = CGRectOffset(subtitleView.frame, subtitleXOffset, 0);
  [self appendChildView:subtitleView];
  CGRect categoryFrame = [Util centeredAndBounded:categoryView.frame.size inFrame:subtitleView.frame];
  categoryFrame.origin.x = padding;
  categoryView.frame = categoryFrame;
  [self addSubview:categoryView];
  UIImageView* arrowImage = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"gray_disclosure_arrow"]] autorelease];
  arrowImage.frame = [Util centeredAndBounded:arrowImage.frame.size inFrame:CGRectMake(280, 0, 40, self.frame.size.height)];
  [self addSubview:arrowImage];
  UIView* buttonView = [Util tapViewWithFrame:self.frame target:self selector:@selector(clicked:) andMessage:nil];
  [self addSubview:buttonView];
  [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, padding)];
}

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super initWithDelegate:nil andFrame:CGRectMake(0, 0, 320, 0)];
  if (self) {
    _stamp = [stamp retain];
    entity_ = [stamp.entity retain];
    [self commonInit];
  }
  return self;
}

- (id)initWithEntity:(id<STEntity>)entity {
  self = [super initWithDelegate:nil andFrame:CGRectMake(0, 0, 320, 0)];
  if (self) {
    entity_ = [entity retain];
    [self commonInit];
  }
  return self;
}

- (void)dealloc {
  [_stamp release];
  [entity_ release];
  [super dealloc];
}

- (void)clicked:(id)msg {
  STActionContext* context = [STActionContext context];
  id<STAction> action = [STStampedActions actionViewEntity:self.entity.entityID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

@end
