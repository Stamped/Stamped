//
//  STRestViewController.m
//
//  Created by Devin Doty on 5/16/12.
//  Copyright (c) 2011. All rights reserved.
//

#import "STRestViewController.h"
#import "Util.h"

static CGFloat _shelfOffset = 9;

@interface STRestViewController ()

@property (nonatomic, readwrite, assign) UITableViewStyle tableStyle;
@property (nonatomic, readwrite, retain) UILabel* searchNoResultsLabel;
@property (nonatomic, readwrite, retain) UIImageView* stickyEnd;
@property (nonatomic, readwrite, retain) EGORefreshTableFooterView* footerRefreshView;
@property (nonatomic, readwrite, retain) EGORefreshTableHeaderView* headerRefreshView;
@property (nonatomic, readwrite, retain) UIView* searchOverlay;
@property (nonatomic, readwrite, retain) NoDataView* noDataView;

@property (nonatomic, readwrite, retain) UITableView *tableView;
@property (nonatomic, readwrite, retain) UITableView *searchResultsTableView;
@property (nonatomic, readwrite, retain) UIView *headerView;
@property (nonatomic, readwrite, retain) STSearchView *searchView;

@property (nonatomic, readwrite, assign) BOOL explicitRefresh;
@property (nonatomic, readwrite, assign) BOOL searching;

@property (nonatomic, readwrite, retain) UIActivityIndicatorView* loadingLockView;

@end

@implementation STRestViewController

@synthesize tableView = _tableView;
@synthesize searchResultsTableView = _searchResultsTableView;
@synthesize headerView = _headerView;
@synthesize footerView = _footerView;
@synthesize searchView = _searchView;
@synthesize noDataView = _noDataView;
@synthesize searchNoResultsLabel = _searchNoResultsLabel;
@synthesize stickyEnd = _stickyEnd;
@synthesize headerRefreshView = _headerRefreshView;
@synthesize footerRefreshView = _footerRefreshView;
@synthesize searchOverlay = _searchOverlay;
@synthesize loadingLockView = _loadingLockView;

@synthesize searching = _searching;
@synthesize showsSearchBar = _showsSearchBar;
@synthesize tableStyle = _tableStyle;
@synthesize explicitRefresh = _explicitRefresh;
@synthesize loadingLocked = _loadingLocked;

- (id)init {
    if ((self = [super initWithNibName:nil bundle:nil])) {
        _tableStyle = UITableViewStylePlain;
    }
    return self;
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}

- (void)dealloc {
    [self releaseAllViews];
    [super dealloc];
}

- (void)releaseAllViews {
    self.tableView = nil;
    self.searchResultsTableView = nil;
    self.headerView = nil;
    self.footerView = nil;
    self.searchView = nil;
    self.noDataView = nil;
    self.searchNoResultsLabel = nil;
    self.stickyEnd = nil;
    self.headerRefreshView = nil;
    self.footerRefreshView = nil;
    self.searchOverlay = nil;
    self.loadingLockView = nil;
}

