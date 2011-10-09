//
//  EntityDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EntityDetailViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "Entity.h"
#import "Stamp.h"
#import "SearchResult.h"
#import "UIColor+Stamped.h"
#import "StampDetailViewController.h"
#import "PlaceDetailViewController.h"
#import "Notifications.h"
#import "Favorite.h"
#import "User.h"

static NSString* const kEntityLookupPath = @"/entities/show.json";

static const CGFloat kOneLineDescriptionHeight = 20.0;

@interface EntityDetailViewController ()
- (void)addTodoBar;
- (NSAttributedString*)todoAttributedString:(User*)user;
- (void)todoBarTapped:(UITapGestureRecognizer*)recognizer;
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
@synthesize shelfImageView = shelfImageView_;

- (id)initWithEntityObject:(Entity*)entity {
  self = [self initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    entityObject_ = [entity retain];
    [self loadEntityDataFromServer];
    sectionsDict_ = [[NSMutableDictionary alloc] init];
  }
  return self;
}

- (id)initWithSearchResult:(SearchResult*)searchResult {
  self = [self initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    searchResult_ = [searchResult retain];
    [self loadEntityDataFromServer];
    sectionsDict_ = [[NSMutableDictionary alloc] init];
  }
  return self;
}

- (void)dealloc {
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.titleLabel = nil;
  self.descriptionLabel = nil;
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
  self.shelfImageView = nil;
  self.scrollView = nil;
  self.categoryImageView = nil;
  self.mainActionsView = nil;
  self.mainContentView = nil;
  self.loadingView = nil;
  
  for (CollapsibleViewController* vc in sectionsDict_.objectEnumerator)
    vc.delegate = nil;

  [entityObject_ release];
  [searchResult_ release];
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
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kEntityLookupPath
                                                                    delegate:self];
  objectLoader.objectMapping = entityMapping;
  NSString* key = @"entity_id";
  id objectForKey = nil;
  if (entityObject_) {
    objectForKey = entityObject_.entityID;
  } else if (searchResult_) {
    if (searchResult_.entityID) {
      objectForKey = searchResult_.entityID;
    } else if (searchResult_.searchID) {
      key = @"search_id";
      objectForKey = searchResult_.searchID;
    }
  }
  NSAssert(objectForKey, @"Must provide a valid search of entity ID to fetch data");
  objectLoader.params = [NSDictionary dictionaryWithObject:objectForKey forKey:key];
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

  titleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:27];
  titleLabel_.textColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  if (entityObject_) {
    titleLabel_.text = entityObject_.title;
  } else if (searchResult_) {
    titleLabel_.text = searchResult_.title;
  }
  descriptionLabel_.text = nil;
  descriptionLabel_.textColor = [UIColor stampedGrayColor];
  mainActionButton_.layer.masksToBounds = YES;
  mainActionButton_.layer.cornerRadius = 2.0;
  mainActionLabel_.shadowColor = [UIColor colorWithWhite:0.0 alpha:0.25];

  if (entityObject_.favorite)
    [self addTodoBar];
}

