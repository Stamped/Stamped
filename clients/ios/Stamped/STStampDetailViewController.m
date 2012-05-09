//
//  STStampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailViewController.h"

#import <Twitter/Twitter.h>

#import "AccountManager.h"
#import "Entity.h"
#import "EntityDetailViewController.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "STSynchronousWrapper.h"
#import "STEntityDetailFactory.h"
#import "STScrollViewContainer.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STStampDetailHeaderView.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import "STStampedAPI.h"
#import "STStampDetailCommentsView.h"
#import "STToolbarView.h"
#import "STLikeButton.h"
#import "STTodoButton.h"
#import "STStampButton.h"
#import "STStampedAPI.h"
#import "STButton.h"
#import "TTTAttributedLabel.h"
#import "STCommentButton.h"
#import "STShareButton.h"

@interface STStampDetailToolbar : UIView

- (id)initWithParent:(UIView*)view controller:(STStampDetailViewController*)controller andStamp:(id<STStamp>)stamp;
- (void)toggleToolbar:(id)button;

@property (nonatomic, readonly, retain) NSArray* buttons;
@property (nonatomic, readwrite, assign) BOOL expanded;
@property (nonatomic, readonly, retain) UIView* expandButton;
@property (nonatomic, readonly, retain) UIView* buttonContainer;

@end

@interface STStampDetailViewController () <UIActionSheetDelegate, UITextFieldDelegate>

@property (nonatomic, readwrite, retain) id<STStamp> stamp;

- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail;
- (void)_deleteStampButtonPressed:(id)caller;

@property (nonatomic, readonly, retain) STStampDetailHeaderView* headerView;
@property (nonatomic, readonly, retain) STStampDetailCommentsView* commentsView;
@property (nonatomic, readwrite, retain) STCancellation* entityDetailCancellation;

@end

@implementation STStampDetailToolbar

@synthesize buttons = buttons_;
@synthesize expanded = expanded_;
@synthesize expandButton = expandButton_;
@synthesize buttonContainer = buttonContainer_;

- (id)initWithParent:(UIView*)view controller:(STStampDetailViewController*)controller andStamp:(id<STStamp>)stamp {
  CGFloat xPadding = 5;
  CGFloat yPadding = 10;
  CGFloat height = 40;
  CGRect frame = CGRectMake(xPadding, view.frame.size.height - (height + yPadding), view.frame.size.width - (2 * xPadding), height);
  self = [super initWithFrame:frame];
  if (self) {
    expanded_ = YES;
    self.layer.cornerRadius = 5;
    self.layer.shadowOpacity = .3;
    self.layer.shadowRadius = 3;
    self.layer.shadowOffset = CGSizeMake(0, 2);
    self.layer.borderColor = [UIColor colorWithWhite:89.0/255 alpha:1].CGColor;
    self.layer.borderWidth = 1;
    [Util addGradientToLayer:self.layer 
                  withColors:[NSArray arrayWithObjects:
                              [UIColor colorWithWhite:.4 alpha:.80],
                              [UIColor colorWithWhite:.2 alpha:.85],
                              nil] 
                    vertical:YES];
    UIImageView* imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"sDetailBar_btn_more"]] autorelease];
    UIImageView* imageView2 = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"sDetailBar_btn_more_active"]] autorelease];
    expandButton_ = [[STButton alloc] initWithFrame:imageView.frame 
                                         normalView:imageView 
                                         activeView:imageView2 
                                             target:self 
                                          andAction:@selector(toggleToolbar:)];
    [Util reframeView:expandButton_ withDeltas:CGRectMake(frame.size.width - (expandButton_.frame.size.width + 10), 10, 0, 0)];
    
    
    buttons_ = [[NSMutableArray arrayWithObjects:
                 [[[STLikeButton alloc] initWithStamp:stamp] autorelease],
                 [[[STTodoButton alloc] initWithStamp:stamp] autorelease],
                 [[[STStampButton alloc] initWithStamp:stamp] autorelease],
                 [[[STCommentButton alloc] initWithCallback:^{
      [Util warnWithMessage:@"Not implemented yet..." andBlock:nil];
    }] autorelease],
                 [[[STShareButton alloc] initWithCallback:^{
      [Util warnWithMessage:@"Not implemented yet..." andBlock:nil];
    }] autorelease],
                 nil] retain];
    CGFloat buttonSpacing = 60;
    buttonContainer_ = [[UIView alloc] initWithFrame:CGRectMake(0, -3, CGRectGetMinX(expandButton_.frame)+50, frame.size.height-7)];
    for (NSInteger i = 0; i < buttons_.count; i++) {
      UIView* button = [buttons_ objectAtIndex:i];
      [Util reframeView:button withDeltas:CGRectMake(-5 + (i * buttonSpacing), -4, 0, 0)];
      [buttonContainer_ addSubview:button];
    }
    buttonContainer_.clipsToBounds = NO;
    [self addSubview:buttonContainer_];
    self.clipsToBounds = YES;
    [Util reframeView:expandButton_ withDeltas:CGRectMake(3, -3, 0, 0)];
    [self addSubview:expandButton_];
    [self toggleToolbar:nil];
  }
  return self;
}

