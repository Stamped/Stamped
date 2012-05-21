//
//  STIWantToViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STIWantToViewController.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import <QuartzCore/QuartzCore.h>
#import "STConsumptionViewController.h"
#import "STButton.h"
#import "ECSlidingViewController.h"
#import "STLegacyMapViewController.h"
#import "STConfiguration.h"
#import "STConsumptionMapViewController.h"

@interface STIWantToViewController ()

@end

@implementation STIWantToViewController

- (id)init {
  self = [super init];
  if (self) {
  }
  return self;
}

- (void)viewDidLoad {
  [super viewDidLoad];
  [Util addHomeButtonToController:self withBadge:YES];
  [Util addCreateStampButtonToController:self];
  CGRect scrollFrame = self.scrollView.frame;
  CGFloat sidePadding = 5;
  CGFloat topPadding = 10;
  CGFloat padding = 10;
  CGFloat cellWidth = ( scrollFrame.size.width - (2 * sidePadding + padding) ) / 2;
  CGFloat cellHeight = 125;
  NSArray* categories = [Util categories];
  for (NSInteger i = 0; i < categories.count; i++) {
    NSString* category = [categories objectAtIndex:i];
    NSInteger row = i / 2;
    NSInteger col = i % 2;
    
    UIView* views[2];
    CGRect buttonFrame = CGRectMake(0, 0, cellWidth, cellHeight);
    for (NSInteger k = 0; k < 2; k++) {
      UIView* cellView = [[[UIView alloc] initWithFrame:buttonFrame] autorelease];
      cellView.layer.cornerRadius = 5;
      cellView.layer.borderWidth = 1;
      cellView.layer.borderColor = [UIColor colorWithWhite:.8 alpha:1].CGColor;
      cellView.layer.shadowOpacity = .4;
      cellView.layer.shadowRadius = 2;
      cellView.layer.shadowOffset = CGSizeMake(0, 2);
        cellView.layer.shadowPath = [UIBezierPath bezierPathWithRect:cellView.bounds].CGPath;
      
      NSArray* colors;
      if (k == 0) {
        colors = [UIColor stampedLightGradient];
      }
      else {
        colors = [UIColor stampedDarkGradient];
      }
      [Util addGradientToLayer:cellView.layer withColors:colors vertical:YES];
      views[k] = cellView;
    }
    STButton* button = [[[STButton alloc] initWithFrame:buttonFrame 
                                             normalView:views[0] 
                                             activeView:views[1] 
                                                 target:self 
                                              andAction:@selector(buttonClicked:)] autorelease];
    button.message = category;
    NSString* imageName = [NSString stringWithFormat:@"consumption_%@", category];
    UIImageView* imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:imageName]] autorelease];
    [button addSubview:imageView];
    [Util reframeView:button withDeltas:CGRectMake(sidePadding + col * (cellWidth + padding), topPadding + row * (cellHeight + padding), 0, 0)];
    [self.scrollView addSubview:button];
  }
}

- (void)viewDidUnload {
  [super viewDidUnload];
  // Release any retained subviews of the main view.
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)buttonClicked:(NSString*)category {
  UIViewController* controller = nil;
  if (category) {
    if ([category isEqualToString:@"food"]) {
      controller = [[[STConsumptionMapViewController alloc] init] autorelease];
    }
    else {
      controller = [[[STConsumptionViewController alloc] initWithCategory:category] autorelease];
    }
  }
  if (controller) {
    [self.navigationController pushViewController:controller animated:YES];
  }
  else {
    [Util warnWithMessage:[NSString stringWithFormat:@"controller for %@ not implemented yet...", category] andBlock:nil];
  }
}

+ (void)setupConfigurations {
  [STConsumptionMapViewController setupConfigurations];
  [STConsumptionViewController setupConfigurations];
}

@end
