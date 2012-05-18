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

@protocol STRestController;

@class STSearchView;
@interface STRestViewController : UIViewController <UITextFieldDelegate> {
    
    UITableViewStyle _tableStyle;
    UITableView *_tableView;
    EGORefreshTableFooterView *_footerRefreshView;
    EGORefreshTableHeaderView *_headerRefreshView;
    UIView *_searchOverlay;
    NoDataView *_noDataView;
    
    BOOL _explicitRefresh;
    BOOL _searching;
       
    struct {
        unsigned int dataSourceReloading:1;
        unsigned int dataSourceLoadNextPage:1;
        unsigned int dataSourceHasMoreData:1;
        unsigned int dataSourceReloadDataSource:1;
        unsigned int dataSourceIsEmpty:1;
        unsigned int dataSourceSetupNoDataView:1;
    } _restFlags;
    
}

@property(strong, nonatomic) UITableView *tableView;
@property(strong, nonatomic) UIView *headerView;
@property(strong, nonatomic) UIView *footerView;
@property(readonly, nonatomic) STSearchView *searchView;
@property(nonatomic, assign, getter = isShowingSearch) BOOL showsSearchBar;

- (void)setContentInset:(UIEdgeInsets)inset;
- (void)scrollViewDidScroll:(UIScrollView*)scrollView;

- (void)reloadDataSource;
- (void)dataSourceDidFinishLoading;

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
