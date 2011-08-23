//
//  StampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/6/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampDetailViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>
#import <RestKit/CoreData/CoreData.h>

#import "AccountManager.h"
#import "CreateStampViewController.h"
#import "EntityDetailViewController.h"
#import "Comment.h"
#import "PlaceDetailViewController.h"
#import "GenericItemDetailViewController.h"
#import "Entity.h"
#import "Favorite.h"
#import "Notifications.h"
#import "ProfileViewController.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "StampDetailCommentView.h"
#import "UserImageView.h"

static const CGFloat kMainCommentFrameMinHeight = 75.0;
static const CGFloat kKeyboardHeight = 216.0;
static NSString* const kCreateFavoritePath = @"/favorites/create.json";
static NSString* const kRemoveFavoritePath = @"/favorites/remove.json";
static NSString* const kCreateCommentPath = @"/comments/create.json";

@interface StampDetailViewController ()
- (void)setUpHeader;
- (void)setUpToolbar;
- (void)setUpMainContentView;
- (void)setUpCommentsView;
- (void)handleTap:(UITapGestureRecognizer*)recognizer;
- (void)handleEntityTap:(UITapGestureRecognizer*)recognizer;
- (void)handleCommentUserImageViewTap:(NSNotification*)notification;
- (void)handleUserImageViewTap:(id)sender;
- (void)renderComments;
- (void)addComment:(Comment*)comment;
- (void)loadCommentsFromServer;
- (void)preloadEntityView;
@end

@implementation StampDetailViewController

@synthesize headerView = headerView_;
@synthesize mainCommentContainer = mainCommentContainer_;
@synthesize scrollView = scrollView_;
@synthesize addCommentField = addCommentField_;
@synthesize commentsView = commentsView_;
@synthesize activityView = activityView_;
@synthesize bottomToolbar = bottomToolbar_;
@synthesize currentUserImageView = currentUserImageView_;
@synthesize commenterImageView = commenterImageView_;
@synthesize commenterNameLabel = commenterNameLabel_;
@synthesize stampedLabel = stampedLabel_;
@synthesize loadingView = loadingView_;
@synthesize addFavoriteButton = addFavoriteButton_;

- (id)initWithStamp:(Stamp*)stamp {
  self = [self initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    stamp_ = [stamp retain];
  }
  return self;
}

