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
#import "CreateStampViewController.h"
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
#import "StampDetailHeaderView.h"
#import "STStampDetailHeaderView.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import "STStampedAPI.h"
#import "STStampDetailCommentsView.h"
#import "STToolbarView.h"
#import "STLikeButton.h"
#import "STTodoButton.h"
#import "STStampButton.h"


@interface STStampDetailViewController () <StampDetailHeaderViewDelegate, UIActionSheetDelegate, UITextFieldDelegate>

@property (nonatomic, readwrite, retain) id<STStamp> stamp;

- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail;
- (void)_deleteStampButtonPressed:(id)caller;

@property (nonatomic, readonly, retain) STStampDetailHeaderView* headerView;
@property (nonatomic, readonly, retain) STStampDetailCommentsView* commentsView;

@end

@implementation STStampDetailViewController

@synthesize headerView = _headerView;
@synthesize commentsView = _commentsView;
@synthesize stamp = _stamp;

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super init];
  if (self) {
    _stamp = [stamp retain];
  }
  return self;
}

- (void)loadView {
  [super loadView];
  
  UIBarButtonItem* backButton = [[[UIBarButtonItem alloc] initWithTitle:[Util truncateTitleForBackButton:self.stamp.entity.title]
                                                                  style:UIBarButtonItemStyleBordered
                                                                 target:nil
                                                                 action:nil] autorelease];
  [[self navigationItem] setBackBarButtonItem:backButton];
  
  _headerView = [[STStampDetailHeaderView alloc] initWithStamp:self.stamp];
  [self.scrollView appendChildView:_headerView];
  _commentsView = [[STStampDetailCommentsView alloc] initWithStamp:self.stamp andDelegate:self.scrollView];
  _commentsView.addCommentView.delegate = self;
  [self.scrollView appendChildView:_commentsView];
  
  STToolbarView* toolbar = [[STToolbarView alloc] initWithFrame:CGRectMake(0, 0, 320, 70)];
  NSMutableArray* views = [NSMutableArray arrayWithObjects:
                           [[[STLikeButton alloc] initWithStamp:self.stamp] autorelease],
                           [[[STTodoButton alloc] initWithStamp:self.stamp] autorelease],
                           nil];
  if (![AccountManager.sharedManager.currentUser.screenName isEqualToString:self.stamp.user.screenName]) {
    [views addObject:[[[STStampButton alloc] initWithStamp:self.stamp] autorelease]];
  }
  else {
    UIBarButtonItem* rightButton = [[UIBarButtonItem alloc] initWithTitle:@"Delete"
                                                                    style:UIBarButtonItemStylePlain
                                                                   target:self
                                                                   action:@selector(_deleteStampButtonPressed:)];
    self.navigationItem.rightBarButtonItem = rightButton;
  }
  [toolbar packViews:views withPadding:10];
  [self setToolbar:toolbar withAnimation:YES];
  
}

- (void)dealloc {
  [_stamp release];
  [_headerView release];
  [super dealloc];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  NSLog(@"viewWillDisappear");
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  //[self setUpToolbar];
  [_headerView setNeedsDisplay];
  NSLog(@"viewWillAppear");
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  //stampPhotoView_.imageURL = stamp_.imageURL;
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

@end
