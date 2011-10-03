//
//  NotificationSettingsViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/2/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "NotificationSettingsViewController.h"

@implementation NotificationSettingsViewController

@synthesize scrollView = scrollView_;

- (id)init {
  self = [self initWithNibName:@"NotificationSettingsViewController" bundle:nil];
  if (self) {
    
  }
  return self;
}

- (void)dealloc {
  self.scrollView = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  UIView* lastView = scrollView_.subviews.lastObject;
  scrollView_.contentSize = CGSizeMake(320, CGRectGetMaxY(lastView.frame));
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.scrollView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Actions

- (IBAction)settingsButtomPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

@end
