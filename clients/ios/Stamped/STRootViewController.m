//
//  STRootViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STRootViewController.h"
#import "Util.h"

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
  self.view.backgroundColor = [UIColor colorWithWhite:1 alpha:.5];
  [UIView animateWithDuration:1 animations:^{
    //[Util reframeView:self.view withDeltas:CGRectMake(100, 0, 0, 0)];
  } completion:^(BOOL finished) {
    [UIView animateWithDuration:1 animations:^{
      //[Util reframeView:self.view withDeltas:CGRectMake(100, 0, 0, 0)];
    }];
  }];
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
