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

#import "EntityDetailViewController.h"
#import "Comment.h"
#import "FilmDetailViewController.h"
#import "PlaceDetailViewController.h"
#import "BookDetailViewController.h"
#import "MusicDetailViewController.h"
#import "Entity.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "StampedAppDelegate.h"
#import "StampDetailCommentView.h"
#import "UserImageView.h"

static const CGFloat kMainCommentFrameMinHeight = 75.0;
static const CGFloat kKeyboardHeight = 216.0;

@interface StampDetailViewController ()
- (void)setUpHeader;
- (void)setUpToolbarAndBackground;
- (void)setUpMainContentView;
- (void)setUpCommentsView;
- (void)handleTap:(UITapGestureRecognizer*)sender;
- (void)handleEntityTap:(UITapGestureRecognizer*)sender;
- (void)renderComments;
- (void)addComment:(Comment*)comment;
- (void)loadCommentsFromServer;
- (void)loadCommentsFromDataStore;
@end

@implementation StampDetailViewController

@synthesize topHeaderCell = topHeaderCell_;
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

@synthesize commentsArray = commentsArray_;

- (id)initWithStamp:(Stamp*)stamp {
  self = [self initWithNibName:@"StampDetailViewController" bundle:nil];
  if (self) {
    stamp_ = [stamp retain];
  }
  return self;
}

- (void)dealloc {
  [stamp_ release];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.commentsArray = nil;
  self.topHeaderCell = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.mainCommentContainer = nil;
  self.scrollView = nil;
  self.currentUserImageView = nil;
  self.commenterImageView = nil;
  self.commenterNameLabel = nil;
  self.stampedLabel = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewWillDisappear:(BOOL)animated {
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  UITapGestureRecognizer* gestureRecognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
  [self.activityView addGestureRecognizer:gestureRecognizer];
  [gestureRecognizer release];

  scrollView_.contentSize = self.view.bounds.size;
  
  [self setUpToolbarAndBackground];
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
  
  [self setUpMainContentView];
  [self setUpCommentsView];
  
  //[self loadCommentsFromDataStore];
  [self loadCommentsFromServer];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [[RKRequestQueue sharedQueue] cancelRequestsWithDelegate:self];
  self.commentsArray = nil;
  self.topHeaderCell = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.mainCommentContainer = nil;
  self.scrollView = nil;
  self.currentUserImageView = nil;
  self.commenterImageView = nil;
  self.commenterNameLabel = nil;
  self.stampedLabel = nil;
}

- (void)setUpHeader {
  NSString* fontString = @"TitlingGothicFBComp-Regular";
  CGFloat fontSize = 36.0;
  CGSize stringSize = [stamp_.entityObject.title sizeWithFont:[UIFont fontWithName:fontString size:fontSize]
                                                     forWidth:280
                                                lineBreakMode:UILineBreakModeTailTruncation];
  
  UILabel* nameLabel = [[UILabel alloc] initWithFrame:CGRectMake(15, 11, stringSize.width, stringSize.height)];
  nameLabel.font = [UIFont fontWithName:fontString size:fontSize];
  nameLabel.text = stamp_.entityObject.title;
  nameLabel.textColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  nameLabel.backgroundColor = [UIColor clearColor];
  
  // Badge stamp.
  CALayer* stampLayer = [[CALayer alloc] init];
  stampLayer.frame = CGRectMake(15 + stringSize.width - (46 / 2),
                                11 - (46 / 2),
                                46, 46);
  stampLayer.contents = (id)stamp_.user.stampImage.CGImage;
  
  [topHeaderCell_.contentView.layer addSublayer:stampLayer];
  [topHeaderCell_.contentView addSubview:nameLabel];
  [stampLayer release];
  [nameLabel release];
  
  CALayer* typeIconLayer = [[CALayer alloc] init];
  typeIconLayer.contentsGravity = kCAGravityResizeAspect;
  typeIconLayer.contents = (id)stamp_.entityObject.categoryImage.CGImage;
  typeIconLayer.frame = CGRectMake(15, 48, 12, 12);
  [topHeaderCell_.layer addSublayer:typeIconLayer];
  [typeIconLayer release];
  
  UILabel* detailLabel =
      [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMaxX(typeIconLayer.frame) + 3, 48, 258, 15)];
  detailLabel.opaque = NO;
  detailLabel.backgroundColor = [UIColor clearColor];
  detailLabel.text = stamp_.entityObject.subtitle;
  detailLabel.font = [UIFont fontWithName:@"HelveticaNeue" size:11];
  detailLabel.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  [topHeaderCell_ addSubview:detailLabel];
  [detailLabel release];

  UITapGestureRecognizer* gestureRecognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self 
                                              action:@selector(handleEntityTap:)];
  [topHeaderCell_ addGestureRecognizer:gestureRecognizer];
  [gestureRecognizer release];
}

