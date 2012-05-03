//
//  STInboxViewController.m
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STInboxViewController.h"
#import "STToolbarView.h"
#import "STScopeSlider.h"
#import "STUserStampsSliceList.h"
#import "STGenericTableDelegate.h"
#import "STYouStampsList.h"
#import "STStampCellFactory.h"
#import "Util.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STGenericCellFactory.h"
#import "STFriendsStampsList.h"
#import "STFriendsOfFriendsStampsList.h"

@interface STInboxViewController () <STScopeSliderDelegate>

+ (void)setScope:(STStampedAPIScope)scope withInstance:(STInboxViewController*)instance;

@property (nonatomic, readonly, retain) STScopeSlider* slider;
@property (nonatomic, readonly, retain) STGenericTableDelegate* tableDelegate;

@end

@implementation STInboxViewController

@synthesize toolbar = toolbar_;
@synthesize slider = slider_;
@synthesize tableDelegate = tableDelegate_;

static STStampedAPIScope _scope = STStampedAPIScopeFriends;

- (id)init
{
  self = [super initWithHeaderHeight:0];
  if (self) {
    // Custom initialization
    tableDelegate_ = [[STGenericTableDelegate alloc] init];
    __block STInboxViewController* weakSelf = self;
    tableDelegate_.tableShouldReloadCallback = ^(id<STTableDelegate> tableDelegate) {
      [weakSelf.tableView reloadData];
    };
    tableDelegate_.selectedCallback = ^(STGenericTableDelegate* tableDelegate, UITableView* tableView, NSIndexPath* path) {
      id data = [tableDelegate_.lazyList objectAtIndex:path.row];
      if (data) {
        id<STStamp> stamp = data;
        STActionContext* context = [STActionContext context];
        context.stamp = stamp;
        id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
        [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
      }
    };
  }
  return self;
}

- (void)dealloc
{
  NSLog(@"\n\n\n\n\n\ndeallocing Inbox");
  [super dealloc];
}

- (void)viewDidLoad
{
  toolbar_ = [[STToolbarView alloc] init];
  [super viewDidLoad];
  slider_ = [[STScopeSlider alloc] initWithFrame:CGRectMake(45, 15, 230, 23)];
  slider_.delegate = self;
  [toolbar_ addSubview:slider_];
  tableDelegate_.lazyList = [STFriendsStampsList sharedInstance];
  tableDelegate_.tableViewCellFactory = [STGenericCellFactory sharedInstance];
  self.tableView.delegate = tableDelegate_;
  self.tableView.dataSource = tableDelegate_;
  [STInboxViewController setScope:_scope withInstance:self];
  [Util addHomeButtonToController:self];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  [toolbar_ release];
  [slider_ release];
  toolbar_ = nil;
  slider_ = nil;
}

- (void)scopeSlider:(STScopeSlider*)slider didChangeGranularity:(STStampedAPIScope)granularity {
  [STInboxViewController setScope:granularity withInstance:self];
}

- (void)reloadStampedData {
  [self.tableDelegate reloadStampedData];
  [super reloadStampedData];
}

+ (void)setScope:(STStampedAPIScope)scope withInstance:(STInboxViewController*)instance {
  [instance.tableDelegate.lazyList cancelPendingRequests];
  instance.tableDelegate.lazyList = [[STStampedAPI sharedInstance] globalListByScope:scope];
  
  [instance.tableView reloadData];
  if (instance.tableDelegate.lazyList.count > 0) {
    [instance.tableView scrollToRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0] atScrollPosition:UITableViewScrollPositionTop animated:NO];
  }
}

@end
