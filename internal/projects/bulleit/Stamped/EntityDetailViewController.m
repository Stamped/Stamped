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
#import "DetailedEntity.h"
#import "Entity.h"
#import "Stamp.h"
#import "SearchResult.h"
#import "UIColor+Stamped.h"
#import "StampDetailViewController.h"
#import "PlaceDetailViewController.h"
#import "OtherDetailViewController.h"
#import "Notifications.h"
#import "Favorite.h"
#import "User.h"
#import "StampedAppDelegate.h"

static NSString* const kEntityLookupPath = @"/entities/show.json";
static NSString* const kCreateFavoritePath = @"/favorites/create.json";

static const CGFloat kOneLineDescriptionHeight = 20.0;

@interface EntityDetailViewController ()

@property (nonatomic, retain) UIButton* addFavoriteButton;
@property (nonatomic, retain) UIActivityIndicatorView* spinner;

- (void)addTodoBar;
- (NSAttributedString*)todoAttributedString:(User*)user;
- (void)todoBarTapped:(UITapGestureRecognizer*)recognizer;
- (void)loadEntityDataFromServer;
- (void)showContents;
- (void)setupSectionViews;
- (void)addSelfAsFavorite;
- (void)dismissSelf;
- (void)ensureTitleLabelHeight;
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
@synthesize addFavoriteButton = addFavoriteButton_;
@synthesize spinner = spinner_;
@synthesize imageView = imageView_;


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
  self.addFavoriteButton = nil;
  self.spinner = nil;
  self.imageView = nil;
  
  for (CollapsibleViewController* vc in sectionsDict_.objectEnumerator)
    vc.delegate = nil;
  
  [DetailedEntity.managedObjectContext refreshObject:detailedEntity_ mergeChanges:NO];
  [entityObject_ release];
  [detailedEntity_ release];
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
  if (![[RKClient sharedClient] isNetworkAvailable]) {
    return;
  } 
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* entityMapping = [objectManager.mappingProvider mappingForKeyPath:@"DetailedEntity"];
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
  NSAssert(objectForKey, @"Must provide a valid search or entity ID to fetch data");
  objectLoader.params = [NSDictionary dictionaryWithObject:objectForKey forKey:key];
  [objectLoader send];
  [self view];
  [self.loadingView startAnimating];
}

- (void)showContents {
  // Default does nothing. Override in subclasses.
}

- (void)setupSectionViews {
  
//  if (self.contentHeight < self.scrollView.frame.size.height) {
//    self.mainContentView.backgroundColor = [UIColor colorWithWhite:0.83 alpha:1.0];
//    UIImageView* imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"eDetail_empty_shadow"]];
//    imageView.frame = CGRectMake(0, self.contentHeight, 320, 320);
//    [self.mainContentView addSubview:imageView];
//    [imageView release];
//  }
}

- (void)ensureTitleLabelHeight {
  if ([self lineCountOfLabel:self.titleLabel] > 1) {
    CGFloat newHeight = self.titleLabel.font.lineHeight * 2 + 8;
    CGFloat delta = newHeight - self.titleLabel.frame.size.height;
    self.titleLabel.frame = CGRectMake(self.titleLabel.frame.origin.x, self.titleLabel.frame.origin.y,
                                       self.titleLabel.frame.size.width, newHeight);
    self.descriptionLabel.frame = CGRectOffset(self.descriptionLabel.frame, 0.0, delta);
    self.mainActionsView.frame = CGRectOffset(self.mainActionsView.frame, 0.0, delta);
    self.mainContentView.frame = CGRectOffset(self.mainContentView.frame, 0.0, delta);
    if ([self isKindOfClass:[PlaceDetailViewController class]] ||
        [self isKindOfClass:[OtherDetailViewController class]]) {
      ((PlaceDetailViewController*)self).mapContainerView.frame = CGRectOffset(((PlaceDetailViewController*)self).mapContainerView.frame, 0.0, delta);
    }
  }
  if (titleLabel_.text.length > 60) {
    self.titleLabel.text = [self.titleLabel.text substringToIndex:55];
    self.titleLabel.text = [self.titleLabel.text stringByAppendingString:@"…"];
  }
}

