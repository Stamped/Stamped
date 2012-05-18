//
//  STProfileSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/23/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STProfileSource.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STButton.h"
#import <QuartzCore/QuartzCore.h>
#import "STUsersViewController.h"
#import "STTableViewController.h"

const static NSInteger _headerHeight = 50;
const static NSInteger _histogramHeight = 100;

@interface STDistributionHistogramCell : UITableViewCell

@end

@implementation STDistributionHistogramCell

- (id)initWithUserDetail:(id<STUserDetail>)userDetail {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"TODO"];
  if (self) {
    self.selectionStyle = UITableViewCellSelectionStyleNone;
    NSInteger maxStamps = 1;
    NSInteger totalStamps = 0;
    for (id<STDistributionItem> item in userDetail.distribution) {
      maxStamps = MAX(item.count.integerValue, maxStamps);
      totalStamps += item.count.integerValue;
    }
    self.accessoryType = UITableViewCellAccessoryNone;
    
    CGFloat bodyHeight = _histogramHeight;
    
    CGRect barFrame = CGRectMake(10, 10, 45, bodyHeight - 30);
    for (id<STDistributionItem> item in userDetail.distribution) {
      
      UIView* background = [[[UIView alloc] initWithFrame:barFrame] autorelease];
      background.backgroundColor = [UIColor colorWithWhite:.95 alpha:1];
      background.layer.cornerRadius = 3;
      background.layer.borderColor = [UIColor colorWithWhite:.8 alpha:1].CGColor;
      background.layer.borderWidth = 1;
      [self.contentView addSubview:background];
      CGFloat x = item.count.integerValue;
      CGFloat coeff = MIN((.5 - (1 / powf((x + 6), .4))) * 80/33,1);
      CGFloat height = MAX((coeff * barFrame.size.height), 2);
      UIView* histogram = [[[UIView alloc] initWithFrame:CGRectMake(barFrame.origin.x, barFrame.origin.y + barFrame.size.height - height, barFrame.size.width, height)] autorelease];
      
      histogram.layer.cornerRadius = 3;
      histogram.layer.borderColor = [UIColor colorWithWhite:0 alpha:.05].CGColor;
      histogram.layer.borderWidth = 1;
      
      NSArray* colors = [NSArray arrayWithObjects:
                         (id)[UIColor colorWithRed:.1 green:.8 blue:.4 alpha:1].CGColor,
                         (id)[UIColor colorWithRed:.05 green:.6 blue:.3 alpha:1].CGColor,
                         nil];
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
      [self.contentView addSubview:histogram];
      UIView* categoryIcon = [Util imageViewWithURL:[NSURL URLWithString:item.icon] andFrame:CGRectMake(0, 0, 11, 11)];
      categoryIcon.frame = [Util centeredAndBounded:categoryIcon.frame.size inFrame:CGRectMake(barFrame.origin.x, 
                                                                                               CGRectGetMaxY(barFrame),
                                                                                               barFrame.size.width, 
                                                                                               20)];
      [self.contentView addSubview:categoryIcon];
      
      STUserCollectionSlice* slice = [[[STUserCollectionSlice alloc] init] autorelease];
      slice.category = item.category;
      slice.userID = userDetail.userID;
      slice.offset = [NSNumber numberWithInteger:0];
      slice.limit = [NSNumber numberWithInteger:1000];
      UIView* button = [Util tapViewWithFrame:CGRectMake(barFrame.origin.x, 
                                                         barFrame.origin.y, 
                                                         barFrame.size.width, 
                                                         CGRectGetMaxY(categoryIcon.frame)-barFrame.origin.y)
                                       target:self
                                     selector:@selector(clickedBar:) 
                                   andMessage:slice];
      [self.contentView addSubview:button];
      barFrame = CGRectOffset(barFrame, barFrame.size.width+6, 0);
    }
  }
  return self;
}

- (void)clickedBar:(STUserCollectionSlice*)slice {
  STTableViewController* controller = [[[STTableViewController alloc] initWithHeaderHeight:0] autorelease];
  [controller view];
  STUserSource* source = [[[STUserSource alloc] init] autorelease];
  source.userID = slice.userID;
  source.slice = slice;
  source.table = controller.tableView;
  [controller retainObject:source];
  [[Util sharedNavigationController] pushViewController:controller animated:YES];
}

