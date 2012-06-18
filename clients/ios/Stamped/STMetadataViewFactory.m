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
#import "STViewContainer.h"

static const CGFloat _kReadMoreHeight = 78;
static const CGFloat _kReadMoreHeightCutoff = 90;

@interface MetadatumView : STViewContainer

- (id)initWithDatum:(id<STMetadataItem>)datum andDelegate:(id<STViewDelegate>)delegate;

- (void)clicked:(id)button;
- (void)actionClicked:(id<STAction>)action;

@property (nonatomic, assign) CGFloat uncollapsedValueHeight;
@property (nonatomic, retain) UIView* valueViewContainer;
@property (nonatomic, retain) CAGradientLayer* gradient;
@property (nonatomic, retain) UIView* readMore;
@property (nonatomic, retain) UIView* readLess;
@property (nonatomic, assign) BOOL collapsed;
@property (nonatomic, retain) UIView* button;
@property (nonatomic, assign) id<STViewDelegate> delegateRef;

@end

@implementation MetadatumView

@synthesize uncollapsedValueHeight = uncollapsedValueHeight_;
@synthesize valueViewContainer = valueViewContainer_;
@synthesize gradient = gradient_;
@synthesize readMore = readMore_;
@synthesize readLess = readLess_;
@synthesize collapsed = collapsed_;
@synthesize button = button_;
@synthesize delegateRef = delegateRef_;

- (id)initWithDatum:(id<STMetadataItem>)datum andDelegate:(id<STViewDelegate>)delegate {
  self = [super initWithDelegate:delegate andFrame:CGRectZero];
  if (self) {
    if (datum.action) {
      self.button = [Util tapViewWithFrame:CGRectZero target:self selector:@selector(actionClicked:) andMessage:datum.action];
      self.delegateRef = delegate;
      //self.button.backgroundColor = [UIColor redColor];
      [self addSubview:self.button];
    }
    CGFloat maxWidth = 262;
    UIColor* valueColor = [UIColor stampedGrayColor];
    if (self.button) {
      valueColor = [UIColor colorWithRed:.3 green:.3 blue:.5 alpha:1];
    }
    UIView* valueView = [Util viewWithText:datum.value
                                      font:[UIFont stampedFontWithSize:12]
                                     color:valueColor
                                      mode:UILineBreakModeWordWrap 
                                andMaxSize:CGSizeMake(maxWidth, CGFLOAT_MAX)];
    
    UIView* nameView = [Util viewWithText:datum.name
                                     font:[UIFont stampedBoldFontWithSize:12]
                                    color:[UIColor stampedDarkGrayColor]
                                     mode:UILineBreakModeTailTruncation
                               andMaxSize:CGSizeMake(maxWidth, CGFLOAT_MAX)];
    CGFloat minSpacing = 10;
    valueView.clipsToBounds = YES;
    nameView.frame = CGRectOffset(nameView.frame, 14, 14);
    self.uncollapsedValueHeight = valueView.frame.size.height;
    if (nameView.frame.size.width + valueView.frame.size.width > maxWidth - minSpacing) {
      if (valueView.frame.size.height > _kReadMoreHeightCutoff) {
        valueView.frame = CGRectMake(14, 0, valueView.frame.size.width, valueView.frame.size.height);
      }
      else {
        valueView.frame = CGRectOffset(valueView.frame, 14 , 14 + CGRectGetMaxY(nameView.frame));
      }
    }
    else {
      valueView.frame = CGRectOffset(valueView.frame, 290 - (valueView.frame.size.width + 14 ) , 14);
    }
    
    self.backgroundColor = [UIColor clearColor];
    
    self.gradient = [CAGradientLayer layer];
    //[self.layer addSublayer:self.gradient];
    [self addSubview:nameView];
    if (self.uncollapsedValueHeight > _kReadMoreHeightCutoff) {
      CGRect frame = CGRectMake(0, 0, 290, CGRectGetMaxY(nameView.frame)+14);
      CGRect valueFrame = CGRectMake(0, 0, 290, _kReadMoreHeight);
      self.valueViewContainer = [[[UIView alloc] initWithFrame:valueFrame] autorelease];
      self.valueViewContainer.clipsToBounds = YES;
      self.valueViewContainer.backgroundColor = [UIColor clearColor];
      [self.valueViewContainer addSubview:valueView];
      
      self.frame = frame;
      [self appendChildView:self.valueViewContainer];
      self.readMore = [Util viewWithText:@"read more" 
                                    font:[UIFont stampedFontWithSize:12] 
                                   color:[UIColor stampedDarkGrayColor] 
                                    mode:UILineBreakModeTailTruncation 
                              andMaxSize:CGSizeMake(290, CGFLOAT_MAX)];
      self.readLess = [Util viewWithText:@"read less" 
                                    font:[UIFont stampedFontWithSize:12] 
                                   color:[UIColor stampedDarkGrayColor] 
                                    mode:UILineBreakModeTailTruncation 
                              andMaxSize:CGSizeMake(290, CGFLOAT_MAX)];
      self.readMore.frame = CGRectOffset(self.readMore.frame, 14, 14);
      self.readLess.frame = CGRectOffset(self.readLess.frame, 14, 14);
      self.readLess.hidden = YES;
      UIView* buttonContainer = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 290, self.readLess.frame.size.height+28)] autorelease];
      UIView* button = [Util tapViewWithFrame:buttonContainer.frame target:self selector:@selector(clicked:) andMessage:nil];
      [buttonContainer addSubview:button];
      [buttonContainer addSubview:self.readMore];
      [buttonContainer addSubview:self.readLess];
      [self appendChildView:buttonContainer];
      self.collapsed = YES;
    }
    else {
      CGRect frame = CGRectMake(0, 0, 290, CGRectGetMaxY(valueView.frame)+14);
      self.frame = frame;
      [self addSubview:valueView];
    }
      
    self.gradient.contentsScale = [[UIScreen mainScreen] scale];
    self.gradient.anchorPoint = CGPointMake(0, 0);
    self.gradient.position = CGPointMake(0, 0);
    self.gradient.frame = self.layer.frame;
    self.gradient.cornerRadius = 2.0;
    self.gradient.colors = [NSMutableArray arrayWithObjects:
                            (id)[UIColor colorWithRed:1.0 green:1.0 blue:1.0 alpha:.8].CGColor,
                            (id)[UIColor colorWithRed:.95 green:.95 blue:.95 alpha:.6].CGColor,
                            nil];
    if (self.button && NO) {
      self.gradient.colors = [NSMutableArray arrayWithObjects:
                              (id)[UIColor colorWithRed:.9 green:.90 blue:1.0 alpha:.6].CGColor,
                              (id)[UIColor colorWithRed:.80 green:.80 blue:.95 alpha:.6].CGColor,
                              nil];
    }
    if (self.button) {
      self.button.frame = CGRectMake(0, 0, self.frame.size.width, self.frame.size.height);
    }
  }
  return self;
}

