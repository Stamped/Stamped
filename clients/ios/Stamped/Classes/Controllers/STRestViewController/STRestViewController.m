//
//  STRestViewController.m
//
//  Created by Devin Doty on 5/16/12.
//  Copyright (c) 2011. All rights reserved.
//

#import "STRestViewController.h"
#import "STSearchView.h"

@implementation STRestViewController

@synthesize tableView=_tableView;
@synthesize footerView=_footerView;
@synthesize headerView=_headerView;
@synthesize showsSearchBar=_showsSearchBar;
@synthesize searchView=_searchView;

- (id)init {
    if ((self = [super init])) {
        _tableStyle = UITableViewStylePlain;
    }
    return self;
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}

- (void)dealloc {
    [_tableView release], _tableView=nil;
    [_headerView release], _headerView=nil;
    [_footerView release], _footerView=nil;
    _headerRefreshView = nil;
    _footerRefreshView = nil;
    _searchView = nil;
    [super dealloc];
}


#pragma mark - View lifecycle

- (void)viewDidLoad {
    [super viewDidLoad];
    
    _restFlags.dataSourceReloading = [self respondsToSelector:@selector(dataSourceReloading)];
    _restFlags.dataSourceLoadNextPage = [self respondsToSelector:@selector(loadNextPage)];
    _restFlags.dataSourceHasMoreData = [self respondsToSelector:@selector(dataSourceHasMoreData)];
    _restFlags.dataSourceReloadDataSource = [self respondsToSelector:@selector(reloadDataSource)];
    _restFlags.dataSourceIsEmpty = [self respondsToSelector:@selector(dataSourceIsEmpty)];
    _restFlags.dataSourceSetupNoDataView = [self respondsToSelector:@selector(setupNoDataView:)];
    
    if (!_tableView) {
        UITableView *tableView = [[UITableView alloc] initWithFrame:self.view.bounds style:_tableStyle];
        tableView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [self.view addSubview:tableView];
        _tableView = [tableView retain];
        [tableView release];
    }
    
    if (!_headerRefreshView) {
        EGORefreshTableHeaderView *view = [[EGORefreshTableHeaderView alloc] initWithFrame:CGRectMake(0.0f, -60.0f, self.tableView.bounds.size.width, 60.0f)];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        view.delegate = (id<EGORefreshTableHeaderDelegate>)self;
        [self.tableView addSubview:view];
        _headerRefreshView = view; 
        [view release];
    }
    
    if (!_footerRefreshView && _restFlags.dataSourceHasMoreData) {
        EGORefreshTableFooterView *view = [[EGORefreshTableFooterView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.tableView.bounds.size.width, 40.0f)];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableView.tableFooterView = view;
        _footerRefreshView = view;
        [view release];
    }
    
    _explicitRefresh = NO;
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
    _footerRefreshView=nil;
    _headerRefreshView=nil;
    _searchView=nil;
    self.tableView.tableHeaderView = nil;
    self.tableView=nil;
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow animated:YES];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillShow:) name:UIKeyboardWillShowNotification  object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillHide:) name:UIKeyboardWillHideNotification object:nil];
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];
    [[NSNotificationCenter defaultCenter] removeObserver:self name:UIKeyboardWillShowNotification  object:nil];
    [[NSNotificationCenter defaultCenter] removeObserver:self name:UIKeyboardWillHideNotification object:nil];
}


#pragma mark - TableView Layout

- (void)layoutTableView {
    
    CGFloat origin = 0.0f;
    CGFloat height = self.view.bounds.size.height;
    
    if (_headerView) {
        origin = _headerView.bounds.size.height;
        height -= _headerView.bounds.size.height;
    }
    
    if (_footerView) {
        height -= _footerView.bounds.size.height;
    }
    
    CGRect frame = self.tableView.frame;
    frame.origin.y = origin;
    frame.size.height = height;
    self.tableView.frame = frame;
    
}


#pragma mark - Setters

- (void)setContentInset:(UIEdgeInsets)inset {
    self.tableView.contentInset = inset;
    self.tableView.scrollIndicatorInsets = inset;
    _headerRefreshView.tableInset = inset;
}