- (void)toggleToolbar:(id)notImportant {
  CGFloat delta = 155;
  CGFloat deltaSpacing = 15;
  CGFloat duration = .5;
  if (self.expanded) {
    [UIView animateWithDuration:duration animations:^{
      [Util reframeView:self withDeltas:CGRectMake(delta, 0, -delta, 0)];
      [Util reframeView:self.buttonContainer withDeltas:CGRectMake(0, 0, -delta, 0)];
      [Util reframeView:self.expandButton withDeltas:CGRectMake(-delta, 0, 0, 0)];
      for (NSInteger i = 0; i < buttons_.count; i++) {
        UIView* button = [buttons_ objectAtIndex:i];
        [Util reframeView:button withDeltas:CGRectMake(i * -deltaSpacing, 0, 0, 0)];
        if (CGRectGetMaxX(button.frame) - 20 > self.buttonContainer.frame.size.width - 50) {
          button.alpha = 0;
        }
      }
    }];
  }
  else {
    [UIView animateWithDuration:duration animations:^{
      [Util reframeView:self withDeltas:CGRectMake(-delta, 0, delta, 0)];
      [Util reframeView:self.buttonContainer withDeltas:CGRectMake(0, 0, delta, 0)];
      [Util reframeView:self.expandButton withDeltas:CGRectMake(delta, 0, 0, 0)];
      for (NSInteger i = 0; i < buttons_.count; i++) {
        UIView* button = [buttons_ objectAtIndex:i];
        [Util reframeView:button withDeltas:CGRectMake(i * deltaSpacing, 0, 0, 0)];
        button.alpha = 1;
      }
    }];
  }
  self.expanded = !self.expanded;
}

- (void)reloadStampedData {
  for (id view in self.buttonContainer.subviews) {
    if ([view respondsToSelector:@selector(reloadStampedData)]) {
      [view reloadStampedData]; 
    }
  }
}

@end

@implementation STStampDetailViewController

@synthesize headerView = _headerView;
@synthesize commentsView = _commentsView;
@synthesize stamp = _stamp;
@synthesize toolbar = _toolbar;
@synthesize entityDetailCancellation = entityDetailCancellation_;

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super init];
  if (self) {
    _stamp = [stamp retain];
  }
  return self;
}

- (void)dealloc
{
  [_headerView release];
  [_commentsView release];
  [_stamp release];
  [_toolbar release];
  [entityDetailCancellation_ release];
  [super dealloc];
}

