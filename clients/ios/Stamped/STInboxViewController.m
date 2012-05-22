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
#import "STStampedActions.h"

#import "EntityDetailViewController.h"
#import "STStampCell.h"
#import "AccountManager.h"


@interface STInboxViewController () <STScopeSliderDelegate>

- (void)setScope:(STStampedAPIScope)scope withInstance:(STInboxViewController*)instance;

@property (nonatomic, readonly, retain) STGenericTableDelegate* tableDelegate;
@property (nonatomic, readonly, retain) STTableDelegator* tableDelegator;
@property (nonatomic, readwrite, copy) NSString* query;

@property (nonatomic, readonly, retain) STSliderScopeView* slider;
@property (nonatomic, readonly, retain) Stamps* stamps;

@end

@implementation STInboxViewController

@synthesize tableDelegate = tableDelegate_;
@synthesize tableDelegator = tableDelegator_;
@synthesize query = query_;
@synthesize slider = _slider;
@synthesize stamps = _stamps;

- (id)init {
  if (self = [super init]) {
    _stamps = [[Stamps alloc] init];
    if ([AccountManager sharedManager].currentUser == nil) {
      _stamps.scope = STStampedAPIScopeEveryone;
    } else {
      _stamps.scope = STStampedAPIScopeFriends;
    }
    
  }
  return self;
}

- (void)dealloc {
  [tableDelegate_ release];
  [tableDelegator_ release];
  [query_ release];
  
  [_stamps release];
  [_slider release];
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  
  self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
  
  [Util addHomeButtonToController:self withBadge:YES];
  [Util addCreateStampButtonToController:self];
  
  if (!_slider) {
    _slider = [[STSliderScopeView alloc] initWithFrame:CGRectMake(0, 0.0f, self.view.bounds.size.width, 54)];
    _slider.delegate = (id<STSliderScopeViewDelegate>)self;
    self.footerView = _slider;
    _slider.scope = _stamps.scope;
  }
  self.showsSearchBar = YES;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  [_slider release];
}

- (void)stampsChanged:(NSNotification *)notification {
  NSLog(@"Stamps Changed");
  [self.tableView reloadData];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  //[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(stampsChanged:) name:StampsChangedNotification object:nil];
  [self.stamps reloadData];
}

- (void)viewDidDisappear:(BOOL)animated {
  [super viewDidDisappear:animated];
  //[[NSNotificationCenter defaultCenter] removeObserver:self];
}


#pragma mark - STSliderScopeViewDelegate

- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope {
  [_stamps setScope:scope];
}


#pragma mark - UITableViewDataSouce

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {    
    return 44.0f;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return [_stamps numberOfStamps];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  
  static NSString *CellIdentifier = @"CellIdentifier";
  
  STStampCell *cell = (STStampCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier];
  }
  
  //TODO fix
  //NSString* stampID = [_stamps stampIDAtIndex:indexPath.row];
  //id<STStamp> stamp = [[STStampedAPI sharedInstance] cachedStampForStampID:stampID];
  //[cell setupWithStamp:stamp];
  
  return cell;
  
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
  //
  //NSString* stampID = [_stamps stampIDAtIndex:indexPath.row];
  //[[STStampedActions sharedInstance] viewStampWithStampID:stampID];
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