@end

@interface STProfileSource ()

- (void)creditsButtonPressed:(id)button;
- (void)followersButtonPressed:(id)button;
- (void)friendsButtonPressed:(id)button;

@property (nonatomic, readwrite, retain) UITableViewCell* cell;
@property (nonatomic, readonly, retain) UITableViewCell* histogram;
@property (nonatomic, readwrite, retain) id<STUserDetail> userDetail;

@end

@implementation STProfileSource

@synthesize cell = cell_;
@synthesize histogram = histogram_;
@synthesize userDetail = userDetail_;

- (void)setupHistogram {
  histogram_ = [[STDistributionHistogramCell alloc] initWithUserDetail:self.userDetail];
}

- (id)initWithUserDetail:(id<STUserDetail>)userDetail {
  self = [super init];
  if (self) {
    self.userID = userDetail.userID;
    self.userDetail = userDetail;
    STGenericCollectionSlice* slice = [[[STGenericCollectionSlice alloc] init] autorelease];
    slice.offset = [NSNumber numberWithInt:0];
    slice.limit = [NSNumber numberWithInt:NSIntegerMax];
    slice.sort = @"created";
    self.slice = slice;
    self.mainSection = 3;
    
    CGFloat padding = 10;
    CGFloat contentWidth = 320 - ( 2 * padding );
    cell_ = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"TODO"];
    cell_.accessoryType = UITableViewCellAccessoryNone;
    cell_.selectionStyle = UITableViewCellSelectionStyleNone;
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
    CGRect buttonRect = [Util centeredAndBounded:size inFrame:CGRectMake(0, 0, 320, _headerHeight)];
    [Util offsetViews:buttons byX:buttonRect.origin.x andY:buttonRect.origin.y];
    for (UIView* button in buttons) {
      [cell_.contentView addSubview:button];
    }
[self setupHistogram];
}
return self;
}

- (void)dealloc
{
  [userDetail_ release];
  [cell_ release];
  [histogram_ release];
  [super dealloc];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  if (section == 0) {
    return 1;
  }
  else if (section == 1) {
    return 1;
  }
  else {
    return [super tableView:tableView numberOfRowsInSection:section];
  }
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  if (indexPath.section == 0) {
    return self.cell;
  }
  else if (indexPath.section == 1) {
    return self.histogram;
  }
  else {
    return [super tableView:tableView cellForRowAtIndexPath:indexPath];
  }
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
  if (indexPath.section == 0) {
    return _headerHeight;
  }
  else if (indexPath.section == 1) {
    return _histogramHeight;
  }
  else {
    return [super tableView:tableView heightForRowAtIndexPath:indexPath];
  }
}


- (void)creditsButtonPressed:(id)button {
  [Util warnWithMessage:@"Not implemented yet..." andBlock:nil];
}

- (void)followersButtonPressed:(id)button {
  [self cancelPendingOperations];
  [Util globalLoadingLock];
  [[STStampedAPI sharedInstance] followerIDsForUserID:self.userDetail.userID andCallback:^(NSArray *followerIDs, NSError *error) {
    [Util globalLoadingUnlock];
    if (followerIDs) {
      STUsersViewController* controller = [[[STUsersViewController alloc] initWithUserIDs:followerIDs] autorelease];
      [[Util sharedNavigationController] pushViewController:controller animated:YES];
    }
  }];
}

- (void)friendsButtonPressed:(id)button {
  [self cancelPendingOperations];
  [Util globalLoadingLock];
  [[STStampedAPI sharedInstance] friendIDsForUserID:self.userDetail.userID andCallback:^(NSArray *friendIDs, NSError *error) {
    [Util globalLoadingUnlock];
    if (friendIDs) {
      STUsersViewController* controller = [[[STUsersViewController alloc] initWithUserIDs:friendIDs] autorelease];
      [[Util sharedNavigationController] pushViewController:controller animated:YES];
    }
  }];
}

@end