- (void)viewDidLoad {
  //STToolbarView* toolbar = [[STToolbarView alloc] init];
  //_toolbar = toolbar;
  [super viewDidLoad];
  UIBarButtonItem* backButton = [[[UIBarButtonItem alloc] initWithTitle:[Util truncateTitleForBackButton:self.stamp.entity.title]
                                                                  style:UIBarButtonItemStyleBordered
                                                                 target:nil
                                                                 action:nil] autorelease];
  [[self navigationItem] setBackBarButtonItem:backButton];
  
  _headerView = [[STStampDetailHeaderView alloc] initWithStamp:self.stamp];
  [self.scrollView appendChildView:_headerView];
  for (NSInteger i = 0; i < self.stamp.contents.count; i++) {
    _commentsView = [[STStampDetailCommentsView alloc] initWithStamp:self.stamp 
                                                               index:i 
                                                               style:STStampDetailCommentsViewStyleNormal 
                                                         andDelegate:self.scrollView];
    _commentsView.addCommentView.delegate = self;
    [self.scrollView appendChildView:_commentsView];
  }
  if ([AccountManager.sharedManager.currentUser.screenName isEqualToString:self.stamp.user.screenName]) {
    UIBarButtonItem* rightButton = [[[UIBarButtonItem alloc] initWithTitle:@"Delete"
                                                                     style:UIBarButtonItemStylePlain
                                                                    target:self
                                                                    action:@selector(_deleteStampButtonPressed:)] autorelease];
    self.navigationItem.rightBarButtonItem = rightButton;
  }
  //[toolbar packViews:views];
  UIView* newToolbar = [[[STStampDetailToolbar alloc] initWithParent:self.view controller:self andStamp:self.stamp] autorelease];
  [self.view addSubview:newToolbar];
  
  self.entityDetailCancellation = [[STStampedAPI sharedInstance] entityDetailForEntityID:self.stamp.entity.entityID 
                                                                             andCallback:^(id<STEntityDetail> detail, NSError *error, STCancellation *cancellation) {
                                                                               
                                                                               STSynchronousWrapper* wrapper = [STSynchronousWrapper wrapperForStampDetail:detail withFrame:CGRectMake(0, 0, 320, 200) stamp:self.stamp delegate:self.scrollView];
                                                                               [self.scrollView appendChildView:wrapper];
                                                                               self.scrollView.contentSize = CGSizeMake(self.scrollView.contentSize.width, self.scrollView.contentSize.height);
                                                                               UIView* padding = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 0, 60)] autorelease];
                                                                               [self.scrollView appendChildView:padding];
                                                                             }];
  
  
}

- (void)viewDidUnload {
}

- (void)cancelPendingRequests {
  [self.entityDetailCancellation cancel];
}


- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  //[self setUpToolbar];
  [_headerView setNeedsDisplay];
  NSLog(@"viewWillAppear");
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [[STActionManager sharedActionManager] setStampContext:self.stamp];
}

- (void)viewWillDisappear:(BOOL)animated {
  [[STActionManager sharedActionManager] setStampContext:nil];
  [super viewWillDisappear:animated];
}

- (void)_deleteStampButtonPressed:(id)caller {
  [Util confirmWithMessage:@"Are you sure?" action:@"Delete" destructive:YES withBlock:^(BOOL confirmed) {
    if (confirmed) {
      STActionContext* context = [STActionContext contextWithCompletionBlock:^(id success, NSError *error) {
        if (!error) {
          [[Util sharedNavigationController] popViewControllerAnimated:YES];
        }
      }];
      id<STAction> action = [STStampedActions actionDeleteStamp:self.stamp.stampID withOutputContext:context];
      [[STActionManager sharedActionManager] didChooseAction:action withContext:context];    }
  }];
}

- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail {
  NSLog(@"detail");
  CGFloat wrapperHeight = 200;
  CGRect wrapperFrame = CGRectMake(0, 0 , 320, wrapperHeight);
  STSynchronousWrapper* eDetailView = [STSynchronousWrapper wrapperForEntityDetail:detail
                                                                         withFrame:wrapperFrame 
                                                                          andStyle:@"StampDetail" 
                                                                          delegate:self.scrollView];
  [self.scrollView appendChildView:eDetailView];
}

- (void)handleEntityTap:(id)sender {
  STActionContext* context = [STActionContext context];
  id<STAction> action = [STStampedActions actionViewEntity:self.stamp.entity.entityID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (UIView *)toolbar {
  return _toolbar;
}

@end
