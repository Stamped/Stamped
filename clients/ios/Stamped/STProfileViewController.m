//
//  STProfileViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STProfileViewController.h"
#import "STStampedAPI.h"
#import "STLegacyStampCell.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STUserSource.h"
#import <QuartzCore/QuartzCore.h>
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STButton.h"
#import "STUsersViewController.h"
#import "STPhotoViewController.h"
#import "STProfileSource.h"

@interface STProfileViewController ()

- (void)commonSetup;

@property (nonatomic, readonly, retain) NSString* userID;
@property (nonatomic, readwrite, retain) id<STUserDetail> userDetail;
@property (nonatomic, readwrite, retain) STProfileSource* source;
@property (nonatomic, readwrite, retain) UIView* header;

@end

@implementation STProfileViewController

@synthesize userID = userID_;
@synthesize userDetail = userDetail_;
@synthesize source = source_;
@synthesize header = header_;

static const NSInteger _headerHeight = 95;

- (id)initWithUserID:(NSString*)userID 
{
  self = [super initWithHeaderHeight:_headerHeight];
  if (self) {
    userID_ = [userID retain];
  }
  return self;
}

- (void)dealloc
{
  [source_ release];
  [userDetail_ release];
  [userID_ release];
  [header_ release];
  [super dealloc];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  [self reloadStampedData];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  self.header = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self.source resumeOperations];
}

- (void)cancelPendingRequests {
  [self.source cancelPendingOperations];
}

- (void)setSource:(STProfileSource *)source {
  source_.table = nil;
  [source_ release];
  source_ = [source retain];
  source_.table = self.tableView;
}

- (void)followButtonClicked:(id)button {
  [[STStampedAPI sharedInstance] addFriendForUserID:self.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
    if (userDetail) {
      [self reloadStampedData];
    }
  }];
}

- (void)unfollowButtonClicked:(id)button {
  [[STStampedAPI sharedInstance] removeFriendForUserID:self.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
    if (userDetail) {
      [self reloadStampedData];
    }
  }];
}

- (void)reloadStampedData {
  self.userDetail = nil;
  [[STStampedAPI sharedInstance] userDetailForUserID:self.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
    if (userDetail) {
      self.userDetail = userDetail;
      [self commonSetup];
      STProfileSource* source = [[[STProfileSource alloc] initWithUserDetail:userDetail] autorelease];
      self.source = source;
      [[STStampedAPI sharedInstance] isFriendForUserID:userDetail.userID andCallback:^(BOOL isFriend, NSError *error) {
        NSString* string;
        SEL action;
        if (isFriend) {
          string = @"Unfollow";
          action = @selector(unfollowButtonClicked:);
        }
        else {
          string = @"Follow";
          action = @selector(followButtonClicked:);
        }
        UIBarButtonItem* rightButton = [[[UIBarButtonItem alloc] initWithTitle:string
                                                                        style:UIBarButtonItemStylePlain
                                                                       target:self
                                                                       action:action] autorelease];
        self.navigationItem.rightBarButtonItem = rightButton;
      }];
    }
  }];
}

- (void)commonSetup {
  [self.header removeFromSuperview];
  self.header = [[[UIView alloc] initWithFrame:CGRectMake(0, self.headerOffset, self.scrollView.frame.size.width, _headerHeight)] autorelease];
  CGFloat padding = 10;
  CGFloat imageOffset = padding;
  UIView* userImage = [Util profileImageViewForUser:self.userDetail withSize:STProfileImageSize72];
  [Util reframeView:userImage withDeltas:CGRectMake(imageOffset, imageOffset, 0, 0)];
  [self.header addSubview:userImage];
  UIView* imageButtom = [Util tapViewWithFrame:userImage.frame target:self selector:@selector(userImageTapped:) andMessage:nil];
  [self.header addSubview:imageButtom];
  
  
  UIImage* stampImage = [Util stampImageForUser:self.userDetail withSize:STStampImageSize60];
  UIImageView* stampImageView = [[[UIImageView alloc] initWithImage:stampImage] autorelease];
  [Util reframeView:stampImageView withDeltas:CGRectMake(CGRectGetMaxX(userImage.frame) - 34,
                                                         CGRectGetMinY(userImage.frame) - 20,
                                                         0, 
                                                         0)];
  [self.header addSubview:stampImageView];
  
  CGFloat textOffset = CGRectGetMaxX(userImage.frame) + imageOffset + 5;
  CGFloat textMaxWidth = self.header.frame.size.width - padding - textOffset;
  UILabel* nameView = [Util viewWithText:self.userDetail.name
                                    font:[UIFont stampedBoldFontWithSize:18]
                                   color:[UIColor stampedDarkGrayColor]
                                    mode:UILineBreakModeTailTruncation
                              andMaxSize:CGSizeMake(textMaxWidth, CGFLOAT_MAX)];
  [Util reframeView:nameView withDeltas:CGRectMake(textOffset, CGRectGetMinY(userImage.frame), 0, 0)];
  [self.header addSubview:nameView];
  UILabel* screenName = [Util viewWithText:self.userDetail.screenName
                                      font:[UIFont stampedFontWithSize:14]
                                     color:[UIColor stampedGrayColor]
                                      mode:UILineBreakModeTailTruncation
                                andMaxSize:CGSizeMake(textMaxWidth, CGFLOAT_MAX)];
  [Util reframeView:screenName withDeltas:CGRectMake(textOffset, CGRectGetMaxY(nameView.frame), 0, 0)];
  [self.header addSubview:screenName];
  
  if (self.userDetail.bio) {
    UIView* bioView = [Util viewWithText:self.userDetail.bio
                                    font:[UIFont stampedFontWithSize:12]
                                   color:[UIColor stampedGrayColor]
                                    mode:UILineBreakModeWordWrap
                              andMaxSize:CGSizeMake(textMaxWidth, 20)];
    [Util reframeView:bioView withDeltas:CGRectMake(textOffset, CGRectGetMaxY(screenName.frame), 0, 0)];
    [self.header addSubview:bioView];
  }
    self.header.backgroundColor = [UIColor whiteColor];
    self.header.layer.shadowColor = [UIColor blackColor].CGColor;
    self.header.layer.shadowOpacity = .5;
    self.header.layer.shadowRadius = 2;
    self.header.layer.shadowOffset = CGSizeMake(0, 2);
    self.header.layer.shadowPath = [UIBezierPath bezierPathWithRect:self.header.bounds].CGPath;
    [self.scrollView addSubview:self.header];
}

- (void)userImageTapped:(id)sender {
    STPhotoViewController *controller = [[STPhotoViewController alloc] initWithURL:[NSURL URLWithString:[Util largeProfileImageURLWithUser:self.userDetail]]];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
    [controller release];
}

@end
