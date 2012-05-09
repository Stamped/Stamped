//
//  STRootViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRootViewController.h"
#import "Util.h"
#import "STNavigationBar.h"
#import "ECSlidingViewController.h"
#import <QuartzCore/QuartzCore.h>

static NSString* const kLocalDataBaseURL = @"http://localhost:18000/v0";
#if defined (DEV_BUILD)
static NSString* const kDataBaseURL = @"https://dev.stamped.com/v0";
#else
static NSString* const kDataBaseURL = @"https://api.stamped.com/v0";
#endif
static NSString* const kPushNotificationPath = @"/account/alerts/ios/update.json";


@interface STRootViewController ()

@end

@implementation STRootViewController

- (void)viewDidLoad
{
  [super viewDidLoad];
  
  self.view.layer.shadowOpacity = .75;
  self.view.layer.shadowRadius = 10;
  self.view.backgroundColor = [UIColor colorWithWhite:1 alpha:1];
  [self setValue:[[[STNavigationBar alloc] initWithFrame:CGRectMake(0, 0, 320, 44)] autorelease] forKey:@"navigationBar"];
}

- (void)viewWillAppear:(BOOL)animated
{
  [super viewWillAppear:animated];
  [self.navigationBar addGestureRecognizer:self.slidingViewController.panGesture];
  //[self.view addGestureRecognizer:self.slidingViewController.panGesture];
  [self.slidingViewController setAnchorRightRevealAmount:260.0f];
  [self.slidingViewController setAnchorLeftRevealAmount:70.0f];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  [self.navigationBar removeGestureRecognizer:self.slidingViewController.panGesture];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