#pragma mark - View lifecycle

- (void)viewDidLoad {  
  [super viewDidLoad];
  UIBarButtonItem* backButton = [[UIBarButtonItem alloc] initWithTitle:@"Details"
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil];
  [[self navigationItem] setBackBarButtonItem:backButton];
  [backButton release];
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

  if (entityObject_.favorite.stamp)
    [self addTodoBar];
  
  [self ensureTitleLabelHeight];
  
  if (![[RKClient sharedClient] isNetworkAvailable]) {
    UIImageView* iv = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"eDetail_notConnected"]];
    CGFloat xOffset = CGRectGetWidth(self.view.bounds) - CGRectGetWidth(iv.bounds);
    CGFloat yOffset = CGRectGetHeight(self.view.bounds) - CGRectGetHeight(iv.bounds);
    iv.frame = CGRectMake(floorf(xOffset/2), floorf(0.95 * yOffset/2), iv.bounds.size.width, iv.bounds.size.height);
    [self.scrollView addSubview:iv];
    [iv release];
  }
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
  self.scrollView.contentSize = CGSizeMake(self.scrollView.contentSize.width,
                                           self.scrollView.contentSize.height + bar.bounds.size.height);
  [bar release];
}

- (void)addToolbar {
  UIView* bar = [[UIView alloc] initWithFrame:CGRectMake(0, self.view.frame.size.height - 56, 320, 56)];
  bar.layer.shadowPath = [UIBezierPath bezierPathWithRect:bar.bounds].CGPath;
  bar.layer.shadowOpacity = 0.2;
  bar.layer.shadowOffset = CGSizeMake(0, -1);
  CAGradientLayer* toolbarGradient = [[CAGradientLayer alloc] init];
  toolbarGradient.frame = bar.bounds;
  toolbarGradient.colors = [NSArray arrayWithObjects:
                            (id)[UIColor whiteColor].CGColor,
                            (id)[UIColor colorWithWhite:0.85 alpha:1.0].CGColor, nil];
  [bar.layer addSublayer:toolbarGradient];
  [toolbarGradient release];
  
  UIButton* button = [UIButton buttonWithType:UIButtonTypeCustom];
  UIImage* buttonBG = [UIImage imageNamed:@"big_blue_button_bg"];
  [button setBackgroundImage:buttonBG forState:UIControlStateNormal];
  [button setTitle:@"Add To-Do" forState:UIControlStateNormal];
  [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
  button.titleLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:14.0];
  button.titleLabel.shadowColor = [UIColor colorWithWhite:0.3 alpha:1.0];
  button.titleLabel.shadowOffset = CGSizeMake(0.0, -1.0);
  button.frame = CGRectMake((bar.frame.size.width - buttonBG.size.width) / 2, 8.0, buttonBG.size.width, buttonBG.size.height);
  [button addTarget:self action:@selector(addSelfAsFavorite) forControlEvents:UIControlEventTouchUpInside];
  self.addFavoriteButton = button;
  [bar addSubview:self.addFavoriteButton];
  
  UIActivityIndicatorView* activity = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
  activity.center = button.center;
  activity.hidesWhenStopped = YES;
  [activity stopAnimating];
  self.spinner = activity;
  [bar addSubview:self.spinner];
  
  [self.view addSubview:bar];
  CGRect frame = self.scrollView.frame;
  frame.size.height -= 56;
  self.scrollView.frame = frame;
  
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
  NSString* screenName = user.screenName;
  if ([user.screenName isEqualToString:[AccountManager sharedManager].currentUser.screenName])
    screenName = @"you";

  NSString* full = [NSString stringWithFormat:@"To-do added via %@", screenName];
  NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
  [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                         (id)style, (id)kCTParagraphStyleAttributeName,
                         (id)[UIColor whiteColor].CGColor, (id)kCTForegroundColorAttributeName, nil]
                  range:NSMakeRange(0, full.length)];
  [string addAttribute:(NSString*)kCTFontAttributeName
                 value:(id)font 
                 range:[full rangeOfString:screenName options:NSBackwardsSearch]];
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
  self.addFavoriteButton = nil;
  self.spinner = nil;
  self.imageView = nil;
  
  for (CollapsibleViewController* vc in sectionsDict_.objectEnumerator)
    vc.delegate = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
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
  // Handle callback from "Add To-Do"
  if ([objectLoader.resourcePath isEqualToString:kCreateFavoritePath]) {
    [self.spinner stopAnimating];
    [self dismissSelf];
    return;
  }
  
  dataLoaded_ = YES;
  [detailedEntity_ release];
  detailedEntity_ = [(DetailedEntity*)object retain];
  [self showContents];
  [self.loadingView stopAnimating];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  // Handle callback from "Add To-Do"
  if ([objectLoader.resourcePath isEqualToString:kCreateFavoritePath]) {
    [self.spinner stopAnimating];
    self.addFavoriteButton.hidden = NO;
  }
  
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadEntityDataFromServer];
    return;
  }
  [self.loadingView stopAnimating];
}

