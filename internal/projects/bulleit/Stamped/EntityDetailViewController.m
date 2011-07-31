//
//  EntityDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EntityDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "Stamp.h"

static const CGFloat kOneLineDescriptionHeight = 20.0;

@interface EntityDetailViewController ()

@end

@implementation EntityDetailViewController

@synthesize scrollView = scrollView_;
@synthesize titleLabel = titleLabel_;
@synthesize descriptionLabel = descriptionLabel_;
@synthesize mainActionButton = mainActionButton_;
@synthesize mainActionLabel = mainActionLabel_;

- (id)initWithEntityObject:(Entity*)entity {
  self = [self initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    entityObject_ = [entity retain];
  }
  return self;
}

- (void)dealloc {
  self.titleLabel = nil;
  self.descriptionLabel = nil;
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
  self.scrollView = nil;
  [entityObject_ release];
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
  scrollView_.contentSize = self.view.bounds.size;
  CAGradientLayer* backgroundGradient = [[CAGradientLayer alloc] init];
  backgroundGradient.colors = [NSArray arrayWithObjects:
                               (id)[UIColor colorWithWhite:1.0 alpha:1.0].CGColor,
                               (id)[UIColor colorWithWhite:0.93 alpha:1.0].CGColor, nil];
  backgroundGradient.frame = self.view.bounds;
  [self.view.layer insertSublayer:backgroundGradient atIndex:0];
  [backgroundGradient release];
  titleLabel_.text = entityObject_.title;
  titleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:27];
  titleLabel_.textColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  descriptionLabel_.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  mainActionButton_.layer.masksToBounds = YES;
  mainActionButton_.layer.cornerRadius = 2.0;
  mainActionLabel_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.25];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.titleLabel = nil;
  self.descriptionLabel = nil;
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
