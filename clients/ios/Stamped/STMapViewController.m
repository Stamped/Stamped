//
//  STMapViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMapViewController.h"

#import "StampedAppDelegate.h"
#import "STSearchField.h"

@interface STMapViewController ()

- (void)overlayTapped:(UIGestureRecognizer*)recognizer;

@end

@implementation STMapViewController

@synthesize overlayView = overlayView_;
@synthesize locationButton = locationButton_;
@synthesize cancelButton = cancelButton_;
@synthesize searchField = searchField_;
@synthesize mapView = mapView_;

- (id)init {
  self = [super initWithNibName:@"STMapViewController" bundle:nil];
  if (self) {
    
  }
  return self;
}

- (void)dealloc {
  self.overlayView = nil;
  self.locationButton = nil;
  self.cancelButton = nil;
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
  UITapGestureRecognizer* recognizer = [[UITapGestureRecognizer alloc] initWithTarget:self
                                                                               action:@selector(overlayTapped:)];
  [overlayView_ addGestureRecognizer:recognizer];
  [recognizer release];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.overlayView = nil;
  self.locationButton = nil;
  self.cancelButton = nil;
  self.searchField = nil;
  self.mapView.delegate = nil;
  self.mapView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (UINavigationController*)navigationController {
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  return delegate.navigationController;
}

#pragma mark - UITextFieldDelegate methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [self.navigationController setNavigationBarHidden:YES animated:YES];
  [UIView animateWithDuration:0.3 animations:^{
    overlayView_.alpha = 0.75;
  }];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  [self.navigationController setNavigationBarHidden:NO animated:YES];
  [UIView animateWithDuration:0.3 animations:^{
    overlayView_.alpha = 0;
  }];
}

#pragma mark - Actions.

- (IBAction)cancelButtonPressed:(id)sender {
  [searchField_ resignFirstResponder];
}

- (IBAction)locationButtonPressed:(id)sender {
  
}

#pragma mark - Gesture recognizers.

- (void)overlayTapped:(UIGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  [searchField_ resignFirstResponder];
}

@end
