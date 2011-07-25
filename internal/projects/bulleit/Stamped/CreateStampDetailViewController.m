//
//  CreateStampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreateStampDetailViewController.h"

#import "Entity.h"
#import "STNavigationBar.h"

@implementation CreateStampDetailViewController

@synthesize titleLabel = titleLabel_;
@synthesize detailLabel = detailLabel_;
@synthesize categoryImageView = categoryImageView_;
@synthesize navigationBar = navigationBar_;

- (id)initWithEntity:(Entity*)entityObject {
  self = [super initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    entityObject_ = [entityObject retain];
  }
  return self;
}

- (void)dealloc {
  [entityObject_ release];
  self.titleLabel = nil;
  self.detailLabel = nil;
  self.categoryImageView = nil;
  self.navigationBar = nil;
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
  navigationBar_.hideLogo = YES;

  titleLabel_.text = entityObject_.title;
  titleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:36];
  titleLabel_.textColor = [UIColor colorWithWhite:0.3 alpha:1.0];
  
  detailLabel_.text = entityObject_.subtitle;
  detailLabel_.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  
  categoryImageView_.image = entityObject_.categoryImage;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.titleLabel = nil;
  self.detailLabel = nil;
  self.categoryImageView = nil;
  self.navigationBar = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)backButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

@end