- (void)objectLoaderDidLoadUnexpectedResponse:(RKObjectLoader *)objectLoader {
  if ([objectLoader.response isUnauthorized]) {
    [[AccountManager sharedManager] refreshToken];
    [self loadEntityDataFromServer];
  }
  [self.loadingView stopAnimating];
}

#pragma mark - Section / collapsible view management.

- (NSUInteger)lineCountOfLabel:(UILabel *)label {  
  CGRect frame = label.frame;
  frame.size.width = label.frame.size.width;
  frame.size = [label sizeThatFits:frame.size];
//  label.frame = frame;
  CGFloat lineHeight = label.font.lineHeight;
  NSUInteger linesInLabel = floor(frame.size.height/lineHeight);
  return linesInLabel;
}

- (CollapsibleViewController*)makeSectionWithName:(NSString*)name {
  CollapsibleViewController* collapsibleVC = [[CollapsibleViewController alloc] 
                                              initWithNibName:@"CollapsibleViewController" bundle:nil];
  
  collapsibleVC.view.frame = CGRectMake(0, [self contentHeight], 
                                        mainContentView_.frame.size.width, 
                                        collapsibleVC.collapsedHeight);
  
  collapsibleVC.sectionLabel.text = name;
  collapsibleVC.delegate = self;
  return [collapsibleVC autorelease];
  //TODO: ensure this doesn't leak
}

- (void)addSection:(CollapsibleViewController*)section {
  [sectionsDict_ setObject:section forKey:section.sectionLabel.text];
  [mainContentView_ addSubview:section.view];
  if (self.imageView && self.imageView.hidden == NO)
    [section moveArrowViewIfBehindImageView:self.imageView];
}

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
  if (self.imageView && self.imageView.hidden == NO)
    [collapsibleVC moveArrowViewIfBehindImageView:self.imageView];
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
  if (self.imageView && self.imageView.hidden == NO)
    [collapsibleVC moveArrowViewIfBehindImageView:self.imageView];
}