- (void)setUpToolbarAndBackground {
  CAGradientLayer* toolbarGradient = [[CAGradientLayer alloc] init];
  toolbarGradient.colors = [NSArray arrayWithObjects:
                            (id)[UIColor colorWithWhite:1.0 alpha:1.0].CGColor,
                            (id)[UIColor colorWithWhite:0.855 alpha:1.0].CGColor, nil];
  toolbarGradient.frame = bottomToolbar_.bounds;
  [bottomToolbar_.layer addSublayer:toolbarGradient];
  [toolbarGradient release];
  CAGradientLayer* backgroundGradient = [[CAGradientLayer alloc] init];
  backgroundGradient.colors = [NSArray arrayWithObjects:
                               (id)[UIColor colorWithWhite:1.0 alpha:1.0].CGColor,
                               (id)[UIColor colorWithWhite:0.93 alpha:1.0].CGColor, nil];
  backgroundGradient.frame = self.view.bounds;
  [self.view.layer insertSublayer:backgroundGradient atIndex:0];
  [backgroundGradient release];
  bottomToolbar_.layer.shadowPath = [UIBezierPath bezierPathWithRect:bottomToolbar_.bounds].CGPath;
  bottomToolbar_.layer.shadowOpacity = 0.2;
  bottomToolbar_.layer.shadowOffset = CGSizeMake(0, -1);
  bottomToolbar_.alpha = 0.5;
}