- (void)setLoadingLocked:(BOOL)loadingLocked {
    if (loadingLocked != _loadingLocked) {
        _loadingLocked = loadingLocked;
        if (loadingLocked) {
            self.loadingLockView = [[[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray] autorelease];
            self.loadingLockView.frame = [Util originRectWithRect:self.view.frame];
            [self.view addSubview:self.loadingLockView];
            [self.loadingLockView startAnimating];
        }
        else {
            [self.loadingLockView removeFromSuperview];
            self.loadingLockView = nil;
        }
    }
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
    
    if (!self.tableView) {
        UITableView *tableView = [[[UITableView alloc] initWithFrame:self.view.bounds style:_tableStyle] autorelease];
        tableView.clipsToBounds = NO;
        tableView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        tableView.delegate = (id<UITableViewDelegate>)self;
        tableView.dataSource = (id<UITableViewDataSource>)self;
        [Util reframeView:self.tableView withDeltas:CGRectMake(0, _shelfOffset, 0, -_shelfOffset)];
        [self.view addSubview:tableView];
        self.tableView = tableView;
    }
    
    if (!self.headerRefreshView) {
        
        UIView *header = [[[UIView alloc] initWithFrame:CGRectMake(0.0f, -300.0f, self.view.bounds.size.width, 241.0f)] autorelease];
        header.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        header.backgroundColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
        [self.tableView addSubview:header];
        
        EGORefreshTableHeaderView *view = [[[EGORefreshTableHeaderView alloc] initWithFrame:CGRectMake(0.0f, -60.0f, self.tableView.bounds.size.width, 60.0f)] autorelease];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        view.delegate = (id<EGORefreshTableHeaderDelegate>)self;
        [self.tableView addSubview:view];
        self.headerRefreshView = view;
        
    }
    
    if (!self.footerRefreshView && _restFlags.dataSourceHasMoreData) {
        EGORefreshTableFooterView *view = [[[EGORefreshTableFooterView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.tableView.bounds.size.width, 40.0f)] autorelease];
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        self.tableView.tableFooterView = view;
        self.footerRefreshView = view;
    }
    
    if (!self.stickyEnd) {
        UIImageView *imageView = [[[UIImageView alloc] initWithImage:[[UIImage imageNamed:@"refresh_sticky_end.png"] 
                                                                      stretchableImageWithLeftCapWidth:1 
                                                                      topCapHeight:0]] autorelease];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        [self.view addSubview:imageView];
        CGRect frame = imageView.frame;
        frame.size.width = self.view.bounds.size.width;
        imageView.frame = frame;
        self.stickyEnd = imageView;
        self.stickyEnd.hidden = YES;
    }
    
    self.explicitRefresh = NO;
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
    [self releaseAllViews];
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    
    if (self.searching) {
        [self.navigationController setNavigationBarHidden:YES animated:NO];
        [self.searchResultsTableView deselectRowAtIndexPath:self.searchResultsTableView.indexPathForSelectedRow animated:YES];
    } else {
        [self.tableView deselectRowAtIndexPath:self.tableView.indexPathForSelectedRow animated:YES];
        if (self.showsSearchBar && CGPointEqualToPoint(self.tableView.contentOffset, CGPointZero)) {
            //[self.tableView setContentOffset:CGPointMake(0.0f, 49.0f)];
        }
    }
    
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillShow:) name:UIKeyboardWillShowNotification  object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillHide:) name:UIKeyboardWillHideNotification object:nil];

}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];
    if (self.searching) {
        [self.navigationController setNavigationBarHidden:NO animated:NO];
    }
    [[NSNotificationCenter defaultCenter] removeObserver:self name:UIKeyboardWillShowNotification  object:nil];
    [[NSNotificationCenter defaultCenter] removeObserver:self name:UIKeyboardWillHideNotification object:nil];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    if (!self.searching && self.showsSearchBar && CGPointEqualToPoint(self.tableView.contentOffset, CGPointZero)) {
        //[self.tableView setContentOffset:CGPointMake(0.0f, 49.0f)];
    }
}


#pragma mark - Cell Animation

- (void)animateView:(UIView*)view withDelay:(float)delay {
    
    view.layer.opacity = 0.0f;
    
    [CATransaction begin];
    [CATransaction setCompletionBlock:^{
        view.layer.opacity = 1.0f;
        [view.layer removeAllAnimations];
    }];
    
    CAAnimationGroup *animation = [CAAnimationGroup animation];
    animation.duration = 0.3f;
    animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
    animation.beginTime = [view.layer convertTime:CACurrentMediaTime() fromLayer:nil] + delay;
    animation.removedOnCompletion = NO;
    animation.fillMode = kCAFillModeForwards;
    
    CABasicAnimation *position = [CABasicAnimation animationWithKeyPath:@"position"];
    position.fromValue = [NSValue valueWithCGPoint:CGPointMake(view.layer.position.x, view.layer.position.y + self.tableView.frame.size.height)];
    
    CAKeyframeAnimation *opacity = [CAKeyframeAnimation animationWithKeyPath:@"opacity"];
    opacity.values = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.0f], [NSNumber numberWithFloat:1.0f], [NSNumber numberWithFloat:1.0f], nil];
    opacity.keyTimes = [NSArray arrayWithObjects:[NSNumber numberWithFloat:0.0f], [NSNumber numberWithFloat:0.01f], [NSNumber numberWithFloat:1.0f], nil];
    
    [animation setAnimations:[NSArray arrayWithObjects:position, opacity, nil]];
    [view.layer addAnimation:animation forKey:nil];
    [CATransaction commit];
    
}

