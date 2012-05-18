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
#import "STSliderScopeView.h"

#import "EntityDetailViewController.h"
#import "STStampCell.h"
#import "AccountManager.h"


@interface STInboxViewController () <STScopeSliderDelegate>

- (void)setScope:(STStampedAPIScope)scope withInstance:(STInboxViewController*)instance;

@property (nonatomic, readonly, retain) STGenericTableDelegate* tableDelegate;
@property (nonatomic, readonly, retain) STTableDelegator* tableDelegator;
@property (nonatomic, readwrite, copy) NSString* query;

@end

@implementation STInboxViewController

@synthesize tableDelegate = tableDelegate_;
@synthesize tableDelegator = tableDelegator_;
@synthesize query = query_;

- (id)init {
  //self = [super initWithHeaderHeight:0];
  if (self = [super init]) {
    // Custom initialization
      /*
    tableDelegator_ = [[STTableDelegator alloc] init];
    
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
       */
      
      if ([AccountManager sharedManager].currentUser == nil) {
          _scope = STStampedAPIScopeEveryone;
      } else {
          _scope = STStampedAPIScopeFriends;
      }

  }
  return self;
}

- (void)dealloc {
    [tableDelegate_ release];
    [tableDelegator_ release];
    [query_ release];
    
    _slider = nil;
    [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
    
    
    tableDelegate_.lazyList = [STFriendsStampsList sharedInstance];
    tableDelegate_.tableViewCellFactory = [STGenericCellFactory sharedInstance];
    //self.tableView.delegate = tableDelegator_;
    //self.tableView.dataSource = tableDelegator_;
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
   
    [Util addHomeButtonToController:self withBadge:YES];
    [Util addCreateStampButtonToController:self];

    if (!_slider) {
        STSliderScopeView *slider = [[STSliderScopeView alloc] initWithFrame:CGRectMake(0, 0.0f, self.view.bounds.size.width, 54)];
        slider.delegate = (id<STSliderScopeViewDelegate>)self;
        self.footerView = slider;
        slider.scope = _scope;
        _slider = slider;
    }
    [self setScope:_scope];
    self.showsSearchBar = YES;

    
}

- (void)viewDidUnload {
    [super viewDidUnload];
    _slider = nil;
    //[toolbar_ release];
    //toolbar_ = nil;
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  [self.tableView reloadData];
}


#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope {
    [_stamps setScope:scope];
    
    /*
    [instance.tableDelegate.lazyList cancelPendingRequests];
  id<STLazyList> lazyList = nil;
  if (instance.query) {
      }
  else {
    lazyList = [[STStampedAPI sharedInstance] globalListByScope:scope];
  }
  instance.tableDelegate.lazyList = lazyList;
  [instance.tableView reloadData];
  if (instance.tableDelegate.lazyList.count > 0) {
      instance.tableView.contentOffset = CGPointZero;
  }
    */
}


#pragma mark - STSliderScopeViewDelegate

- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope {
    [self setScope:scope];
    
}


#pragma mark - UITableViewDataSouce

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return [_stamps numberOfStamps];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";
    
    STStampCell *cell = (STStampCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier];
    }
    
    id stamp = [_stamps stampAtIndex:indexPath.row];
    [cell setupWithStamp:stamp];
    
    return cell;
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    id stamp = [_stamps stampAtIndex:indexPath.row];
    EntityDetailViewController *controller = [[EntityDetailViewController alloc] initWithEntityID:[stamp sourceID]];
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];
    
}


#pragma mark - UITextFieldDelegate

- (BOOL)textField:(UITextField *)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString *)string {
  [Util executeOnMainThread:^{
    _stamps.searchQuery = [textField.text isEqualToString:@""] ? nil : textField.text;
  }];
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
    [super textFieldDidBeginEditing:textField];
  //Override collapsing behavior
  //[[Util sharedNavigationController] setNavigationBarHidden:YES animated:YES];
  //[self.tableDelegate cancelPendingRequests];
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
    [super textFieldDidEndEditing:textField];
  //Override collapsing behavior
  _stamps.searchQuery = [textField.text isEqualToString:@""] ? nil : textField.text;
  [self setScope:_scope];
 // [[Util sharedNavigationController] setNavigationBarHidden:NO animated:YES];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
    [super textFieldShouldReturn:textField];
    [textField resignFirstResponder];
    return YES;
}


#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return [_stamps isReloading];
}

- (void)loadNextPage {
    [_stamps loadNextPage];
}

- (BOOL)dataSourceHasMoreData {
    return [_stamps hasMoreData];
}

- (void)reloadDataSource {
    [_stamps reloadData];
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return [_stamps isEmpty];
}

- (void)setupNoDataView:(NoDataView*)view {
    
    [view setTitle:@"No Stamps" detailedTitle:@"No stamps found." imageName:nil];
    
}





@end
