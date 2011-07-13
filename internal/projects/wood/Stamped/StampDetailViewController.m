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

#import "EntityDetailViewController.h"
#import "FilmDetailViewController.h"
#import "PlaceDetailViewController.h"
#import "BookDetailViewController.h"
#import "MusicDetailViewController.h"
#import "StampEntity.h"
#import "StampedAppDelegate.h"
#import "UserImageView.h"

@interface StampDetailViewController ()
- (void)setUpHeader;
- (void)setUpToolbarAndBackground;
- (void)setUpMainContentView;
- (void)setUpCommentsView;
- (void)handleTap:(UITapGestureRecognizer*)sender;
- (void)handleEntityTap:(UITapGestureRecognizer*)sender;
@end

@implementation StampDetailViewController

@synthesize topHeaderCell = topHeaderCell_;
@synthesize scrollView = scrollView_;
@synthesize addCommentField = addCommentField_;
@synthesize commentsView = commentsView_;
@synthesize activityView = activityView_;
@synthesize bottomToolbar = bottomToolbar_;

- (id)initWithEntity:(StampEntity*)entity {
  self = [self initWithNibName:@"StampDetailViewController" bundle:nil];
  if (self) {
    entity_ = [entity retain];
  }
  return self;
}

- (void)dealloc {
  [entity_ release];

  self.topHeaderCell = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.scrollView = nil;
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
  UITapGestureRecognizer* gestureRecognizer =
      [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
  [self.view addGestureRecognizer:gestureRecognizer];
  [gestureRecognizer release];

  scrollView_.contentSize = self.view.bounds.size;
  
  [self setUpToolbarAndBackground];
  [self setUpHeader];

  activityView_.layer.shadowOpacity = 0.1;
  activityView_.layer.shadowOffset = CGSizeMake(0, 1);
  activityView_.layer.shadowRadius = 2;
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;

  [self setUpMainContentView];
  [self setUpCommentsView];
}

- (void)setUpHeader {
  NSString* fontString = @"TitlingGothicFBComp-Regular";
  CGFloat fontSize = 36.0;
  CGSize stringSize = [entity_.name sizeWithFont:[UIFont fontWithName:fontString size:fontSize]
                                        forWidth:280
                                   lineBreakMode:UILineBreakModeTailTruncation];
  
  UILabel* nameLabel = [[UILabel alloc] initWithFrame:CGRectMake(15, 11, stringSize.width, stringSize.height)];
  nameLabel.font = [UIFont fontWithName:fontString size:fontSize];
  nameLabel.text = entity_.name;
  nameLabel.textColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  nameLabel.backgroundColor = [UIColor clearColor];
  
  // Badge stamp.
  CALayer* stampLayer = [[CALayer alloc] init];
  stampLayer.frame = CGRectMake(15 + stringSize.width - (46 / 2),
                                11 - (46 / 2),
                                46, 46);
  stampLayer.contents = (id)entity_.stampImage.CGImage;
  
  [topHeaderCell_.contentView.layer addSublayer:stampLayer];
  [topHeaderCell_.contentView addSubview:nameLabel];
  [stampLayer release];
  [nameLabel release];
  
  CALayer* typeIconLayer = [[CALayer alloc] init];
  typeIconLayer.contentsGravity = kCAGravityResizeAspect;
  typeIconLayer.contents = (id)entity_.categoryImage.CGImage;
  typeIconLayer.frame = CGRectMake(15, 48, 12, 12);
  [topHeaderCell_.layer addSublayer:typeIconLayer];
  [typeIconLayer release];
  
  UILabel* detailLabel =
  [[UILabel alloc] initWithFrame:CGRectMake(CGRectGetMaxX(typeIconLayer.frame) + 3, 48, 258, 15)];
  detailLabel.opaque = NO;
  detailLabel.backgroundColor = [UIColor clearColor];
  detailLabel.text = entity_.detail;
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
  UserImageView* userImgView = [[UserImageView alloc] initWithFrame:CGRectMake(10, 10, 55, 55)];
  userImgView.image = entity_.userImage;
  [activityView_ addSubview:userImgView];
  [userImgView release];

  const CGFloat leftPadding = CGRectGetMaxX(userImgView.frame) + 10;
  NSString* fontString = @"Helvetica-Bold";
  CGSize stringSize = [entity_.userName sizeWithFont:[UIFont fontWithName:fontString size:14]
                                            forWidth:218
                                       lineBreakMode:UILineBreakModeTailTruncation];
  
  UILabel* userNameLabel = [[UILabel alloc] initWithFrame:CGRectMake(
      leftPadding, 10, stringSize.width, stringSize.height)];
  userNameLabel.font = [UIFont fontWithName:fontString size:14];
  userNameLabel.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  userNameLabel.text = entity_.userName;
  [activityView_ addSubview:userNameLabel];
  [userNameLabel release];

  // TODO(andybons): Ripe for caching.
  fontString = @"HelveticaNeue";
  stringSize = [@"stamped" sizeWithFont:[UIFont fontWithName:fontString size:14]
                               forWidth:218  // TODO(andybons) right width, here.
                          lineBreakMode:UILineBreakModeTailTruncation];
  UILabel* stampedLabel = [[UILabel alloc] initWithFrame:CGRectMake(
      CGRectGetMaxX(userNameLabel.frame) + 2, 10, stringSize.width, stringSize.height)];
  stampedLabel.font = [UIFont fontWithName:fontString size:14];
  stampedLabel.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  stampedLabel.text = @"stamped";
  [activityView_ addSubview:stampedLabel];
  [stampedLabel release];

  if (!entity_.comment)
    return;

  // TODO(andybons): Use this pattern for labels.
  UILabel* commentLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  UIFont* commentFont = [UIFont fontWithName:@"HelveticaNeue" size:14];
  commentLabel.font = commentFont;
  commentLabel.textColor = [UIColor colorWithWhite:0.2 alpha:1.0];
  commentLabel.text = entity_.comment;
  commentLabel.numberOfLines = 2;
  stringSize = [entity_.comment sizeWithFont:commentFont
                           constrainedToSize:CGSizeMake(210, 40) 
                               lineBreakMode:commentLabel.lineBreakMode];
  commentLabel.frame = CGRectMake(leftPadding, 29, stringSize.width, stringSize.height);
  [activityView_ addSubview:commentLabel];
  [commentLabel release];
}

- (void)setUpCommentsView {
  UserImageView* userImgView = [[UserImageView alloc] initWithFrame:CGRectMake(10, 10, 31, 31)];
  userImgView.image = [UIImage imageNamed:@"robby_s_user_image"];
  [commentsView_ addSubview:userImgView];
  [userImgView release];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.topHeaderCell = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.scrollView = nil;
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
  switch (entity_.type) {
    case StampEntityTypePlace:
      detailViewController = [[PlaceDetailViewController alloc] initWithNibName:@"PlaceDetailViewController" entity:entity_];
      break;
    case StampEntityTypeBook:
      detailViewController = [[BookDetailViewController alloc] initWithNibName:@"BookDetailViewController" entity:entity_];
      break;
    case StampEntityTypeMusic:
      detailViewController = [[MusicDetailViewController alloc] initWithNibName:@"MusicDetailViewController" entity:entity_];
      break;
    case StampEntityTypeFilm:
      detailViewController = [[FilmDetailViewController alloc] initWithNibName:@"FilmDetailViewController" entity:entity_];
      break;
    default:
      detailViewController = [[EntityDetailViewController alloc] initWithNibName:@"EntityDetailViewController" entity:entity_];
      break;
  }
  // Pass the selected object to the new view controller.
  StampedAppDelegate* delegate = [[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
