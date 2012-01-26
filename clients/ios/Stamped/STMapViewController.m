//
//  STMapViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMapViewController.h"

#import "STSearchField.h"

@implementation STMapViewController

@synthesize searchField = searchField_;
@synthesize mapView = mapView_;

- (id)init {
  self = [super initWithNibName:@"STMapViewController" bundle:nil];
  if (self) {
    
  }
  return self;
}

- (void)dealloc {
  self.searchField = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
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
  // Do any additional setup after loading the view from its nib.
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.searchField = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Actions.

- (IBAction)cancelButtonPressed:(id)sender {
  
}

- (IBAction)locationButtonPressed:(id)sender {
  
}

@end
