//
//  STPostStampViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STPostStampViewController.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STStampedAPI.h"
#import <QuartzCore/QuartzCore.h>
#import "STRippleViewContainer.h"
#import "STRippleBar.h"
#import "STStampedByView.h"
#import "STSimpleStampedBy.h"
#import "STStampedActions.h"
#import "STActionManager.h"

@interface STPostStampViewController ()

@property (nonatomic, readonly, retain) id<STStamp> stamp;
@property (nonatomic, readwrite, retain) id<STStampedBy> stampedBy;
@property (nonatomic, readwrite, retain) id<STUserDetail> userDetail;

- (UIView*)createHeaderView;
- (void)handleUserDetail:(id<STUserDetail>)userDetail withError:(NSError*)error;
- (void)handleStampedBy:(id<STStampedBy>)stampedBy withError:(NSError*)error;
- (void)addBadgesWithUser:(id<STUserDetail>)userDetail andView:(STViewContainer*)view;
- (void)addFriendOrdinalToView:(STViewContainer*)view;

@end

@implementation STPostStampViewController

@synthesize stamp = _stamp;
@synthesize userDetail = userDetail_;
@synthesize stampedBy = stampedBy_;

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super init];
  if (self) {
    _stamp = [stamp retain];
  }
  return self;
}

- (void)dealloc
{
  [_stamp release];
  [userDetail_ release];
  [stampedBy_ release];
  [super dealloc];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  if (self.stamp) {
    self.navigationItem.leftBarButtonItem.enabled = NO;
    // Do any additional setup after loading the view.
    [self.scrollView appendChildView:[self createHeaderView]];
    [[STStampedAPI sharedInstance] userDetailForUserID:self.stamp.user.userID andCallback:^(id<STUserDetail> userDetail, NSError *error) {
      [self handleUserDetail:userDetail withError:error];
    }];
    STStampedBySlice* slice = [[[STStampedBySlice alloc] init] autorelease];
    slice.entityID = self.stamp.entity.entityID;
    slice.limit = [NSNumber numberWithInteger:10];
    [[STStampedAPI sharedInstance] stampedByForStampedBySlice:slice 
                                         andCallback:^(id<STStampedBy> stampedBy, NSError* error, STCancellation* cancellation) {
                                           [self handleStampedBy:stampedBy withError:error];
                                         }];
  }
  else {
    [Util warnWithMessage:@"Created post stamp with no stamp; CreateStamp bug" andBlock:^{
      [[Util sharedNavigationController] popToRootViewControllerAnimated:YES];
    }];
  }
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  // Release any retained subviews of the main view.
}

- (void)profileImageClicked:(id)nothing {
  STActionContext* context = [STActionContext context];
  id<STAction> action = [STStampedActions actionViewUser:self.stamp.user.userID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)friendImageClicked:(id<STStamp>)stamp {
  STActionContext* context = [STActionContext context];
  context.stamp = stamp;
  id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (UIView*)createHeaderView {
  CGFloat height = 60;
  CGFloat paddingX = 8;
  UIView* view = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, height)] autorelease];
  
  //Profile image packed left x + padding, centered y
  UIView* profileImage = [Util profileImageViewForUser:self.stamp.user withSize:STProfileImageSize37];
  profileImage.frame = [Util centeredAndBounded:profileImage.frame.size inFrame:CGRectMake(paddingX, 0, height, height)];
  [view addSubview:profileImage];
  
  UIView* profileImageButton = [Util tapViewWithFrame:profileImage.frame target:self selector:@selector(profileImageClicked:) andMessage:nil];
  [view addSubview:profileImageButton];
  
  CGFloat textX = CGRectGetMaxX(profileImage.frame) + paddingX;
  
  // "You stamped" packed left x to image + padding , aligned y with top of image
  UILabel* upperText = [Util viewWithText:@"You stamped"
                                     font:[UIFont stampedFontWithSize:10]
                                    color:[UIColor stampedGrayColor]
                                     mode:UILineBreakModeTailTruncation
                               andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
  [Util reframeView:upperText withDeltas:CGRectMake(textX,
                                                    CGRectGetMinY(profileImage.frame),
                                                    0,
                                                    0)];
  [view addSubview:upperText];
  
  // Entity title and stamp image
  UILabel* entityTitle = [Util viewWithText:self.stamp.entity.title
                                       font:[UIFont stampedTitleFontWithSize:26]
                                      color:[UIColor stampedBlackColor]
                                       mode:UILineBreakModeTailTruncation
                                 andMaxSize:CGSizeMake(view.frame.size.width - textX, 26)];
  [Util reframeView:entityTitle withDeltas:CGRectMake(textX, 
                                                      (CGRectGetMaxY(profileImage.frame) - entityTitle.frame.size.height) + 8,
                                                      0,
                                                      0)];
  //TODO add stamp image
  [view addSubview:entityTitle];
  return view;
}

