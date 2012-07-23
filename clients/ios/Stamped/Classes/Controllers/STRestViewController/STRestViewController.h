//
//  GiftureRestTableViewController.h
//  Gifture
//
//  Created by Devin Doty on 5/16/12.
//  Copyright (c) 2011. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "EGORefreshTableHeaderView.h"
#import "EGORefreshTableFooterView.h"
#import "NoDataView.h"
#import "STSearchView.h"

@protocol STRestController;

@interface STRestViewController : UIViewController <STSearchViewDelegate> {
    struct {
        unsigned int dataSourceReloading:1;
        unsigned int dataSourceLoadNextPage:1;
        unsigned int dataSourceHasMoreData:1;
        unsigned int dataSourceReloadDataSource:1;
        unsigned int dataSourceIsEmpty:1;
        unsigned int dataSourceSetupNoDataView:1;
    } _restFlags;
    
}

@property (nonatomic, readonly, retain) UITableView *tableView;
@property (nonatomic, readonly, retain) UITableView *searchResultsTableView;
@property (nonatomic, readonly, retain) UIView *headerView;
@property (nonatomic, readwrite, retain) UIView *footerView;
@property (nonatomic, readonly, retain) STSearchView *searchView;
@property (nonatomic, assign, getter = isShowingSearch) BOOL showsSearchBar;
@property (nonatomic, readonly, getter = isSearching) BOOL searching;

- (void)setShowSearchTable:(BOOL)visible;

- (void)setContentInset:(UIEdgeInsets)inset;
- (void)scrollViewDidScroll:(UIScrollView*)scrollView;

- (void)reloadDataSource;
- (void)dataSourceDidFinishLoading;
- (void)animateIn;
- (void)layoutTableView;

@end

@protocol STRestController <NSObject>
@optional
- (BOOL)dataSourceReloading;
- (void)loadNextPage;
- (BOOL)dataSourceHasMoreData;
- (void)reloadDataSource;
- (BOOL)dataSourceIsEmpty;
- (void)setupNoDataView:(NoDataView*)view;
@end