- (void)setUpMainContentView {
  commenterImageView_.image = stamp_.user.profileImage;

  const CGFloat leftPadding = CGRectGetMaxX(commenterImageView_.frame) + 10;
  CGSize stringSize = [stamp_.user.displayName sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:14]
                                                   forWidth:218
                                              lineBreakMode:UILineBreakModeTailTruncation];
  CGRect nameLabelFrame = commenterNameLabel_.frame;
  nameLabelFrame.size = stringSize;
  commenterNameLabel_.frame = nameLabelFrame;
  commenterNameLabel_.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  commenterNameLabel_.text = stamp_.user.displayName;

  stringSize = [@"stamped" sizeWithFont:[UIFont fontWithName:@"HelveticaNeue" size:14]
                               forWidth:60
                          lineBreakMode:UILineBreakModeTailTruncation];
  CGRect stampedFrame = stampedLabel_.frame;
  stampedFrame.origin.x = CGRectGetMaxX(nameLabelFrame) + 3;
  stampedFrame.size = stringSize;
  stampedLabel_.frame = stampedFrame;
  stampedLabel_.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];

  // TODO(andybons): Use this pattern for labels.
  UILabel* commentLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  UIFont* commentFont = [UIFont fontWithName:@"HelveticaNeue" size:14];
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
  mainCommentContainer_.frame = mainCommentFrame;
  mainCommentContainer_.layer.shadowPath = [UIBezierPath bezierPathWithRect:mainCommentContainer_.bounds].CGPath;
  CGRect activityFrame = activityView_.frame;
  activityFrame.size.height = CGRectGetMaxY(mainCommentContainer_.frame) + CGRectGetHeight(commentsView_.bounds) + 5;
  [commentLabel release];
  activityView_.frame = activityFrame;
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.view.bounds), CGRectGetMaxY(activityFrame) + kKeyboardHeight);
  CAGradientLayer* gradientLayer = [[CAGradientLayer alloc] init];
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:stamp_.user.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (stamp_.user.secondaryColor) {
    [Util splitHexString:stamp_.user.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  gradientLayer.colors = [NSArray arrayWithObjects:(id)[UIColor colorWithRed:r1 green:g1 blue:b1 alpha:0.75].CGColor,
                                                   (id)[UIColor colorWithRed:r2 green:g2 blue:b2 alpha:0.75].CGColor,
                                                   nil];
  gradientLayer.frame = activityView_.bounds;
  gradientLayer.startPoint = CGPointMake(0.0, 0.0);
  gradientLayer.endPoint = CGPointMake(1.0, 1.0);
  [activityView_.layer insertSublayer:gradientLayer atIndex:0];
  [gradientLayer release];
}

- (void)setUpCommentsView {
  currentUserImageView_.image = [UIImage imageNamed:@"robby_s_user_image"];
}

- (IBAction)handleCommentButtonTap:(id)sender {
  [addCommentField_ becomeFirstResponder];
}

- (void)handleTap:(UITapGestureRecognizer*)sender {
  if (sender.state != UIGestureRecognizerStateEnded)
    return;

  [addCommentField_ resignFirstResponder];
}

- (void)handleEntityTap:(UITapGestureRecognizer*)sender {
  if (sender.state != UIGestureRecognizerStateEnded)
    return;

  [addCommentField_ resignFirstResponder];
  EntityDetailViewController* detailViewController = nil;
  switch (stamp_.category) {
    case StampCategoryPlace:
      detailViewController = [[PlaceDetailViewController alloc] initWithNibName:@"PlaceDetailViewController" stamp:stamp_];
      break;
    case StampCategoryBook:
      detailViewController = [[BookDetailViewController alloc] initWithNibName:@"BookDetailViewController" stamp:stamp_];
      break;
    case StampCategoryMusic:
      detailViewController = [[MusicDetailViewController alloc] initWithNibName:@"MusicDetailViewController" stamp:stamp_];
      break;
    case StampCategoryFilm:
      detailViewController = [[FilmDetailViewController alloc] initWithNibName:@"FilmDetailViewController" stamp:stamp_];
      break;
    default:
      detailViewController = [[EntityDetailViewController alloc] initWithNibName:@"EntityDetailViewController" stamp:stamp_];
      break;
  }
  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Comments.

- (void)loadCommentsFromServer {
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* commentMapping = [objectManager.mappingProvider objectMappingForKeyPath:@"Comment"];
  NSString* resourcePath = [NSString stringWithFormat:@"/comments/show.json?stamp_id=%@&authenticated_user_id=%@",
      stamp_.stampID, @"4e28ef4c6da2353e50000006"];
  [objectManager loadObjectsAtResourcePath:resourcePath
                             objectMapping:commentMapping
                                  delegate:self];
}

- (void)loadCommentsFromDataStore {
  /*self.commentsArray = nil;
  NSFetchRequest* request = [Comment fetchRequest];
	NSSortDescriptor* descriptor = [NSSortDescriptor sortDescriptorWithKey:@"lastModified" ascending:YES];
	[request setSortDescriptors:[NSArray arrayWithObject:descriptor]];
	self.commentsArray = [Comment objectsWithFetchRequest:request];
*/

}

- (void)renderComments {
  for (Comment* c in self.commentsArray) {
    [self addComment:c];
  }
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
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.view.bounds), CGRectGetMaxY(activityView_.frame) + kKeyboardHeight);
}

#pragma mark - UITextFieldDelegate Methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  [scrollView_ setContentOffset:CGPointMake(0, CGRectGetMaxY(activityView_.frame) - (CGRectGetHeight(scrollView_.frame) - kKeyboardHeight))
                       animated:YES];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != addCommentField_)
    return YES;

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* commentMapping = [objectManager.mappingProvider objectMappingForKeyPath:@"Comment"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:@"/comments/create.json" delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = commentMapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
      addCommentField_.text, @"blurb",
      @"4e28ef4c6da2353e50000006", @"authenticated_user_id",
      stamp_.stampID, @"stamp_id", nil];
  [objectLoader send];
  return NO;
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	if ([objectLoader.resourcePath isEqualToString:@"/comments/create.json"]) {
    [self addComment:[objects objectAtIndex:0]];
    addCommentField_.text = nil;
    [addCommentField_ resignFirstResponder];
    return;
  }

  self.commentsArray = nil;
  self.commentsArray = objects;
  [self renderComments];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  [addCommentField_ becomeFirstResponder];
  UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Error"
                                                   message:[error localizedDescription] 
                                                  delegate:nil 
                                         cancelButtonTitle:@"OK" otherButtonTitles:nil] autorelease];
	[alert show];
	NSLog(@"Hit error: %@", error);
}

@end