- (void)animateIn {
    
    float delay = 0.0f;
    for (UITableViewCell *cell in self.tableView.visibleCells) {
        [self animateView:cell withDelay:delay];
        delay += 0.15f;
    }
    
}


#pragma mark - TableView Layout

- (void)layoutTableView {
    
    CGFloat origin = 0.0f;
    CGFloat height = self.view.bounds.size.height;
    
    if (self.headerView) {
        origin = self.headerView.bounds.size.height;
        height -= self.headerView.bounds.size.height;
    }
    
    if (self.footerView) {
        height -= self.footerView.bounds.size.height;
    }
    
    CGRect frame = self.tableView.frame;
    self.tableView.clipsToBounds = NO;
    frame.origin.y = origin + _shelfOffset;
    frame.size.height = height - _shelfOffset;
    self.tableView.frame = frame;
    
}


#pragma mark - Setters

- (void)setContentInset:(UIEdgeInsets)inset {
    self.tableView.contentInset = inset;
    self.tableView.scrollIndicatorInsets = inset;
    self.headerRefreshView.tableInset = inset;

    if (self.searchResultsTableView) {
        self.searchResultsTableView.contentInset = inset;
        self.searchResultsTableView.scrollIndicatorInsets = inset;
    }
    
}

- (void)setHeaderView:(UIView *)headerView {
    
    // remove old header
    if (_headerView) {
        [_headerView removeFromSuperview];
        [_headerView autorelease];
        _headerView = nil;
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
        [_footerView autorelease];
        _footerView = nil;
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
    
    if (_showsSearchBar) {
        
        if (!self.searchView) {
            
            STSearchView *view = [[STSearchView alloc] initWithFrame:CGRectMake(0, 0, self.view.bounds.size.width, 52)];
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
            view.delegate = (id<STSearchViewDelegate>)self;
            self.tableView.tableHeaderView = view;
            self.searchView = view;
            [view release];
            
            self.tableView.contentOffset = CGPointMake(0.0f, -140.0f);
            
        }
        
    } else {
        
        if (self.searchView) {
            self.searchView = nil;
            self.tableView.tableHeaderView = nil;
        }
        
    }
    
    self.headerRefreshView.showingSearch = _showsSearchBar;
}


#pragma mark - Rest Methods

- (void)setState {
	
	[self.headerRefreshView updateRefreshState:self.tableView];
    
    if (_restFlags.dataSourceReloading) {	
		if ([[self.tableView tableFooterView] isKindOfClass:[EGORefreshTableFooterView class]] && self.footerRefreshView) {
            if (!self.explicitRefresh) {
                [self.footerRefreshView setLoading:[(id<STRestController>)self dataSourceReloading]];
            }
		}
	} 
	
	BOOL empty = NO;
	if (_restFlags.dataSourceIsEmpty) {
		empty = [(id<STRestController>)self  dataSourceIsEmpty];
	}

	if (!empty || [(id<STRestController>)self dataSourceReloading]) {
		
        self.tableView.scrollEnabled = YES;
		if (self.noDataView!=nil) {
            [self.noDataView removeFromSuperview];
            self.noDataView = nil;
        }
		
	} else {
		
		if (self.noDataView==nil) {
            
            CGFloat yOffset = self.tableView.tableHeaderView ? self.tableView.tableHeaderView.bounds.size.height : 0.0f;
			NoDataView *view = [[NoDataView alloc] initWithFrame:CGRectMake(0.0f, yOffset, self.tableView.frame.size.width, floorf(self.tableView.frame.size.height))];
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
            view.backgroundColor = self.tableView.backgroundColor;
			[self.tableView addSubview:view];
			view.alpha = 0.01f;
			self.noDataView = view;
            view=nil;
			
		}
		
		[UIView animateWithDuration:0.2f animations:^{
			self.noDataView.alpha = 1.0f;
		}];
		
		if (_restFlags.dataSourceSetupNoDataView) {
			[(id<STRestController>)self setupNoDataView:_noDataView];
		}
		
	}
    
}

- (void)reloadDataSource {
    
    [self.headerRefreshView updateRefreshState:self.tableView];
    [self setState];
    self.explicitRefresh = NO;

}

- (void)dataSourceDidFinishLoading {
    
    self.explicitRefresh = NO;
	[self.headerRefreshView egoRefreshScrollViewDataSourceDidFinishedLoading:self.tableView];
	[self setState];
    
    if (self.searching) {
        [self updateSearchState];
    }
    
}


#pragma mark - UIScrollViewDelegate

- (void)scrollViewDidScroll:(UIScrollView*)scrollView {
    if (scrollView != self.tableView) return;
    
    BOOL hidden = scrollView.contentOffset.y <= 49.0f;
    if (self.stickyEnd.hidden != hidden) {
        self.stickyEnd.hidden = hidden;
    }
    [self.headerRefreshView egoRefreshScrollViewDidScroll:scrollView];
    if (_restFlags.dataSourceLoadNextPage && _restFlags.dataSourceHasMoreData && _restFlags.dataSourceReloading) {
        if (![(id<STRestController>)self dataSourceReloading] &&
            scrollView.contentOffset.y >= ((scrollView.contentSize.height - (scrollView.frame.size.height*2)) -10) &&
            [(id<STRestController>)self dataSourceHasMoreData]) {
            [(id<STRestController>)self loadNextPage];
            [self setState];
        }
    }
    
}

- (void)scrollViewWillEndDragging:(UIScrollView *)scrollView withVelocity:(CGPoint)velocity targetContentOffset:(inout CGPoint *)targetContentOffset {
    if (scrollView != self.tableView) {
        return;
    }

    if (scrollView.contentOffset.y < 0.0f) {
        [self.headerRefreshView egoRefreshScrollViewDidEndDragging:scrollView];
    }
    
}


#pragma mark - EGORefreshTableHeaderDelegate

- (void)egoRefreshTableHeaderDidTriggerRefresh:(EGORefreshTableHeaderView*)view {
	
	if (_restFlags.dataSourceReloadDataSource) {
        self.explicitRefresh = YES;
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

- (void)updateSearchState {
    
    if (self.searchResultsTableView) {
        
        NSInteger count = [self.searchResultsTableView numberOfRowsInSection:0];
        
        if (count == 0 && self.searchOverlay!=nil && self.searchOverlay.hidden) {
            
            // no results
            if (!self.searchNoResultsLabel) {
                
                UILabel *label = [[[UILabel alloc] initWithFrame:CGRectZero] autorelease];
                label.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
                label.font = [UIFont boldSystemFontOfSize:15];
                label.backgroundColor = [UIColor clearColor];
                label.textColor = [UIColor grayColor];
                label.text = @"";
                //label.text = NSLocalizedString(@"No results.", @"No results.");
                [label sizeToFit];
                [self.searchResultsTableView addSubview:label];
                self.searchNoResultsLabel = label;
                
                CGRect frame = label.frame;
                frame.origin.x = floorf((self.view.bounds.size.width-label.bounds.size.width)/2);
                frame.origin.y = 58.0f;
                label.frame = frame;
                
            }
            
        }
        else {
            
            // has results
            if (self.searchNoResultsLabel) {
                [self.searchNoResultsLabel removeFromSuperview];
                self.searchNoResultsLabel = nil;
            }
            
        }
        
    }
    
}

- (void)overlayTapped:(UITapGestureRecognizer*)gesture {
    
    [self.searchView cancelSearch];
    
}

- (void)setSearching:(BOOL)searching {
    _searching = searching;
    
    [self.navigationController setNavigationBarHidden:_searching animated:YES];
    self.tableView.contentOffset = CGPointZero;
    self.tableView.scrollEnabled = !_searching;
    
    if (_searching) {
        
        CGFloat barHeight = self.searchView.bounds.size.height;
        
        if (!self.searchResultsTableView) {
            
            UITableView *tableView = [[[UITableView alloc] initWithFrame:CGRectMake(0.0f, 
                                                                                   self.searchView.bounds.size.height, 
                                                                                   self.view.bounds.size.width, 
                                                                                   self.view.bounds.size.height - _searchView.bounds.size.height) 
                                                                  style:UITableViewStylePlain] autorelease];
            tableView.delegate = (id<UITableViewDelegate>)self;
            tableView.dataSource = (id<UITableViewDataSource>)self;
            [self.view addSubview:tableView];
            self.searchResultsTableView = tableView;
            self.searchResultsTableView.hidden = YES;
            
        }
        
        if (!self.searchOverlay) {
            
            UIView *view = [[[UIView alloc] initWithFrame:CGRectMake(0.0f,
                                                                     barHeight,
                                                                     self.view.bounds.size.width, 
                                                                     self.view.bounds.size.height - barHeight)] autorelease];
            [self.view addSubview:view];
            self.searchOverlay = view;

            UIColor *color = [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.5f];
            CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"backgroundColor"];
            animation.fromValue = (id)[UIColor clearColor].CGColor;
            animation.toValue = (id)color.CGColor;
            animation.duration = 0.3f;
            animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
            [self.searchOverlay.layer addAnimation:animation forKey:nil];
            self.searchOverlay.layer.backgroundColor = color.CGColor;
            
            UITapGestureRecognizer *gesture = [[[UITapGestureRecognizer alloc] initWithTarget:self 
                                                                                       action:@selector(overlayTapped:)] autorelease];
            [self.searchOverlay addGestureRecognizer:gesture];
            
        }
        
    } 
    else {
        
        if (self.searchOverlay) {
            
            UIView *view = self.searchOverlay;
            self.searchOverlay = nil;
            
            [CATransaction begin];
            [CATransaction setAnimationDuration:0.3f];
            [CATransaction setCompletionBlock:^{
                [view removeFromSuperview];
            }];
            
            CGColorRef cgColor = view.layer.backgroundColor;
            CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"backgroundColor"];
            animation.fromValue = (id)cgColor;
            animation.toValue = (id)[UIColor clearColor].CGColor;
            animation.duration = 0.3f;
            animation.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
            [view.layer addAnimation:animation forKey:nil];
            view.layer.backgroundColor = [UIColor clearColor].CGColor;

            [CATransaction commit];
            
        }
        [self updateSearchState];
        
        if (self.searchResultsTableView) {
            [self.searchResultsTableView removeFromSuperview];
            self.searchResultsTableView = nil;
        }
        
    }
    
    self.searchView.showCancelButton = _searching;
    
}


#pragma mark - STSearchViewDelegate

- (void)stSearchViewDidCancel:(STSearchView*)view {
     
    [self setSearching:NO];

}

- (void)stSearchViewDidBeginSearching:(STSearchView*)view {
    
    [self setSearching:YES];
    
}

- (void)stSearchViewDidEndSearching:(STSearchView*)view {
    

}

- (void)stSearchView:(STSearchView*)view textDidChange:(NSString*)text {
    
    if (self.searchOverlay) {
        self.searchOverlay.hidden = (text!=nil && [text stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]].length > 0);
        self.searchResultsTableView.hidden = !self.searchOverlay.hidden;
    }
    
    [self updateSearchState];
    
}

- (void)setShowSearchTable:(BOOL)visible {
    self.searchOverlay.hidden = !visible;
    self.searchResultsTableView.hidden = visible;
}

#pragma mark - UIKeyboard Notfications

- (void)keyboardWillShow:(NSNotification*)notification {    
    
    CGRect keyboardFrame = [[[notification userInfo] objectForKey:UIKeyboardFrameEndUserInfoKey] CGRectValue];
    [UIView animateWithDuration:0.3 delay:0 options:UIViewAnimationCurveEaseOut animations:^{
        [self setContentInset:UIEdgeInsetsMake(self.tableView.contentInset.top, 0, keyboardFrame.size.height, 0)];
    } completion:^(BOOL finished){}];
    
}

- (void)keyboardWillHide:(NSNotification*)notification {
    
    [UIView animateWithDuration:0.3 animations:^{
        [self setContentInset:UIEdgeInsetsMake(self.tableView.contentInset.top, 0, 0, 0)];
    }];
    
}


@end
