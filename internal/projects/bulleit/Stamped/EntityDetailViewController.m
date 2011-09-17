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
#import "UIColor+Stamped.h"
#import "PlaceDetailViewController.h"
#import "Notifications.h"

static NSString* const kEntityLookupPath = @"/entities/show.json";

static const CGFloat kOneLineDescriptionHeight = 20.0;

@interface EntityDetailViewController ()
- (void)loadEntityDataFromServer;
- (void)showContents;
- (void)setupSectionViews;
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
@synthesize mainContentView = mainContentView_;


- (id)initWithEntityObject:(Entity*)entity {
  self = [self initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    entityObject_ = [entity retain];
    [self loadEntityDataFromServer];
    sectionsDict_ = [[NSMutableDictionary dictionary] retain];
  }
  return self;
}

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.titleLabel = nil;
  self.descriptionLabel = nil;
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
  self.scrollView = nil;
  self.categoryImageView = nil;
  self.mainActionsView = nil;
  self.loadingView = nil;
  [entityObject_ release];
  [sectionsDict_ release];
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
  RKObjectLoader*   objectLoader = [objectManager objectLoaderWithResourcePath:kEntityLookupPath
                                                                    delegate:self];
  objectLoader.objectMapping = entityMapping;
  objectLoader.params = [NSDictionary dictionaryWithKeysAndObjects:@"entity_id", entityObject_.entityID, nil];
  [objectLoader send];
  [self view];
  [self.loadingView startAnimating];
}

- (void)showContents {
  // Default does nothing. Override in subclasses.
}

- (void)setupSectionViews {
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
  descriptionLabel_.textColor = [UIColor stampedGrayColor];
  mainActionButton_.layer.masksToBounds = YES;
  mainActionButton_.layer.cornerRadius = 2.0;
  mainActionLabel_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.25];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.titleLabel = nil;
  self.descriptionLabel = nil;
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
  self.scrollView = nil;
  self.categoryImageView = nil;
  self.mainActionsView = nil;
  self.loadingView = nil;
  
  for (CollapsibleViewController* vc in sectionsDict_.objectEnumerator)
    vc.delegate = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  self.categoryImageView.contentMode = UIViewContentModeRight;
  viewIsVisible_ = YES;
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
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
  NSLog(@"Query: %@ Response: %@", objectLoader.resourcePath, objectLoader.response.bodyAsString);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadEntityDataFromServer];
    return;
  }
  [self.loadingView stopAnimating];
}


#pragma mark - Section / collapsible view management.

- (void)addSectionWithName:(NSString*)name {
  CollapsibleViewController* collapsibleVC = [[CollapsibleViewController alloc] 
                                              initWithNibName:@"CollapsibleViewController" bundle:nil];
  
  collapsibleVC.view.frame = CGRectMake(0, [self contentHeight], 
                                        mainContentView_.frame.size.width, 
                                        collapsibleVC.collapsedHeight);
  
  collapsibleVC.sectionLabel.text = name;
  collapsibleVC.delegate = self;

  [sectionsDict_ setObject:collapsibleVC forKey:name];
  [mainContentView_ addSubview:collapsibleVC.view];
}

- (void)addSectionWithName:(NSString*)name previewHeight:(CGFloat)previewHeight;
{
  CollapsibleViewController* collapsibleVC = [[CollapsibleViewController alloc] 
                                              initWithNibName:@"CollapsiblePreviewController" bundle:nil];

  collapsibleVC.collapsedHeight = previewHeight;
  collapsibleVC.view.frame = CGRectMake(0, [self contentHeight], 
                                        mainContentView_.frame.size.width, 
                                        collapsibleVC.collapsedHeight);
  collapsibleVC.sectionLabel.text = name;
  collapsibleVC.delegate = self;
  
  [sectionsDict_ setObject:collapsibleVC forKey:name];
  [mainContentView_ addSubview:collapsibleVC.view];
}

- (void)addSectionStampedBy
{
  [self addSectionWithName:@"Stamped by"];
  CollapsibleViewController* collapsibleVC = [sectionsDict_ objectForKey:@"Stamped by"];
  
  collapsibleVC.iconView.image = [UIImage imageNamed:@"stamp_12pt_solid"];
  collapsibleVC.iconView.alpha = 0.6;
  collapsibleVC.sectionLabel.frame = CGRectOffset(collapsibleVC.sectionLabel.frame, collapsibleVC.iconView.frame.size.width, 0);
  
  collapsibleVC.numLabel.hidden = NO;
  collapsibleVC.iconView.hidden = NO;
  
  [collapsibleVC addImagesForStamps:entityObject_.stamps];
}


// Delegate method
- (void)collapsibleViewController:(CollapsibleViewController *)collapsibleVC willChangeHeightBy:(CGFloat)delta
{
  for (CollapsibleViewController* vc in sectionsDict_.objectEnumerator)
  {
    if (CGRectGetMinY(vc.view.frame) > CGRectGetMinY(collapsibleVC.view.frame))
    {
      [UIView animateWithDuration:0.25
                       animations:^{vc.view.frame = CGRectOffset(vc.view.frame, 0, delta);}];
    }
  }
  
  CGFloat newHeight = [self contentHeight];
  newHeight += delta;
  
 
  CGRect contentFrame = self.mainContentView.frame;
  contentFrame.size.height = newHeight;
  self.mainContentView.frame = contentFrame;
  
  newHeight += CGRectGetMinY(self.mainContentView.frame);
  
  
  self.scrollView.contentSize = CGSizeMake(scrollView_.contentSize.width, newHeight);  
}

- (CGFloat)contentHeight
{
  CGFloat contentHeight = 0.f;
  
  if (!sectionsDict_) return 0.f;
  if (sectionsDict_.count == 0) return 0.f;
  
  for (CollapsibleViewController* cvc in sectionsDict_.objectEnumerator)
  {
    contentHeight += cvc.view.frame.size.height;
  }
  
  return contentHeight;
}



@end
