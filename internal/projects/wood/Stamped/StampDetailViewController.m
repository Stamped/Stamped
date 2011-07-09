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

#import "StampEntity.h"

@interface StampDetailViewController ()
- (void)setUpHeader;
- (void)setUpToolbarAndBackground;
- (void)setUpActivityView;
@end

@implementation StampDetailViewController

@synthesize topHeaderCell = topHeaderCell_;
@synthesize scrollView = scrollView_;
@synthesize activityView = activityView_;
@synthesize bottomToolbar = bottomToolbar_;

- (id)initWithEntity:(StampEntity*)entity {
  self = [self initWithNibName:@"StampDetailViewController" bundle:nil];
  if (self) {
    entity_ = entity;
    scrollView_.contentSize = self.view.bounds.size;
  }
  return self;
}

- (void)dealloc {
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
  [self setUpToolbarAndBackground];
  [self setUpHeader];
  [self setUpActivityView];
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

- (void)setUpActivityView {
  activityView_.layer.shadowOpacity = 0.1;
  activityView_.layer.shadowOffset = CGSizeMake(0, 1);
  activityView_.layer.shadowRadius = 2;
  activityView_.layer.shadowPath = [UIBezierPath bezierPathWithRect:activityView_.bounds].CGPath;

  CALayer* userImgLayer = [[CALayer alloc] init];
  userImgLayer.contents = (id)entity_.userImage.CGImage;
  userImgLayer.contentsGravity = kCAGravityResizeAspect;
  userImgLayer.frame = CGRectMake(10, 10, 55, 55);
  userImgLayer.borderColor = [UIColor whiteColor].CGColor;
  userImgLayer.borderWidth = 2.0;
  userImgLayer.shadowOpacity = 0.5;
  userImgLayer.shadowOffset = CGSizeMake(0, 0.5);
  userImgLayer.shadowRadius = 1.0;
  userImgLayer.shadowPath = [UIBezierPath bezierPathWithRect:userImgLayer.bounds].CGPath;
  [activityView_.layer addSublayer:userImgLayer];
  [userImgLayer release];
  
  const CGFloat leftPadding = CGRectGetMaxX(userImgLayer.frame) + 10;
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

- (void)viewDidUnload {
  [super viewDidUnload];
  self.topHeaderCell = nil;
  self.bottomToolbar = nil;
  self.activityView = nil;
  self.scrollView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
