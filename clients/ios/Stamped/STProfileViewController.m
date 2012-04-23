//
//  STProfileViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STProfileViewController.h"
#import "STStampedAPI.h"
#import "STStampCell.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STUserSource.h"
#import <QuartzCore/QuartzCore.h>
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STButton.h"

@interface STProfileViewController ()

- (void)commonSetup;
- (void)creditsButtonPressed:(id)button;
- (void)followersButtonPressed:(id)button;
- (void)friendsButtonPressed:(id)button;

@property (nonatomic, readonly, retain) NSString* userID;
@property (nonatomic, readwrite, retain) id<STUserDetail> userDetail;
@property (nonatomic, readwrite, retain) STUserSource* source;
@property (nonatomic, readwrite, retain) UIView* header;

@end

@implementation STProfileViewController

@synthesize userID = userID_;
@synthesize userDetail = userDetail_;
@synthesize source = source_;
@synthesize header = header_;

static const NSInteger _headerHeight = 135;

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
  self.tableView.rowHeight = 96;
  [self reloadStampedData];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  self.header = nil;
}

- (void)setSource:(STUserSource *)source {
  source_.table = nil;
  [source_ release];
  source_ = [source retain];
  source_.table = self.tableView;
}

- (void)reloadStampedData {
  self.userDetail = nil;
  [[STStampedAPI sharedInstance] userDetailForUserID:self.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
    if (userDetail) {
      self.userDetail = userDetail;
      [self commonSetup];
      STGenericCollectionSlice* slice = [[[STGenericCollectionSlice alloc] init] autorelease];
      slice.offset = [NSNumber numberWithInt:0];
      slice.limit = [NSNumber numberWithInt:NSIntegerMax];
      slice.sort = @"created";
      STUserSource* source = [[[STUserSource alloc] init] autorelease];
      source.user = self.userDetail;
      source.slice = slice;
      self.source = source;
    }
  }];
}

- (void)commonSetup {
  [self.header removeFromSuperview];
  self.header = [[[UIView alloc] initWithFrame:CGRectMake(0, self.headerOffset, self.scrollView.frame.size.width, _headerHeight)] autorelease];
  CGFloat padding = 10;
  CGFloat contentWidth = self.header.frame.size.width - ( 2 * padding );
  CGFloat imageOffset = padding;
  UIView* userImage = [Util profileImageViewForUser:self.userDetail withSize:STProfileImageSize72];
  [Util reframeView:userImage withDeltas:CGRectMake(imageOffset, imageOffset, 0, 0)];
  [self.header addSubview:userImage];
  
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
                              andMaxSize:CGSizeMake(textMaxWidth, 60)];
    [Util reframeView:bioView withDeltas:CGRectMake(textOffset, CGRectGetMaxY(screenName.frame), 0, 0)];
    [self.header addSubview:bioView];
  }
  
  CGRect buttonFrame = CGRectMake(0, 0, (contentWidth - 20) / 3, 35);
  NSMutableArray* buttons = [NSMutableArray array];
  for (NSInteger i = 0; i < 3; i++) {
    UIView* views[2];
    NSInteger count;
    NSString* subtitle;
    SEL selector;
    if (i == 0) {
      //credits
      count = self.userDetail.numCredits.integerValue;
      subtitle = @"credits";
      selector = @selector(creditsButtonPressed:);
    }
    else if (i== 1) {
      //followers
      count = self.userDetail.numFollowers.integerValue;
      subtitle = @"followers";
      selector = @selector(followersButtonPressed:);
    }
    else {
      //friends
      count = self.userDetail.numFriends.integerValue;
      subtitle = @"following";
      selector = @selector(friendsButtonPressed:);
    }
    for (NSInteger k = 0; k < 2; k++) {
      UIView* view = [[[UIView alloc] initWithFrame:buttonFrame] autorelease];
      UIView* countView = [Util viewWithText:[NSString stringWithFormat:@"%d", count]
                                        font:[UIFont stampedBoldFontWithSize:12]
                                       color:[UIColor stampedDarkGrayColor]
                                        mode:UILineBreakModeTailTruncation
                                  andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
      CGFloat innerPadding = 3;
      [Util reframeView:countView withDeltas:CGRectMake(innerPadding, innerPadding, 0, 0)];
      [view addSubview:countView];
      UIView* subtitleView = [Util viewWithText:subtitle
                                           font:[UIFont stampedFontWithSize:12]
                                          color:[UIColor stampedGrayColor]
                                           mode:UILineBreakModeTailTruncation
                                     andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
      [Util reframeView:subtitleView withDeltas:CGRectMake(innerPadding, CGRectGetMaxY(countView.frame), 0, 0)];
      [view addSubview:subtitleView];
      
      NSArray* colors;
      if (k == 0) {
        colors = [UIColor stampedLightGradient];
      }
      else {
        colors = [UIColor stampedDarkGradient];
      }
      view.layer.cornerRadius = 2;
      view.layer.borderWidth = 1;
      view.layer.borderColor = [UIColor colorWithWhite:.95 alpha:1].CGColor;
      view.layer.shadowOpacity = .6;
      view.layer.shadowOffset = CGSizeMake(0, 1);
      view.layer.shadowRadius = 1;
      [Util addGradientToLayer:view.layer withColors:colors vertical:YES];
      views[k] = view;
    }
    STButton* button = [[[STButton alloc] initWithFrame:buttonFrame normalView:views[0] activeView:views[1] target:self andAction:selector] autorelease];
    [buttons addObject:button];
  }
  CGFloat buttonPadding = (contentWidth - (3 * buttonFrame.size.width)) / 2;
  CGSize size = [Util packViews:buttons padding:buttonPadding vertical:NO uniform:YES];
  CGRect buttonRect = [Util centeredAndBounded:size inFrame:self.header.frame];
  [Util offsetViews:buttons byX:buttonRect.origin.x andY:CGRectGetMaxY(userImage.frame) + 10];
  for (UIView* button in buttons) {
    [self.header addSubview:button];
  }
  self.header.backgroundColor = [UIColor whiteColor];
  self.header.layer.shadowColor = [UIColor blackColor].CGColor;
  self.header.layer.shadowOpacity = .5;
  self.header.layer.shadowRadius = 2;
  self.header.layer.shadowOffset = CGSizeMake(0, 2);
  [self.scrollView addSubview:self.header];
}

- (void)creditsButtonPressed:(id)button {
  [Util warnWithMessage:@"Not implemented yet..." andBlock:nil];
}

- (void)followersButtonPressed:(id)button {
  [Util warnWithMessage:@"Not implemented yet..." andBlock:nil];
}

- (void)friendsButtonPressed:(id)button {
  [Util warnWithMessage:@"Not implemented yet..." andBlock:nil];
}

@end