- (void)setHeaderView:(UIView *)headerView {
    
    // remove old header
    if (_headerView) {
        [_headerView removeFromSuperview];
        [_headerView release], _headerView=nil;
    }
    
    // add header
    if (headerView) {
        _headerView = [headerView retain];
        [self.view addSubview:_headerView];
        _headerView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin;
        
        CGRect frame = _headerView.frame;
        frame.origin.y = 0.0f;
        frame.size.width = self.view.bounds.size.width;
        _headerView.frame = frame;
        
    }
    [self layoutTableView];

}

- (void)setFooterView:(UIView *)footerView {
    
    if (_footerView) {
        [_footerView removeFromSuperview];
        [_footerView release], _footerView=nil;
    }
    
    if (footerView) {
        _footerView = [footerView retain];
        [self.view addSubview:_footerView];
        _footerView.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleWidth;
        
        CGRect frame = _footerView.frame;
        frame.origin.y = self.view.bounds.size.height - _footerView.bounds.size.height;
        frame.size.width = self.view.bounds.size.width;
        _footerView.frame = frame;

    }
    
    [self layoutTableView];
}

- (void)setShowsSearchBar:(BOOL)showsSearchBar {
    _showsSearchBar = showsSearchBar;
    
    if (!_searchView) {
        
        STSearchView *view = [[STSearchView alloc] initWithFrame:CGRectMake(0, 0, self.view.bounds.size.width, 52)];
        view.backgroundColor = [UIColor colorWithPatternImage:[[UIImage imageNamed:@"search_bg.png"] stretchableImageWithLeftCapWidth:1 topCapHeight:0]];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        view.textField.delegate = self;
        self.tableView.tableHeaderView = view;
        _searchView = view;
        [view release];

        self.tableView.contentOffset = CGPointMake(0.0f, -140.0f);

    }
    
}


#pragma mark - Rest Methods

- (void)setState {
	
	[_headerRefreshView updateRefreshState:self.tableView];
    
    if (_restFlags.dataSourceReloading) {	
		if ([[self.tableView tableFooterView] isKindOfClass:[EGORefreshTableFooterView class]] && _footerRefreshView) {
            if (!_explicitRefresh) {
                [_footerRefreshView setLoading:[(id<STRestController>)self dataSourceReloading]];
            }
		}
	} 
	
	BOOL _empty = NO;
	if (_restFlags.dataSourceIsEmpty) {
		_empty = [(id<STRestController>)self  dataSourceIsEmpty];
	}

	if (!_empty || [(id<STRestController>)self dataSourceReloading]) {
		
		if (_noDataView!=nil) {
            [_noDataView removeFromSuperview], _noDataView=nil;
		}
		
	} else {
		
		if (_noDataView==nil) {
            
            CGFloat yOffset = self.tableView.tableHeaderView ? self.tableView.tableHeaderView.bounds.size.height : 0.0f;
			NoDataView *view = [[NoDataView alloc] initWithFrame:CGRectMake(0.0f, yOffset, self.tableView.frame.size.width, floorf(self.tableView.frame.size.height - yOffset))];
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
            view.backgroundColor = self.tableView.backgroundColor;
			[self.tableView addSubview:view];
			view.alpha = 0.01f;
			_noDataView = view;
            view=nil;
			
		}
		
		[UIView animateWithDuration:0.2f animations:^{
			_noDataView.alpha = 1.0f;
		}];
		
		if (_restFlags.dataSourceSetupNoDataView) {
			[(id<STRestController>)self setupNoDataView:_noDataView];
		}
		
	}
    
}

- (void)reloadDataSource {
    
    [_headerRefreshView updateRefreshState:self.tableView];
    [self setState];
    _explicitRefresh = NO;

}

- (void)dataSourceDidFinishLoading {

    _explicitRefresh = NO;
	[_headerRefreshView egoRefreshScrollViewDataSourceDidFinishedLoading:self.tableView];
	[self setState];

}


#pragma mark - UIScrollViewDelegate

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
    
    [_headerRefreshView egoRefreshScrollViewDidScroll:scrollView];
    if (_restFlags.dataSourceLoadNextPage && _restFlags.dataSourceHasMoreData && _restFlags.dataSourceReloading) {
        if (![(id<STRestController>)self dataSourceReloading] && scrollView.contentOffset.y >= ((scrollView.contentSize.height - (scrollView.frame.size.height*2)) -10) && [(id<STRestController>)self dataSourceHasMoreData]) {
            [(id<STRestController>)self loadNextPage];
            [self setState];
        }
    }
    
}