- (void)dealloc {
  [stamp_ release];
  [detailViewController_ release];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.headerView = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.mainCommentContainer = nil;
  self.scrollView = nil;
  self.currentUserImageView = nil;
  self.commenterImageView = nil;
  self.commenterNameLabel = nil;
  self.stampedLabel = nil;
  self.loadingView = nil;
  self.addFavoriteButton = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewWillDisappear:(BOOL)animated {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  [super viewWillDisappear:animated];
}

- (void)viewWillAppear:(BOOL)animated {
  [[NSNotificationCenter defaultCenter] addObserver:self
                                           selector:@selector(handleCommentUserImageViewTap:)
                                               name:kCommentUserImageTappedNotification
                                             object:nil];
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [self preloadEntityView];
  [super viewDidAppear:animated];
}

- (void)viewDidLoad {
  [super viewDidLoad];

  UITapGestureRecognizer* gestureRecognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
  [self.view addGestureRecognizer:gestureRecognizer];
  gestureRecognizer.cancelsTouchesInView = NO;
  [gestureRecognizer release];

  scrollView_.contentSize = self.view.bounds.size;
  
  [self setUpToolbar];
  [self setUpHeader];

  activityView_.layer.shadowOpacity = 0.1;
  activityView_.layer.shadowOffset = CGSizeMake(0, 1);
  activityView_.layer.shadowRadius = 2;
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;

  mainCommentContainer_.layer.shadowOpacity = 0.1;
  mainCommentContainer_.layer.shadowOffset = CGSizeMake(0, 0);
  mainCommentContainer_.layer.shadowRadius = 2;
  mainCommentContainer_.layer.shadowPath =
      [UIBezierPath bezierPathWithRect:mainCommentContainer_.bounds].CGPath;

  if (stamp_.entityObject.favorite)
    self.addFavoriteButton.selected = YES;
  
  [self setUpMainContentView];
  [self setUpCommentsView];

  [self renderComments];
  //[self loadCommentsFromServer];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.headerView = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.mainCommentContainer = nil;
  self.scrollView = nil;
  self.currentUserImageView = nil;
  self.commenterImageView = nil;
  self.commenterNameLabel = nil;
  self.stampedLabel = nil;
  self.loadingView = nil;
  self.addFavoriteButton = nil;
}

- (void)setUpHeader {
  NSString* fontString = @"TitlingGothicFBComp-Regular";
  CGFloat fontSize = 36.0;
  CGSize stringSize = [stamp_.entityObject.title sizeWithFont:[UIFont fontWithName:fontString size:fontSize]
                                                     forWidth:280
                                                lineBreakMode:UILineBreakModeTailTruncation];
  
  UILabel* nameLabel = [[UILabel alloc] initWithFrame:CGRectMake(15, 15, stringSize.width, stringSize.height)];
  nameLabel.font = [UIFont fontWithName:fontString size:fontSize];
  nameLabel.text = stamp_.entityObject.title;
  nameLabel.textColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  nameLabel.backgroundColor = [UIColor clearColor];
  [headerView_ addSubview:nameLabel];
  [nameLabel release];

  // Badge stamp.
  CALayer* stampLayer = [[CALayer alloc] init];
  stampLayer.frame = CGRectMake(15 + stringSize.width - (46 / 2),
                                17 - (46 / 2),
                                46, 46);
  stampLayer.contents = (id)stamp_.user.stampImage.CGImage;
  [headerView_.layer addSublayer:stampLayer];
  [stampLayer release];
  
  CALayer* typeIconLayer = [[CALayer alloc] init];
  typeIconLayer.contentsGravity = kCAGravityResizeAspect;
  typeIconLayer.contents = (id)stamp_.entityObject.categoryImage.CGImage;
  typeIconLayer.frame = CGRectMake(17, 50, 15, 12);
  [headerView_.layer addSublayer:typeIconLayer];
  [typeIconLayer release];
  
  UILabel* detailLabel =
      [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMaxX(typeIconLayer.frame) + 4, 49, 258, 15)];
  detailLabel.opaque = NO;
  detailLabel.backgroundColor = [UIColor clearColor];
  detailLabel.text = stamp_.entityObject.subtitle;
  detailLabel.font = [UIFont fontWithName:@"Helvetica" size:11];
  detailLabel.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  [headerView_ addSubview:detailLabel];
  [detailLabel release];

  UITapGestureRecognizer* gestureRecognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self 
                                              action:@selector(handleEntityTap:)];
  [headerView_ addGestureRecognizer:gestureRecognizer];
  [gestureRecognizer release];
}

- (void)setUpToolbar {
  CAGradientLayer* toolbarGradient = [[CAGradientLayer alloc] init];
  toolbarGradient.colors = [NSArray arrayWithObjects:
                            (id)[UIColor colorWithWhite:1.0 alpha:1.0].CGColor,
                            (id)[UIColor colorWithWhite:0.855 alpha:1.0].CGColor, nil];
  toolbarGradient.frame = bottomToolbar_.bounds;
  [bottomToolbar_.layer addSublayer:toolbarGradient];
  [toolbarGradient release];

  bottomToolbar_.layer.shadowPath = [UIBezierPath bezierPathWithRect:bottomToolbar_.bounds].CGPath;
  bottomToolbar_.layer.shadowOpacity = 0.2;
  bottomToolbar_.layer.shadowOffset = CGSizeMake(0, -1);
  bottomToolbar_.alpha = 0.75;
}