- (void)commonSetup {
  STViewContainer* mainView = [[[STViewContainer alloc] initWithDelegate:self.scrollView andFrame:CGRectMake(5, 0, 310, 2)] autorelease];
  mainView.backgroundColor = [UIColor whiteColor];
  mainView.layer.shadowColor = [UIColor blackColor].CGColor;
  mainView.layer.shadowOpacity = .1;
  mainView.layer.shadowRadius = 4;
  mainView.layer.shadowOffset = CGSizeMake(0,2);
  STRippleBar* topBar = [[[STRippleBar alloc] initWithPrimaryColor:self.userDetail.primaryColor 
                                                 andSecondaryColor:self.userDetail.secondaryColor 
                                                             isTop:YES] autorelease];
  [mainView appendChildView:topBar];
  STRippleBar* bottomBar = [[[STRippleBar alloc] initWithPrimaryColor:self.userDetail.primaryColor
                                                    andSecondaryColor:self.userDetail.secondaryColor
                                                                isTop:NO] autorelease];
  [self addUserDistributionWithUser:self.userDetail andView:mainView];
  [self addFriendOrdinalToView:mainView];
  [self addBadgesWithUser:self.userDetail andView:mainView];
  
  [mainView appendChildView:bottomBar];
  [Util reframeView:mainView withDeltas:CGRectMake(0, 0, 0, 2)];
  [self.scrollView appendChildView:mainView];
  
  STSimpleStampedBy* stampedByLimited = [[[STSimpleStampedBy alloc] init] autorelease];
  stampedByLimited.everyone = self.stampedBy.everyone;
  STStampedByView* stampedByView = [[[STStampedByView alloc] initWithStampedBy:stampedByLimited
                                                                     blacklist:[NSSet setWithObject:self.userDetail.userID] 
                                                                      entityID:self.stamp.entity.entityID
                                                                   andDelegate:self.scrollView] autorelease];
  [Util reframeView:stampedByView withDeltas:CGRectMake(0, 5, 0, 0)];
  [self.scrollView appendChildView:stampedByView];
  [self.scrollView appendChildView:[[[UIView alloc] initWithFrame:CGRectMake(0, 0, 1, 20)] autorelease]];
  
  //Update inbox
  //[[STLegacyInboxViewController sharedInstance] newStampCreated:self.stamp];
  [[[STStampedAPI sharedInstance] globalListByScope:STStampedAPIScopeFriends] reload];
  [[[STStampedAPI sharedInstance] globalListByScope:STStampedAPIScopeYou] reload];
}

- (void)handleUserDetail:(id<STUserDetail>)userDetail withError:(NSError*)error {
  if (userDetail) {
    self.userDetail = userDetail;
    if (self.stampedBy) {
      [self commonSetup];
    }
  }
  else {
    [Util warnWithMessage:@"User Detail failed to load" andBlock:nil];
  }
}

- (void)handleStampedBy:(id<STStampedBy>)stampedBy withError:(NSError*)error {
  if (stampedBy) {
    self.stampedBy = stampedBy;
    if (self.userDetail) {
      [self commonSetup];
    }
  }
  else {
    [Util warnWithMessage:@"Also stamped by failed to load" andBlock:nil];
  }
}