- (void)addTodoBar {
  for (UIView* view in self.scrollView.subviews) {
    if (view == shelfImageView_)
      continue;

    view.frame = CGRectOffset(view.frame, 0, 44);
  }

  UIView* bar = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 44)];
  bar.backgroundColor = [UIColor colorWithWhite:0.0 alpha:.1];
  CAGradientLayer* gradient = [[CAGradientLayer alloc] init];
  gradient.frame = bar.bounds;
  gradient.startPoint = CGPointZero;
  gradient.endPoint = CGPointMake(0, 1);
  gradient.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithRed:0.043 green:0.38 blue:0.85 alpha:1.0].CGColor,
                     (id)[UIColor colorWithRed:0.29 green:0.56 blue:0.95 alpha:1.0].CGColor, nil];
  [bar.layer addSublayer:gradient];
  bar.layer.shadowPath = [UIBezierPath bezierPathWithRect:bar.bounds].CGPath;
  bar.layer.shadowColor = [UIColor blackColor].CGColor;
  bar.layer.shadowOpacity = 0.25;
  bar.layer.shadowOffset = CGSizeMake(0, 1);
  bar.layer.shadowRadius = 3;
  [gradient release];
  
  UIImageView* icon = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"eDetail_todo_icon"]];
  icon.frame = CGRectOffset(icon.frame, 14, 14);
  [bar addSubview:icon];
  [icon release];
  
  UIImageView* arrow = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"eDetail_todo_arrow"]];
  arrow.frame = CGRectOffset(arrow.frame, 297, 18);
  [bar addSubview:arrow];
  [arrow release];
  
  CATextLayer* text = [[CATextLayer alloc] init];
  text.frame = CGRectMake(CGRectGetMaxX(icon.frame) + 2,
                                       CGRectGetMinY(icon.frame) + 5, 200, 14);
  text.truncationMode = kCATruncationEnd;
  text.contentsScale = [[UIScreen mainScreen] scale];
  text.fontSize = 12.0;
  text.foregroundColor = [UIColor whiteColor].CGColor;
  text.string = [self todoAttributedString:entityObject_.favorite.stamp.user];
  [bar.layer addSublayer:text];
  [text release];
  
  UITapGestureRecognizer* recognizer = [[UITapGestureRecognizer alloc] initWithTarget:self
                                                                               action:@selector(todoBarTapped:)];
  [bar addGestureRecognizer:recognizer];
  [recognizer release];
  [self.scrollView insertSubview:bar atIndex:0];
  [bar release];
}

- (NSAttributedString*)todoAttributedString:(User*)user {
  if (!user)
    return nil;
  
  CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
  NSString* full = [NSString stringWithFormat:@"To-do added via %@", user.screenName];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                         (id)style, (id)kCTParagraphStyleAttributeName,
                         (id)[UIColor whiteColor].CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  [string addAttribute:(NSString*)kCTFontAttributeName
                 value:(id)font 
                 range:[full rangeOfString:user.screenName options:NSBackwardsSearch]];
  CFRelease(font);
  CFRelease(style);
  return [string autorelease];
}

- (void)todoBarTapped:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  StampDetailViewController* vc = [[StampDetailViewController alloc] initWithStamp:entityObject_.favorite.stamp];
  [self.navigationController pushViewController:vc animated:YES];
  [vc release];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKClient sharedClient].requestQueue cancelRequestsWithDelegate:self];
  self.titleLabel = nil;
  self.descriptionLabel = nil;
  self.mainActionLabel = nil;
  self.mainActionButton = nil;
  self.shelfImageView = nil;
  self.scrollView = nil;
  self.categoryImageView = nil;
  self.mainActionsView = nil;
  self.loadingView = nil;
  self.mainContentView = nil;
  
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
  [entityObject_ release];
  entityObject_ = [(Entity*)object retain];
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

- (void)addSectionWithName:(NSString*)name previewHeight:(CGFloat)previewHeight {
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

- (void)addSectionStampedBy {
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
- (void)collapsibleViewController:(CollapsibleViewController*)collapsibleVC willChangeHeightBy:(CGFloat)delta {
  for (CollapsibleViewController* vc in sectionsDict_.objectEnumerator) {
    if (CGRectGetMinY(vc.view.frame) > CGRectGetMinY(collapsibleVC.view.frame)) {
      [UIView animateWithDuration:0.25
                       animations:^{ vc.view.frame = CGRectOffset(vc.view.frame, 0, delta); }];
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

- (CGFloat)contentHeight {
  if (sectionsDict_.count == 0)
    return 0.0f;

  CGFloat contentHeight = 0.0f;
  for (CollapsibleViewController* cvc in sectionsDict_.objectEnumerator) {
    contentHeight += cvc.view.frame.size.height;
  }
  
  return contentHeight;
}

@end