- (void)dealloc {
  self.gradient = nil;
  self.valueViewContainer = nil;
  self.readMore = nil;
  self.readLess = nil;
  [super dealloc];
}

- (void)clicked:(id)button {
  CGFloat delta;
  CGFloat duration = .25;
  if (self.collapsed) {
    delta = self.uncollapsedValueHeight - _kReadMoreHeight;
    self.readLess.hidden = NO;
    self.readMore.hidden = YES;
  }
  else {
    delta = _kReadMoreHeight - self.valueViewContainer.frame.size.height;
    self.readLess.hidden = YES;
    self.readMore.hidden = NO;
  }
  [self childView:self.valueViewContainer shouldChangeHeightBy:delta overDuration:duration];
  self.collapsed = !self.collapsed;
}

- (void)childView:(UIView*)view shouldChangeHeightBy:(CGFloat)delta overDuration:(CGFloat)seconds {
  [UIView animateWithDuration:seconds animations:^{
    CGRect frame = self.gradient.frame;
    frame.size.height += delta;
    self.gradient.frame = frame;
    if (self.button) {
      CGRect frame = self.button.frame;
      frame.size.height += delta;
      self.button.frame = frame;
    }
  }];
  [super childView:view shouldChangeHeightBy:delta overDuration:seconds];
}

- (void)actionClicked:(id<STAction>)action {
  [self.delegateRef didChooseAction:action withContext:[STActionContext contextInView:self]];
}

@end

@implementation STMetadataViewFactory

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)entity
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate {
  STViewContainer* main = nil;
  if (entity && entity.metadata && [entity.metadata count] > 0) {
    main = [[[STViewContainer alloc] initWithDelegate:delegate andFrame:CGRectMake(0, 0, 320, 10)] autorelease];
    STViewContainer* view = [[STViewContainer alloc] initWithDelegate:main andFrame:CGRectMake(15, 0, 290, 0)];
    
    UIImage* image = [UIImage imageNamed:@"eDetailBox_line"];
    for (NSInteger i = 0; i < [entity.metadata count]; i++) {
      id<STMetadataItem> datum = [entity.metadata objectAtIndex:i];
      UIView* item = [[MetadatumView alloc] initWithDatum:datum andDelegate:view];
      [view appendChildView:item];
      if (i + 1 != [entity.metadata count] ) {
        UIImageView* bar = [[UIImageView alloc] initWithImage:image];
        bar.backgroundColor = [UIColor clearColor];
        [view appendChildView:bar];
        [bar release];
      }
      [item release];
    }
    
    view.layer.cornerRadius = 2.0;
    view.layer.borderColor =[UIColor colorWithRed:.8 green:.8 blue:.8 alpha:.4].CGColor;
    view.layer.borderWidth = 1.0;
    view.layer.shadowColor = [UIColor blackColor].CGColor;
    view.layer.shadowOpacity = .05;
    view.layer.shadowRadius = 1.0;
    view.layer.shadowOffset = CGSizeMake(0, 1);
    
    [main appendChildView:view];
    [view release];
    
    CGRect frame = main.frame;
    frame.size.height += 10;
    main.frame = frame;
  }
  return main;
}

@end