- (void)scrollViewWillEndDragging:(UIScrollView *)scrollView withVelocity:(CGPoint)velocity targetContentOffset:(inout CGPoint *)targetContentOffset {
    
    if (scrollView.contentOffset.y < 0.0f) {
        [_headerRefreshView egoRefreshScrollViewDidEndDragging:scrollView];
    }
    
}


#pragma mark - EGORefreshTableHeaderDelegate

- (void)egoRefreshTableHeaderDidTriggerRefresh:(EGORefreshTableHeaderView*)view {
	
	if (_restFlags.dataSourceReloadDataSource) {
        _explicitRefresh = YES;
		return [self reloadDataSource];
	}
	
}

- (BOOL)egoRefreshTableHeaderDataSourceIsLoading:(EGORefreshTableHeaderView*)view {
	
	if (_restFlags.dataSourceReloading) {
		return [(id<STRestController>)self dataSourceReloading];
	}
	
	return NO; // should return if data source model is reloading
	
}


#pragma mark - Search State Methods (internal)

- (void)overlayTapped:(UITapGestureRecognizer*)gesture {
    
    [self setSearching:NO];
    
}

- (void)setSearching:(BOOL)searching {
    _searching = searching;
    
    [self.navigationController setNavigationBarHidden:_searching animated:YES];
    
    if (_searching) {
        
        CGFloat barHeight = _searchView.bounds.size.height;

        self.tableView.contentOffset = CGPointMake(0.0f, -barHeight);
        
        if (!_searchOverlay) {
            
            UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, barHeight, self.view.bounds.size.width, self.view.bounds.size.height - barHeight)];
            [self.view addSubview:view];
            _searchOverlay = view;
            [view release];

            UIColor *color = [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.5f];
            CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"backgroundColor"];
            animation.fromValue = (id)[UIColor clearColor].CGColor;
            animation.toValue = (id)color.CGColor;
            animation.duration = 0.25f;
            animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
            [_searchOverlay.layer addAnimation:animation forKey:nil];
            _searchOverlay.layer.backgroundColor = color.CGColor;
            
            UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(overlayTapped:)];
            [_searchOverlay addGestureRecognizer:gesture];
            [gesture release];
            
        }
        
    } else {
        
        [_searchView.textField resignFirstResponder];
        
        if (_searchOverlay) {
            
            __block UIView *view = _searchOverlay;
            _searchOverlay = nil;
            
            [CATransaction begin];
            [CATransaction setAnimationDuration:0.25f];
            [CATransaction setCompletionBlock:^{
                [view removeFromSuperview];
            }];
            
            CGColorRef cgColor = view.layer.backgroundColor;
            CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"backgroundColor"];
            animation.fromValue = (id)cgColor;
            animation.toValue = (id)[UIColor clearColor].CGColor;
            animation.duration = 0.25f;
            animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
            [view.layer addAnimation:animation forKey:nil];
            view.layer.backgroundColor = [UIColor clearColor].CGColor;

            [CATransaction commit];
            
        }
        
    }
    
    
}


#pragma mark - UIKeyboard Notfications

- (void)keyboardWillShow:(NSNotification*)notification {    
    
    CGRect keyboardFrame = [[[notification userInfo] objectForKey:UIKeyboardFrameEndUserInfoKey] CGRectValue];
    [UIView animateWithDuration:0.3 delay:0 options:UIViewAnimationCurveEaseOut animations:^{
        [self setContentInset:UIEdgeInsetsMake(0, 0, keyboardFrame.size.height - 50.0f, 0)];
    } completion:^(BOOL finished){}];
    
}

- (void)keyboardWillHide:(NSNotification*)notification {
    
    [UIView animateWithDuration:0.3 animations:^{
        [self setContentInset:UIEdgeInsetsZero];
    }];
    
}


#pragma mark - UITextFieldDelegate 

- (BOOL)textFieldShouldBeginEditing:(UITextField *)textField {
    
    return YES;
}

- (void)textFieldDidBeginEditing:(UITextField *)textField {
    
    [self setSearching:YES];
    
}

- (BOOL)textFieldShouldEndEditing:(UITextField *)textField {
    
    return YES;
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
    
}

- (BOOL)textFieldShouldClear:(UITextField *)textField {
    
    return YES;
}

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    
    return YES;
}



@end
