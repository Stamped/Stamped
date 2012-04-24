//
//  STRootMenuView.m
//  Stamped
//
//  Created by Landon Judkins on 4/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRootMenuView.h"
#import "Util.h"
#import <QuartzCore/QuartzCore.h>
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STInboxViewController.h"
#import "SettingsViewController.h"
#import "STUniversalNewsController.h"
#import "STTodoViewController.h"
#import "STDebugViewController.h"
#import "ECSlidingViewController.h"
#import "STRootViewController.h"

@interface STRootMenuView ()

@end

@interface STRootMenuViewBar : UIView

@end

@implementation STRootMenuViewBar

- (id)init {
  self = [super initWithFrame:CGRectMake(0, 0, 320, 2)];
  if (self) {
    CAGradientLayer* gradient = [CAGradientLayer layer];
    gradient.anchorPoint = CGPointMake(0, 0);
    gradient.position = CGPointMake(0, 0);
    gradient.bounds = self.layer.bounds;
    gradient.cornerRadius = 2.0;
    gradient.colors = [NSMutableArray arrayWithObjects:
                       (id)[UIColor colorWithWhite:.2 alpha:.4].CGColor,
                       (id)[UIColor colorWithWhite:.7 alpha:.7].CGColor,
                       nil];
    [self.layer addSublayer:gradient];
  }
  return self;
}

@end

@interface STARootMenuViewCell : UIView

- (id)initWithTitle:(NSString*)title;

- (void)clicked:(id)message;

@property (nonatomic, readonly, assign) BOOL selected;

@end

@implementation STARootMenuViewCell

- (id)initWithTitle:(NSString*)title {
  self = [super initWithFrame:CGRectMake(0, 0, 250, 50)];
  if (self) {
    UIView* titleView = [Util viewWithText:title 
                                      font:[UIFont stampedBoldFontWithSize:20] 
                                     color:[UIColor stampedLightGrayColor]
                                      mode:UILineBreakModeClip
                                andMaxSize:CGSizeMake(320, 50)];
    CGRect titleFrame = [Util centeredAndBounded:titleView.frame.size inFrame:self.frame];
    titleFrame.origin.x = 20;
    titleView.frame = titleFrame;
    [self addSubview:titleView];
    UIView* buttonView = [Util tapViewWithFrame:self.frame target:self selector:@selector(clicked:) andMessage:nil];
    [self addSubview:buttonView];
  }
  return self;
}

- (void)clicked:(id)message {
}

- (BOOL)selected {
  return NO;
}

@end

@interface STRootMenuViewCell : STARootMenuViewCell

- (id)initWithTitle:(NSString*)title andController:(UIViewController*)controller;


@property (nonatomic, readonly, retain) UIViewController* controller;

@end

@implementation STRootMenuViewCell

@synthesize controller = _controller;

- (id)initWithTitle:(NSString*)title andController:(UIViewController*)controller {
  self = [super initWithTitle:title];
  if (self) {
    _controller = [controller retain];
  }
  return self;
}

- (void)clicked:(id)message {
  /*
  if (!self.selected) {
    UINavigationController* sharedController = [Util sharedNavigationController];
    [UIView animateWithDuration:.35 animations:^{
      UIView* view = [Util sharedNavigationController].view;
      [Util reframeView:view withDeltas:CGRectMake(100, 0, 0, 0)];
    } completion:^(BOOL finished) {
      [sharedController setViewControllers:[NSArray arrayWithObject:self.controller] animated:NO];
      [[STRootMenuView sharedInstance] toggle];
    }];
  }
  else {
    [[STRootMenuView sharedInstance] toggle];
  }
   */
  NSLog(@"testing");
  ECSlidingViewController* slider = [ECSlidingViewController sharedInstance];
  [slider anchorTopViewOffScreenTo:ECRight animations:nil onComplete:^{
    [[Util sharedNavigationController] setViewControllers:[NSArray arrayWithObject:self.controller] animated:NO];
    [slider resetTopView];
  }];
}

- (BOOL)selected {
  UINavigationController* sharedController = [Util sharedNavigationController];
  return sharedController.topViewController == self.controller;
}

@end

@interface STRootMenuViewSettingsCell : STRootMenuViewCell

@end

@implementation STRootMenuViewSettingsCell

- (void)clicked:(id)message {
  UINavigationController* controller = [Util sharedNavigationController];
  [controller pushViewController:[[[SettingsViewController alloc] initWithNibName:@"SettingsViewController" bundle:nil] autorelease]
                                animated:YES];
}

@end

@implementation STRootMenuView

static STRootMenuView* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STRootMenuView alloc] init];
}

+ (STRootMenuView*)sharedInstance {
  return _sharedInstance;
}

- (id)init
{
  self = [super initWithFrame:CGRectMake(0, 0, 320, 30)];
  if (self) {
    self.backgroundColor = [UIColor clearColor];
    UIView* stampedLabel = [Util viewWithText:@"STAMPED" 
                                         font:[UIFont stampedTitleFontWithSize:30] 
                                        color:[UIColor colorWithWhite:0 alpha:.5]
                                         mode:UILineBreakModeClip 
                                   andMaxSize:CGSizeMake(320, CGFLOAT_MAX)];
    stampedLabel.frame = CGRectMake(20, 0, 320, 50);
    [self appendChildView:stampedLabel];
    NSDictionary* navigators = [NSDictionary dictionaryWithObjectsAndKeys:
                                [STInboxViewController sharedInstance], @"Stamps",
                                [[[STUniversalNewsController alloc] init] autorelease], @"News",
                                [STTodoViewController sharedInstance], @"To-Do",
                                [[[STDebugViewController alloc] init] autorelease], @"Debug",
                                //[[[TodoViewController alloc] initWithNibName:@"TodoViewController" bundle:nil] autorelease], @"To-Do",
                                //[[[PeopleViewController alloc] initWithNibName:@"PeopleViewController" bundle:nil] autorelease], @"People",
                                [[[SettingsViewController alloc] initWithNibName:@"SettingsViewController" bundle:nil] autorelease], @"Settings",
                                nil];
    NSArray* navigatorOrder = [NSArray arrayWithObjects:@"Stamps", @"News", @"To-Do", @"Debug", @"Settings", nil];
    for (NSString* key in navigatorOrder) {
      UIViewController* controller = [navigators objectForKey:key];
      [self appendChildView:[[[STRootMenuViewBar alloc] init] autorelease]];
      [self appendChildView:[[[STRootMenuViewCell alloc] initWithTitle:key andController:controller] autorelease]];
    }
    [self appendChildView:[[[STRootMenuViewBar alloc] init] autorelease]];
    CGRect frame = self.frame;
    //TODO actual height
    frame.size.height = 500;
    self.frame = frame;
    
  }
  return self;
}

- (void)toggle {
  [UIView animateWithDuration:.35 animations:^{
    //for (UIView* view in [UIApplication sharedApplication].keyWindow.subviews) {
    UIView* view = [Util sharedNavigationController].view;
    CGFloat delta = 250;
    if (view.frame.origin.x > 0) {
      view.userInteractionEnabled = YES;
      delta = -view.frame.origin.x;
    }
    else {
      view.userInteractionEnabled = NO;
    }
    [Util reframeView:view withDeltas:CGRectMake(delta, 0, 0, 0)];
    //}
  }];
}

@end
