//
//  EditProfileViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/3/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EditProfileViewController.h"

#import "User.h"
#import "STImageView.h"

@implementation EditProfileViewController

@synthesize user = user_;
@synthesize stampImageView = stampImageView_;
@synthesize userImageView = userImageView_;

- (id)init {
  self = [self initWithNibName:@"EditProfileViewController" bundle:nil];
  if (self) {
  }
  return self;
}

- (void)dealloc {
  self.user = nil;
  self.stampImageView = nil;
  self.userImageView = nil;
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
  self.stampImageView.image = user_.stampImage;
  self.userImageView.userInteractionEnabled = NO;
  self.userImageView.imageURL = user_.profileImageURL;
  // Do any additional setup after loading the view from its nib.
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.stampImageView = nil;
  self.userImageView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Actions

- (IBAction)settingsButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

@end
