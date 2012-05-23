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
#import "STTableDelegator.h"
#import "STSingleViewSource.h"
#import "STSearchField.h"
#import "STEveryoneStampsList.h"
#import "STSliderScopeView.h"
#import "STStampedActions.h"

#import "EntityDetailViewController.h"
#import "STStampCell.h"
#import "AccountManager.h"


@interface STInboxViewController ()

@property (nonatomic, readonly, retain) STSliderScopeView *slider;
@property (nonatomic, readonly, retain) Stamps *stamps;
@property (nonatomic, readonly, retain) Stamps *searchStamps;

@end

@implementation STInboxViewController

@synthesize slider = _slider;
@synthesize stamps = _stamps;
@synthesize searchStamps = _searchStamps;

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
    
    if (_searchStamps) {
        [_searchStamps release], _searchStamps=nil;
    }
    [_stamps release], _stamps=nil;
    [_slider release], _slider=nil;
    
    [[NSNotificationCenter defaultCenter] removeObserver:self];
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
    
    NSInteger sections = [self.tableView numberOfSections];
    if (sections == 0 && ![_stamps isEmpty]) {
        
        [self.tableView beginUpdates];
        [self.tableView insertSections:[NSIndexSet indexSetWithIndex:0] withRowAnimation:UITableViewRowAnimationFade];
        [self.tableView endUpdates];
        
    } else {
        
        [self.tableView reloadData];

    }

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

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    
    if (tableView == _searchResultsTableView) {
        return [_searchStamps isEmpty] ? 0 : 1;
    }
    
    return [_stamps isEmpty] ? 0 : 1;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return [(tableView == _searchResultsTableView) ? _stamps : _searchStamps  numberOfStamps];
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  
    static NSString *CellIdentifier = @"CellIdentifier";
    
    STStampCell *cell = (STStampCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    //TODO fix
    //NSString* stampID = [_stamps stampIDAtIndex:indexPath.row];
    //id<STStamp> stamp = [[STStampedAPI sharedInstance] cachedStampForStampID:stampID];
    //[cell setupWithStamp:stamp];
    
    id<STStamp> stamp = [(tableView == _searchResultsTableView) ? _stamps : _searchStamps stampAtIndex:indexPath.row];
    [cell setupWithStamp:stamp];
    
    return cell;
  
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {

    //NSString* stampID = [_stamps stampIDAtIndex:indexPath.row];
    //[[STStampedActions sharedInstance] viewStampWithStampID:stampID];
    
    id<STStamp> stamp = [(tableView == _searchResultsTableView) ? _stamps : _searchStamps  stampAtIndex:indexPath.row];
    [[STStampedActions sharedInstance] viewStampWithStampID:stamp.stampID];
    
}


#pragma mark STSearchViewDelegate

- (void)stSearchViewDidCancel:(STSearchView*)view {
    [super stSearchViewDidCancel:view];
    
    // cancel model query
    
}

- (void)stSearchViewDidEndSearching:(STSearchView*)view {
    [super stSearchViewDidEndSearching:view];
    
    if (_searchStamps) {
        [_searchStamps release], _searchStamps=nil;
    }
    
}

- (void)stSearchViewDidBeginSearching:(STSearchView *)view {
    [super stSearchViewDidBeginSearching:view];
    
    if (!_searchStamps) {
        _searchStamps = [[Stamps alloc] init];
    }
    
}

- (void)stSearchView:(STSearchView*)view textDidChange:(NSString*)text {
    [super stSearchView:view textDidChange:text];
    _stamps.searchQuery = text;
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
