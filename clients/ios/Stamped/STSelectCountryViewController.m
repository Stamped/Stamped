//
//  STSelectCountryViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSelectCountryViewController.h"

@implementation STSelectCountryViewController

- (id)init {
  self = [super initWithNibName:@"STSelectCountryViewController" bundle:nil];
  if (self) {
    
  }
  return self;
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
}

- (void)viewDidUnload {
  [super viewDidUnload];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