- (void)addSectionStampedBy {
  // Make sure that the current user follows someone who stamped this entity.
  NSPredicate* p = [NSPredicate predicateWithFormat:@"temporary == NO AND deleted == NO"];
  NSArray* stamps = [[entityObject_.stamps allObjects] filteredArrayUsingPredicate:p];
  if (stamps.count == 0)
    return;
  
  CollapsibleViewController* collapsibleVC = [self makeSectionWithName:@"Stamped by"];
  
  collapsibleVC.iconView.image = [UIImage imageNamed:@"stamp_12pt_solid"];
  collapsibleVC.iconView.alpha = 0.6;
  collapsibleVC.sectionLabel.frame = CGRectOffset(collapsibleVC.sectionLabel.frame, collapsibleVC.iconView.frame.size.width, 0);
  
  collapsibleVC.numLabel.hidden = NO;
  collapsibleVC.iconView.hidden = NO;
  
  [collapsibleVC addImagesForStamps:entityObject_.stamps];
  [self addSection:collapsibleVC];
  [collapsibleVC expand];
  [collapsibleVC swapArrowImage];
}

#pragma mark - CollapsibleViewControllerDelegate methods.
- (void)collapsibleViewController:(CollapsibleViewController*)collapsibleVC willChangeHeightBy:(CGFloat)delta {
  for (CollapsibleViewController* vc in sectionsDict_.objectEnumerator) {
    if (CGRectGetMinY(vc.view.frame) > CGRectGetMinY(collapsibleVC.view.frame)) {
      [UIView animateWithDuration:0.25 animations:^{ vc.view.frame = CGRectOffset(vc.view.frame, 0, delta);
                                                     if (self.imageView != nil && self.imageView.hidden == NO)                                        
                                                         [vc moveArrowViewIfBehindImageView:self.imageView];}];
    }
  }
  
  CGFloat newHeight = [self contentHeight];
  newHeight += delta;

  CGRect contentFrame = self.mainContentView.frame;
  contentFrame.size.height = newHeight;
  self.mainContentView.frame = contentFrame;
  
  newHeight += CGRectGetMinY(self.mainContentView.frame);

  BOOL shouldScrollDown = NO;
  if(scrollView_.contentOffset.y != 0 && delta > 0 && !scrollView_.isDragging && !scrollView_.isDecelerating &&
     scrollView_.contentOffset.y >=  scrollView_.contentSize.height - scrollView_.frame.size.height)
    shouldScrollDown = YES;
  scrollView_.contentSize = CGSizeMake(scrollView_.contentSize.width, newHeight);
  if (shouldScrollDown)
    self.scrollView.contentOffset = CGPointMake(0, scrollView_.contentSize.height - scrollView_.frame.size.height);
}

- (void)callMoveArrowOnCollapsibleViewController:(CollapsibleViewController*)cvc {
  if (imageView_ != nil && imageView_.hidden == NO)
    [cvc moveArrowViewIfBehindImageView:self.imageView];
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

#pragma mark - Make a todo from this entity.

- (void)addSelfAsFavorite {
  self.addFavoriteButton.hidden = YES;
  self.spinner.hidden = NO;
  [self.spinner startAnimating];
  [self.addFavoriteButton setNeedsDisplay];
  [self.spinner setNeedsDisplay];
  
  NSString* path = kCreateFavoritePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = favoriteMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:detailedEntity_.entityID, @"entity_id", nil];
  [objectLoader send];
}

- (void)dismissSelf {
  UIViewController* vc = nil;
  if ([self respondsToSelector:@selector(presentingViewController)]) 
    vc = [(id)self presentingViewController];
  else
    vc = self.parentViewController;
  if (vc)
    [vc dismissModalViewControllerAnimated:YES];
}

#pragma mark - Actions.

- (void)imageViewTapped {
  ShowImageViewController* controller = [[ShowImageViewController alloc] initWithNibName:@"ShowImageViewController" bundle:nil];
  if (self.imageView.image)
    controller.image = self.imageView.image;
  else if (detailedEntity_.image && ![detailedEntity_.image isEqualToString:@""])
    controller.imageURL = detailedEntity_.image;
  else
    return;
  [self.navigationController pushViewController:controller animated:YES];
  [controller release];
}

- (void)STImageView:(STImageView *)imageView didLoadImage:(UIImage *)image {
  // Default does nothing. Override in subclasses.
}
  
@end
