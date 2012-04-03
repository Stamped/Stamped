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
#import "STActionManager.h"
#import "STStampedActions.h"

@interface STStampDetailViewController () <StampDetailHeaderViewDelegate>

@property (nonatomic, retain) Stamp* stamp;

- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail;

@property (nonatomic, readonly, retain) StampDetailHeaderView* headerView;

@end

@implementation STStampDetailViewController

@synthesize headerView = _headerView;

@synthesize stamp = _stamp;

- (id)initWithStamp:(Stamp*)stamp {
  self = [super init];
  if (self) {
    _stamp = [stamp retain];
  }
  return self;
}

- (void)loadView {
  [super loadView];
  
  UIBarButtonItem* backButton = [[[UIBarButtonItem alloc] initWithTitle:[Util truncateTitleForBackButton:_stamp.entityObject.title]
                                                                 style:UIBarButtonItemStyleBordered
                                                                target:nil
                                                                action:nil] autorelease];
  [[self navigationItem] setBackBarButtonItem:backButton];
  
  _headerView = [[StampDetailHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 68)];
  _headerView.stamp = self.stamp;
  _headerView.delegate = self;
  //_headerView.backgroundColor = [UIColor redColor];
  [self.scrollView appendChildView:_headerView];
  
  
  NSOperation* operation = [[STEntityDetailFactory sharedFactory] entityDetailCreatorWithEntityId:_stamp.entityObject.entityID 
                                                                                 andCallbackBlock:^(id<STEntityDetail> detail) {
                                                                                   [self _didLoadEntityDetail:detail];
                                                                                 }];
  [Util runOperationAsynchronously:operation];
}

- (void)dealloc {
  [_stamp release];
  [_headerView release];
  [super dealloc];
}

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  //[self setUpToolbar];
  _headerView.inverted = NO;
  [_headerView setNeedsDisplay];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  //stampPhotoView_.imageURL = stamp_.imageURL;
}


- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail {

  CGFloat wrapperHeight = 200;
  CGRect wrapperFrame = CGRectMake(0, 0 , 320, wrapperHeight);
  STSynchronousWrapper* eDetailView = [STSynchronousWrapper wrapperForEntityDetail:detail
                                                                         withFrame:wrapperFrame 
                                                                          andStyle:@"StampDetail" 
                                                                          delegate:self.scrollView];
  [self.scrollView appendChildView:eDetailView];
}

- (IBAction)handleEntityTap:(id)sender {
  STActionContext* context = [STActionContext context];
  id<STAction> action = [STStampedActions actionViewEntity:self.stamp.entityObject.entityID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

@end