- (void)setUpMainContentView {
  commenterImageView_.imageURL = stamp_.user.profileImageURL;
  [commenterImageView_ addTarget:self 
                          action:@selector(handleUserImageViewTap:)
                forControlEvents:UIControlEventTouchUpInside];
  const CGFloat leftPadding = CGRectGetMaxX(commenterImageView_.frame) + 10;
  CGSize stringSize = [stamp_.user.displayName sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:14]
                                                   forWidth:218
                                              lineBreakMode:UILineBreakModeTailTruncation];
  CGRect nameLabelFrame = commenterNameLabel_.frame;
  nameLabelFrame.size = stringSize;
  commenterNameLabel_.frame = nameLabelFrame;
  commenterNameLabel_.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  commenterNameLabel_.text = stamp_.user.displayName;

  stringSize = [@"stamped" sizeWithFont:[UIFont fontWithName:@"Helvetica" size:14]
                               forWidth:60
                          lineBreakMode:UILineBreakModeTailTruncation];
  CGRect stampedFrame = stampedLabel_.frame;
  stampedFrame.origin.x = CGRectGetMaxX(nameLabelFrame) + 3;
  stampedFrame.size = stringSize;
  stampedLabel_.frame = stampedFrame;
  stampedLabel_.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];

  // TODO(andybons): Use this pattern for labels.
  UILabel* commentLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  UIFont* commentFont = [UIFont fontWithName:@"Helvetica" size:14];
  commentLabel.font = commentFont;
  commentLabel.textColor = [UIColor colorWithWhite:0.2 alpha:1.0];
  commentLabel.text = stamp_.blurb;
  commentLabel.numberOfLines = 0;
  stringSize = [stamp_.blurb sizeWithFont:commentFont
                        constrainedToSize:CGSizeMake(210, MAXFLOAT)
                            lineBreakMode:commentLabel.lineBreakMode];
  commentLabel.frame = CGRectMake(leftPadding, 25, stringSize.width, stringSize.height);
  [mainCommentContainer_ addSubview:commentLabel];
  CGRect mainCommentFrame = mainCommentContainer_.frame;
  mainCommentFrame.size.height = fmaxf(kMainCommentFrameMinHeight, CGRectGetMaxY(commentLabel.frame) + 10);
  User* creditedUser = [stamp_.credits anyObject];
  if (creditedUser) {
    mainCommentFrame.size.height += 35;
    CALayer* firstStampLayer = [[CALayer alloc] init];
    firstStampLayer.contents = (id)creditedUser.stampImage.CGImage;
    firstStampLayer.frame = CGRectMake(10, CGRectGetMaxY(mainCommentFrame) - 30, 12, 12);
    [mainCommentContainer_.layer addSublayer:firstStampLayer];
    [firstStampLayer release];
    
    CALayer* secondStampLayer = [[CALayer alloc] init];
    secondStampLayer.contents = (id)stamp_.user.stampImage.CGImage;
    secondStampLayer.frame = CGRectOffset(firstStampLayer.frame, CGRectGetWidth(firstStampLayer.frame) / 2, 0);
    [mainCommentContainer_.layer addSublayer:secondStampLayer];
    [secondStampLayer release];
    
    CATextLayer* creditStringLayer = [[CATextLayer alloc] init];
    creditStringLayer.frame = CGRectMake(CGRectGetMaxX(secondStampLayer.frame) + 5,
                                         CGRectGetMinY(secondStampLayer.frame) + 1, 200, 14);
    creditStringLayer.truncationMode = kCATruncationEnd;
    creditStringLayer.contentsScale = [[UIScreen mainScreen] scale];
    creditStringLayer.fontSize = 12.0;
    creditStringLayer.foregroundColor = [UIColor stampedGrayColor].CGColor;
    CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
    CFIndex numSettings = 1;
    CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
    CTParagraphStyleSetting settings[1] = {
      {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
    };
    CTParagraphStyleRef style = CTParagraphStyleCreate(settings, numSettings);
    NSString* user = creditedUser.displayName;
    NSString* full = [NSString stringWithFormat:@"%@ %@", @"Credit to", user];
    NSMutableAttributedString* string = [[NSMutableAttributedString alloc] initWithString:full];
    [string setAttributes:[NSDictionary dictionaryWithObjectsAndKeys:
                           (id)style, (id)kCTParagraphStyleAttributeName,
                           (id)[UIColor stampedGrayColor].CGColor, (id)kCTForegroundColorAttributeName, nil]
                    range:NSMakeRange(0, full.length)];
    [string addAttribute:(NSString*)kCTFontAttributeName
                   value:(id)font 
                   range:[full rangeOfString:user]];
    CFRelease(font);
    CFRelease(style);
    creditStringLayer.string = string;
    [string release];
    [mainCommentContainer_.layer addSublayer:creditStringLayer];
    [creditStringLayer release];
  }
  mainCommentContainer_.frame = mainCommentFrame;
  mainCommentContainer_.layer.shadowPath = [UIBezierPath bezierPathWithRect:mainCommentContainer_.bounds].CGPath;
  CGRect activityFrame = activityView_.frame;
  activityFrame.size.height = CGRectGetMaxY(mainCommentContainer_.frame) + CGRectGetHeight(commentsView_.bounds) + 5;
  [commentLabel release];
  activityView_.frame = activityFrame;
  
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;

  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.view.bounds), CGRectGetMaxY(activityFrame) + kKeyboardHeight);
  activityGradientLayer_ = [[CAGradientLayer alloc] init];
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:stamp_.user.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (stamp_.user.secondaryColor) {
    [Util splitHexString:stamp_.user.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  activityGradientLayer_.colors =
      [NSArray arrayWithObjects:(id)[UIColor colorWithRed:r1 green:g1 blue:b1 alpha:0.9].CGColor,
                                (id)[UIColor colorWithRed:r2 green:g2 blue:b2 alpha:0.9].CGColor,
                                nil];
  activityGradientLayer_.frame = activityView_.bounds;
  activityGradientLayer_.startPoint = CGPointMake(0.0, 0.0);
  activityGradientLayer_.endPoint = CGPointMake(1.0, 1.0);
  [activityView_.layer insertSublayer:activityGradientLayer_ atIndex:0];
  [activityGradientLayer_ release];
}

- (void)setUpCommentsView {
  currentUserImageView_.imageURL = [AccountManager sharedManager].currentUser.profileImageURL;
}

#pragma mark - Toolbar Actions

- (IBAction)handleRestampButtonTap:(id)sender {
  CreateStampViewController* createViewController =
      [[CreateStampViewController alloc] initWithEntityObject:stamp_.entityObject
                                                   creditedTo:stamp_.user];
  [self.navigationController pushViewController:createViewController animated:YES];
  [createViewController release];
}

- (IBAction)handleTodoButtonTap:(id)sender {
  UIButton* button = sender;
  BOOL shouldDelete = button.selected;
  [button setSelected:!shouldDelete];
  NSString* path = shouldDelete ? kRemoveFavoritePath : kCreateFavoritePath;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* favoriteMapping = [objectManager.mappingProvider mappingForKeyPath:@"Favorite"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:path delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = favoriteMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
      [AccountManager sharedManager].authToken.accessToken, @"oauth_token",
      stamp_.entityObject.entityID, @"entity_id", nil];

  [objectLoader send];
}

- (IBAction)handleSendButtonTap:(id)sender {
  
}

#pragma mark -

- (void)preloadEntityView {
  if (detailViewController_)
    return;

  switch (stamp_.entityObject.entityCategory) {
    case EntityCategoryFood:
      detailViewController_ = [[PlaceDetailViewController alloc] initWithEntityObject:stamp_.entityObject];
      break;
    default:
      detailViewController_ = [[GenericItemDetailViewController alloc] initWithEntityObject:stamp_.entityObject];
      break;
  }
}

- (void)handleTap:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  [addCommentField_ resignFirstResponder];
}