- (void)addUserDistributionWithUser:(id<STUserDetail>)userDetail andView:(STViewContainer*)view {
  if (userDetail.distribution) {
    STViewContainer* distributionView = [[[STViewContainer alloc] initWithDelegate:view andFrame:CGRectMake(0, 0, 310, 0)] autorelease];
    id<STDistributionItem> relevantItem = nil;
    NSInteger maxStamps = 1;
    for (id<STDistributionItem> item in userDetail.distribution) {
      if ([item.category isEqualToString:self.stamp.entity.category]) {
        relevantItem = item;
      }
      maxStamps = MAX(item.count.integerValue, maxStamps);
    }
    UIView* header = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 310, 30)] autorelease];
    CGFloat headerY = 5;
    UIView* headerIcon = [Util imageViewWithURL:[NSURL URLWithString:relevantItem.icon] andFrame:CGRectMake(5, headerY+5, 11, 11)];
    [header addSubview:headerIcon];
    UIFont* normalFont = [UIFont stampedFontWithSize:14];
    UIView* firstText = [Util viewWithText:@"That's your "
                                      font:normalFont
                                     color:[UIColor stampedGrayColor]
                                      mode:UILineBreakModeClip
                                andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:firstText withDeltas:CGRectMake(CGRectGetMaxX(headerIcon.frame)+5, headerY, 0, 0)];
    [header addSubview:firstText];
    UIView* ordinalText = [Util viewWithText:[NSString stringWithFormat:@"%@", relevantItem.count]
                                        font:[UIFont stampedBoldFontWithSize:14]
                                       color:[UIColor stampedDarkGrayColor]
                                        mode:UILineBreakModeClip
                                  andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:ordinalText withDeltas:CGRectMake(CGRectGetMaxX(firstText.frame), headerY, 0, 0)];
    [header addSubview:ordinalText];
    UIView* secondText = [Util viewWithText:[NSString stringWithFormat:@" stamp in %@", [relevantItem.category capitalizedString]]
                                       font:normalFont
                                      color:[UIColor stampedGrayColor]
                                       mode:UILineBreakModeClip
                                 andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:secondText withDeltas:CGRectMake(CGRectGetMaxX(ordinalText.frame), headerY, 0, 0)];
    [header addSubview:secondText];
    [distributionView appendChildView:header];
    CGFloat bodyHeight = 70;
    UIView* body = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, distributionView.frame.size.width, bodyHeight + 20)] autorelease];
    
    CGRect barFrame = CGRectMake(5, 0, 45, bodyHeight);
    for (id<STDistributionItem> item in userDetail.distribution) {
      CGFloat height = MAX((item.count.integerValue * bodyHeight) / maxStamps, 3);
      UIView* histogram = [[[UIView alloc] initWithFrame:CGRectMake(barFrame.origin.x, bodyHeight-height, barFrame.size.width, height)] autorelease];
      
      histogram.layer.cornerRadius = 3;
      histogram.layer.borderColor = [UIColor colorWithWhite:0 alpha:.05].CGColor;
      histogram.layer.borderWidth = 1;
      
      NSArray* colors = [NSArray arrayWithObjects:
                         (id)[UIColor colorWithWhite:.95 alpha:1].CGColor,
                         (id)[UIColor colorWithWhite:.8 alpha:1].CGColor,
                         nil];
      if ([item.category isEqualToString:relevantItem.category]) {
        colors = [NSArray arrayWithObjects:
                  (id)[UIColor colorWithRed:.1 green:.8 blue:.4 alpha:1].CGColor,
                  (id)[UIColor colorWithRed:.05 green:.6 blue:.3 alpha:1].CGColor,
                  nil];
      }
      histogram.layer.shadowColor = [UIColor blackColor].CGColor;
      histogram.layer.shadowOpacity = .1;
      histogram.layer.shadowRadius = 2;
      histogram.layer.shadowOffset = CGSizeMake(0, 2);
      
      CAGradientLayer* gradient = [CAGradientLayer layer];
      gradient.anchorPoint = CGPointMake(0, 0);
      gradient.position = CGPointMake(0, 0);
      gradient.bounds = histogram.layer.bounds;
      gradient.cornerRadius = histogram.layer.cornerRadius;
      gradient.colors = colors;
      [histogram.layer addSublayer:gradient];
      [body addSubview:histogram];
      UIView* categoryIcon = [Util imageViewWithURL:[NSURL URLWithString:item.icon] andFrame:CGRectMake(0, 0, 11, 11)];
      categoryIcon.frame = [Util centeredAndBounded:categoryIcon.frame.size inFrame:CGRectMake(barFrame.origin.x, 
                                                                                               CGRectGetMaxY(barFrame),
                                                                                               barFrame.size.width, 
                                                                                               20)];
      [body addSubview:categoryIcon];
      barFrame = CGRectOffset(barFrame, barFrame.size.width+5, 0);
    }
    
    
    [distributionView appendChildView:body];
    [view appendChildView:distributionView];
  }
}

