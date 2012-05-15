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
#import "STButton.h"
#import "ECSlidingViewController.h"
#import "STTableDelegator.h"
#import "STSingleViewSource.h"
#import "STSearchField.h"
#import "STEveryoneStampsList.h"

@interface STInboxViewController () <STScopeSliderDelegate>

- (void)setScope:(STStampedAPIScope)scope withInstance:(STInboxViewController*)instance;

@property (nonatomic, readonly, retain) STScopeSlider* slider;
@property (nonatomic, readonly, retain) STGenericTableDelegate* tableDelegate;
@property (nonatomic, readonly, retain) STTableDelegator* tableDelegator;
@property (nonatomic, readonly, retain) STSearchField* searchField;
@property (nonatomic, readwrite, copy) NSString* query;

@end

@implementation STInboxViewController

@synthesize toolbar = toolbar_;
@synthesize slider = slider_;
@synthesize tableDelegate = tableDelegate_;
@synthesize tableDelegator = tableDelegator_;
@synthesize searchField = searchField_;
@synthesize query = query_;

static STStampedAPIScope _scope = STStampedAPIScopeFriends;

- (id)init
{
  self = [super initWithHeaderHeight:0];
  if (self) {
    // Custom initialization
    tableDelegator_ = [[STTableDelegator alloc] init];
    UIView* searchBar = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 40)] autorelease];
    searchField_ = [[STSearchField alloc] initWithFrame:CGRectMake(10, 5, 300, 30)];
    searchField_.placeholder = @"Search for stamps";
    searchField_.enablesReturnKeyAutomatically = NO;
    searchField_.delegate = self;
    [searchBar addSubview:searchField_];
    searchBar.backgroundColor = [UIColor colorWithWhite:.9 alpha:1];
    
    STSingleViewSource* searchSource = [[[STSingleViewSource alloc] initWithView:searchBar] autorelease];
    [tableDelegator_ appendTableDelegate:searchSource];
    
    tableDelegate_ = [[STGenericTableDelegate alloc] init];
    tableDelegate_.preloadBufferSize = 30;
    tableDelegate_.pageSize = 10;
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
    [tableDelegator_ appendTableDelegate:tableDelegate_];
  }
  return self;
}

- (void)dealloc
{
  [tableDelegate_ release];
  [tableDelegator_ release];
  [searchField_ release];
  [query_ release];
  [super dealloc];
}

- (void)viewDidLoad
{
  toolbar_ = [[STToolbarView alloc] init];
  [super viewDidLoad];
  slider_ = [[STScopeSlider alloc] initWithFrame:CGRectMake(45, 15, 230, 23)];
  [slider_ setGranularity:_scope animated:NO];
  slider_.delegate = self;
  [toolbar_ addSubview:slider_];
  tableDelegate_.lazyList = [STFriendsStampsList sharedInstance];
  tableDelegate_.tableViewCellFactory = [STGenericCellFactory sharedInstance];
  self.tableView.delegate = tableDelegator_;
  self.tableView.dataSource = tableDelegator_;
  [self setScope:_scope withInstance:self];
  [Util addHomeButtonToController:self withBadge:YES];
  [Util addCreateStampButtonToController:self];
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  [toolbar_ release];
  [slider_ release];
  toolbar_ = nil;
  slider_ = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self.tableView reloadData];
}

- (void)scopeSlider:(STScopeSlider*)slider didChangeGranularity:(STStampedAPIScope)granularity {
  [self setScope:granularity withInstance:self];
}

- (void)reloadStampedData {
  [self.tableDelegate reloadStampedData];
  [super reloadStampedData];
}

- (void)setScope:(STStampedAPIScope)scope withInstance:(STInboxViewController*)instance {
  _scope = scope;
  [instance.tableDelegate.lazyList cancelPendingRequests];
  id<STLazyList> lazyList = nil;
  if (instance.query) {
    if (scope == STStampedAPIScopeYou) {
      STUserStampsSliceList* userList = [[[STUserStampsSliceList alloc] init] autorelease];
      STUserCollectionSlice* userSlice = [[[STUserCollectionSlice alloc] init] autorelease];
      userSlice.userID = [[STStampedAPI sharedInstance].currentUser userID];
      userSlice.query = instance.query;
      userSlice.sort = @"relevance";
      userList.genericSlice = userSlice;
      lazyList = userList;
    }
    else if (scope == STStampedAPIScopeFriends) {
      STFriendsStampsList* stampsList = [[[STFriendsStampsList alloc] init] autorelease];
      STGenericCollectionSlice* slice = [[[STGenericCollectionSlice alloc] init] autorelease];
      slice.query = instance.query;
      slice.sort = @"relevance";
      stampsList.genericSlice = slice;
      lazyList = stampsList;
    }
    else if (scope == STStampedAPIScopeFriendsOfFriends) {
      STFriendsOfFriendsStampsList* stampsList = [[[STFriendsOfFriendsStampsList alloc] init] autorelease];
      STFriendsSlice* slice = [[[STFriendsSlice alloc] init] autorelease];
      slice.distance = [NSNumber numberWithInteger:2];
      slice.inclusive = [NSNumber numberWithBool:NO];
      slice.query = instance.query;
      slice.sort = @"relevance";
      stampsList.genericSlice = slice;
      lazyList = stampsList;
    }
    else {
      STEveryoneStampsList* list = [[[STEveryoneStampsList alloc] init] autorelease];
      STGenericCollectionSlice* slice = [[[STGenericCollectionSlice alloc] init] autorelease];
      slice.query = instance.query;
      slice.sort = @"relevance";
      list.genericSlice = slice;
      lazyList = list;
    }
  }
  else {
    lazyList = [[STStampedAPI sharedInstance] globalListByScope:scope];
  }
  instance.tableDelegate.lazyList = lazyList;
  [instance.tableView reloadData];
  if (instance.tableDelegate.lazyList.count > 0) {
    [instance.tableView scrollToRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0] atScrollPosition:UITableViewScrollPositionTop animated:NO];
  }
}

#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textField:(UITextField *)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString *)string {
  [Util executeOnMainThread:^{
    self.query = [textField.text isEqualToString:@""] ? nil : textField.text;
  }];
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  //Override collapsing behavior
  [[Util sharedNavigationController] setNavigationBarHidden:YES animated:YES];
  [self.tableDelegate cancelPendingRequests];
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
  //Override collapsing behavior
  self.query = [textField.text isEqualToString:@""] ? nil : textField.text;
  [self setScope:_scope withInstance:self];
  [[Util sharedNavigationController] setNavigationBarHidden:NO animated:YES];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  return YES;
}


@end
