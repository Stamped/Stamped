//
//  SettingsViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "SettingsViewController.h"

@implementation SettingsViewController

@synthesize navigationController = navigationController_;

- (id)initWithNibName:(NSString*)nibNameOrNil bundle:(NSBundle*)nibBundleOrNil {
  self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
  if (self) {
    // Custom initialization
  }
  return self;
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.navigationController = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Custom methods.

- (IBAction)doneButtonPressed:(id)sender {
  [self.parentViewController dismissModalViewControllerAnimated:YES];
}

@end
