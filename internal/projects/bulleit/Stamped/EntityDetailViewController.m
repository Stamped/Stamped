//
//  EntityDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EntityDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "Entity.h"
#import "Stamp.h"

static const CGFloat kOneLineDescriptionHeight = 20.0;

@interface EntityDetailViewController ()
- (void)loadEntityDataFromServer;
- (void)showContents;
@end

@implementation EntityDetailViewController

@synthesize scrollView = scrollView_;
@synthesize titleLabel = titleLabel_;
@synthesize descriptionLabel = descriptionLabel_;
@synthesize mainActionsView = mainActionsView_;
@synthesize mainActionButton = mainActionButton_;
@synthesize mainActionLabel = mainActionLabel_;
@synthesize categoryImageView = categoryImageView_;
@synthesize loadingView = loadingView_;

- (id)initWithEntityObject:(Entity*)entity {
  self = [self initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    entityObject_ = [entity retain];
    [self loadEntityDataFromServer];
  }
  return self;
}

- (void)dealloc {
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.titleLabel = nil;
  self.descriptionLabel = nil;
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
  self.scrollView = nil;
  self.categoryImageView = nil;
  self.mainActionsView = nil;
  self.loadingView = nil;
  [entityObject_ release];
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  
  // Release any cached data, images, etc that aren't in use.
}

- (void)loadEntityDataFromServer {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* entityMapping = [objectManager.mappingProvider mappingForKeyPath:@"Entity"];
  NSString* resourcePath = [@"/entities/show.json" appendQueryParams:
      [NSDictionary dictionaryWithObjectsAndKeys:entityObject_.entityID, @"entity_id",
          [AccountManager sharedManager].authToken.accessToken, @"oauth_token",nil]];
  [objectManager loadObjectsAtResourcePath:resourcePath
                             objectMapping:entityMapping
                                  delegate:self];
  [self view];
  [self.loadingView startAnimating];
}

- (void)showContents {
  // Default does nothing. Override in subclasses.
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
  categoryImageView_.image = entityObject_.categoryImage;
  descriptionLabel_.text = nil;
  descriptionLabel_.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  mainActionButton_.layer.masksToBounds = YES;
  mainActionButton_.layer.cornerRadius = 2.0;
  mainActionLabel_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.25];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.titleLabel = nil;
  self.descriptionLabel = nil;
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
  self.scrollView = nil;
  self.categoryImageView = nil;
  self.mainActionsView = nil;
  self.loadingView = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  viewIsVisible_ = YES;
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  viewIsVisible_ = NO;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObject:(id)object {
  dataLoaded_ = YES;
  [self showContents];
  [self.loadingView stopAnimating];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadEntityDataFromServer];
    return;
  }
  [self.loadingView stopAnimating];
}

@end