- (void)addBadgesWithUser:(id<STUserDetail>)userDetail andView:(STViewContainer*)view {
  if (self.stamp.badges) {
    for (id<STBadge> badge in self.stamp.badges) {
      UIView* barView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, view.frame.size.width, 1)] autorelease];
      barView.backgroundColor = [UIColor colorWithWhite:.9 alpha:1];
      [view appendChildView:barView];
      NSString* text = nil;
      NSString* topString = @"You're the";
      NSString* bottomString = @"to stamp this";
      if ([badge.genre isEqualToString:@"entity_first_stamp"]) {
        text = @"1st on Stamped";
      }
      else if ([badge.genre isEqualToString:@"friends_first_stamp"]) {
        text = @"1st of your friends";
      }
      else if ([badge.genre isEqualToString:@"user_first_stamp"]) {
        topString = @"This is your";
        text = @"1st Stamp";
        bottomString = @"Welcome to Stamped!";
      }
      if (text) {
        UIView* cell = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 310, 85)] autorelease];
        UIView* imageView = [Util badgeViewForGenre:badge.genre];
        imageView.frame = [Util centeredAndBounded:imageView.frame.size inFrame:CGRectMake(0, 0, cell.frame.size.height, cell.frame.size.height)];
        [cell addSubview:imageView];
        UILabel* mainText = [Util viewWithText:text
                                          font:[UIFont stampedBoldFontWithSize:14]
                                         color:[UIColor stampedDarkGrayColor]
                                          mode:UILineBreakModeTailTruncation
                                    andMaxSize:CGSizeMake(200, CGFLOAT_MAX)];
        mainText.frame = [Util centeredAndBounded:mainText.frame.size inFrame:cell.frame];
        [cell addSubview:mainText];
        
        UIFont* font = [UIFont stampedFontWithSize:10];
        UIColor* color = [UIColor stampedGrayColor];
        UILabel* topText = [Util viewWithText:topString
                                         font:font
                                        color:color 
                                         mode:UILineBreakModeTailTruncation
                                   andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
        topText.frame = [Util centeredAndBounded:topText.frame.size inFrame:cell.frame];
        [Util reframeView:topText withDeltas:CGRectMake(0, -mainText.frame.size.height, 0, 0)];
        [cell addSubview:topText];
        UILabel* bottomText = [Util viewWithText:bottomString
                                            font:font
                                           color:color
                                            mode:UILineBreakModeTailTruncation
                                      andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
        bottomText.frame = [Util centeredAndBounded:bottomText.frame.size inFrame:cell.frame];
        [Util reframeView:bottomText withDeltas:CGRectMake(0, mainText.frame.size.height, 0, 0)];
        [cell addSubview:bottomText];
        
        [view appendChildView:cell];
      }
    }
  }
}

- (void)addFriendOrdinalToView:(STViewContainer*)view {
  STViewContainer* friendsView = [[[STViewContainer alloc] initWithDelegate:view andFrame:CGRectMake(0, 0, 310, 0)] autorelease];
  UIView* header = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 310, 30)] autorelease];
  CGFloat headerY = 5;
  UIImageView* headerIcon = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"scope_drag_inner_friends"]] autorelease];
  headerIcon.frame = CGRectMake(5, headerY+5, 11, 11);
  [header addSubview:headerIcon];
  UIFont* normalFont = [UIFont stampedFontWithSize:14];
  UIView* firstText = [Util viewWithText:@"You're the "
                                    font:normalFont
                                   color:[UIColor stampedGrayColor]
                                    mode:UILineBreakModeClip
                              andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
  [Util reframeView:firstText withDeltas:CGRectMake(CGRectGetMaxX(headerIcon.frame)+5, headerY, 0, 0)];
  [header addSubview:firstText];
  UIView* ordinalText = [Util viewWithText:[NSString stringWithFormat:@"%d", self.stampedBy.friends.count.integerValue + 1]
                                      font:[UIFont stampedBoldFontWithSize:14]
                                     color:[UIColor stampedDarkGrayColor]
                                      mode:UILineBreakModeClip
                                andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
  [Util reframeView:ordinalText withDeltas:CGRectMake(CGRectGetMaxX(firstText.frame), headerY, 0, 0)];
  [header addSubview:ordinalText];
  UIView* secondText = [Util viewWithText:@" of your friends to stamp this."
                                     font:normalFont
                                    color:[UIColor stampedGrayColor]
                                     mode:UILineBreakModeClip
                               andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
  [Util reframeView:secondText withDeltas:CGRectMake(CGRectGetMaxX(ordinalText.frame), headerY, 0, 0)];
  [header addSubview:secondText];
  [friendsView appendChildView:header];
  [Util reframeView:friendsView withDeltas:CGRectMake(0, 0, 0, 50)];
  NSMutableArray* stampPreviews = [NSMutableArray arrayWithObject:self.stamp];
  for (id<STStampPreview> stampPreview in self.stampedBy.friends.stampPreviews) {
    if (stampPreviews.count > 7) {
      break;
    }
    else {
      [stampPreviews addObject:stampPreview];
    }
  }
  CGFloat xOffset = 5;
  CGFloat yOffset = CGRectGetMaxY(ordinalText.frame)+10;
  for (NSInteger i = stampPreviews.count - 1; i >= 0; i--) {
    id<STStamp> stamp = [stampPreviews objectAtIndex:i];
    UIView* imageView = [Util profileImageViewForUser:stamp.user withSize:STProfileImageSize37];
    [Util reframeView:imageView withDeltas:CGRectMake(xOffset, yOffset, 0, 0)];
    [friendsView addSubview:imageView];
    UIView* imageButton = [Util tapViewWithFrame:imageView.frame target:self selector:@selector(friendImageClicked:) andMessage:stamp];
    [friendsView addSubview:imageButton];
    xOffset += 40;
  }
  [view appendChildView:friendsView];
}

@end