- (void)handleEntityTap:(UITapGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  [addCommentField_ resignFirstResponder];
  // Pass the selected object to the new view controller.
  [self.navigationController pushViewController:detailViewController_ animated:YES];
}

- (void)handleUserImageViewTap:(id)sender {
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = stamp_.user;
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

- (void)handleCommentUserImageViewTap:(NSNotification*)notification {
  StampDetailCommentView* commentView = notification.object;
  ProfileViewController* profileViewController = [[ProfileViewController alloc] initWithNibName:@"ProfileViewController" bundle:nil];
  profileViewController.user = commentView.comment.user;
  [self.navigationController pushViewController:profileViewController animated:YES];
  [profileViewController release];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Comments.

- (void)loadCommentsFromServer {
  if (![[RKClient sharedClient] isNetworkAvailable])
    return;

  addCommentField_.hidden = YES;
  currentUserImageView_.hidden = YES;
  [loadingView_ startAnimating];
  
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* commentMapping = [objectManager.mappingProvider mappingForKeyPath:@"Comment"];
  NSString* resourcePath = [@"/comments/show.json" appendQueryParams:[NSDictionary dictionaryWithObjectsAndKeys:stamp_.stampID, @"stamp_id",
          [AccountManager sharedManager].authToken.accessToken, @"oauth_token", nil]];
  [objectManager loadObjectsAtResourcePath:resourcePath
                             objectMapping:commentMapping
                                  delegate:self];
}

- (void)renderComments {
  NSArray* sortDescriptors = [NSArray arrayWithObject:[NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES]];
  for (Comment* c in [stamp_.comments sortedArrayUsingDescriptors:sortDescriptors])
    [self addComment:c];
}

- (void)addComment:(Comment*)comment {
  StampDetailCommentView* commentView = [[StampDetailCommentView alloc] initWithComment:comment];

  CGRect frame = commentView.frame;
  CGFloat yPos = 0.0;
  frame.size.width = CGRectGetWidth(activityView_.frame);
  for (UIView* view in commentsView_.subviews) {
    if ([view isKindOfClass:[StampDetailCommentView class]])
      yPos += CGRectGetHeight(view.frame);
  }
  frame.origin.y = yPos;
  commentView.frame = frame;
  [commentsView_ addSubview:commentView];
  [commentView release];

  frame = commentsView_.frame;
  frame.size.height += CGRectGetHeight(commentView.frame);
  frame.origin.y -= CGRectGetHeight(commentView.frame);
  commentsView_.frame = frame;

  frame = activityView_.frame;
  frame.size.height += CGRectGetHeight(commentView.frame);
  activityView_.frame = frame;
  activityGradientLayer_.frame = activityView_.bounds;
  [activityGradientLayer_ setNeedsDisplay];
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.view.bounds), CGRectGetMaxY(activityView_.frame) + 60);
}

#pragma mark - UITextFieldDelegate Methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [UIView animateWithDuration:0.2 animations:^{
    scrollView_.contentInset = UIEdgeInsetsMake(0, 0, kKeyboardHeight - 60, 0);
    scrollView_.contentOffset = CGPointMake(0, CGRectGetMaxY(activityView_.frame) - (CGRectGetHeight(scrollView_.frame) - kKeyboardHeight));
  }];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  [UIView animateWithDuration:0.2 animations:^{
    scrollView_.contentInset = UIEdgeInsetsZero;
  }];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != addCommentField_)
    return YES;

  addCommentField_.hidden = YES;
  currentUserImageView_.hidden = YES;
  [loadingView_ startAnimating];
  [addCommentField_ resignFirstResponder];
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* commentMapping = [objectManager.mappingProvider mappingForKeyPath:@"Comment"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kCreateCommentPath delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = commentMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
      addCommentField_.text, @"blurb",
      [AccountManager sharedManager].authToken.accessToken, @"oauth_token",
      stamp_.stampID, @"stamp_id", nil];
  [objectLoader send];
 
  return NO;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
  if ([objectLoader.resourcePath isEqualToString:kCreateFavoritePath]) {
    [[NSNotificationCenter defaultCenter] postNotificationName:kFavoriteHasChangedNotification 
                                                        object:nil];
    return;
  }

  if ([objectLoader.resourcePath isEqualToString:kRemoveFavoritePath]) {
    NSLog(@"%@", objectLoader.response.bodyAsString);
    Favorite* fav = [objects lastObject];
    [fav deleteEntity];
    [[NSNotificationCenter defaultCenter] postNotificationName:kFavoriteHasChangedNotification 
                                                        object:nil];
    return;
  }
  
  [loadingView_ stopAnimating];
  addCommentField_.hidden = NO;
  currentUserImageView_.hidden = NO;

	if ([objectLoader.resourcePath isEqualToString:kCreateCommentPath]) {
    Comment* comment = [objects objectAtIndex:0];
    [self addComment:comment];
    [stamp_ addCommentsObject:comment];
    stamp_.numComments = [NSNumber numberWithInt:[stamp_.numComments intValue] + 1];
    [[NSNotificationCenter defaultCenter] postNotificationName:kStampDidChangeNotification
                                                        object:stamp_];
    
    addCommentField_.text = nil;
    return;
  }
  stamp_.comments = [NSSet setWithArray:objects];
  [self renderComments];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
	NSLog(@"Hit error: %@", error);
  if ([objectLoader.response isUnauthorized])
    [[AccountManager sharedManager] refreshToken];

  if ([objectLoader.resourcePath isEqualToString:kCreateFavoritePath] ||
      [objectLoader.resourcePath isEqualToString:kRemoveFavoritePath]) {
    NSLog(@"%@", objectLoader.response.bodyAsString);
    return;
  }

  [loadingView_ stopAnimating];
  addCommentField_.hidden = NO;
  currentUserImageView_.hidden = NO;
  [addCommentField_ becomeFirstResponder];
}

@end
