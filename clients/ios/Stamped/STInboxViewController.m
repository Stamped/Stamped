//
//  STInboxViewController.m
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STInboxViewController.h"
#import "STToolbarView.h"
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
#import "STCache.h"
#import "STSharedCaches.h"

#import "EntityDetailViewController.h"
#import "STStampCell.h"
#import "DDMenuController.h"
#import "STActionManager.h"
#import "FindFriendsViewController.h"
#import "STMenuController.h"
#import "STUserViewController.h"

@interface STInboxViewController ()

@property (nonatomic, readonly, retain) STSliderScopeView *slider;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readwrite, copy) NSString* searchQuery;
@property (nonatomic, readwrite, retain) STCache* cache;
@property (nonatomic, readwrite, retain) STCacheSnapshot* snapshot;
@property (nonatomic, readwrite, retain) NSArray<STStamp>* searchResults;
@property (nonatomic, readwrite, assign) BOOL reloading;

@end

@implementation STInboxViewController

@synthesize slider = _slider;
@synthesize scope = _scope;
@synthesize searchQuery = _searchQuery;
@synthesize cache = _cache;
@synthesize snapshot = _snapshot;
@synthesize searchResults = _searchResults;
@synthesize reloading = _reloading;

- (id)init {
  if (self = [super init]) {
      
      [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(logginStatusChanged:) name:STStampedAPILoginNotification object:nil];
      [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(logginStatusChanged:) name:STStampedAPILogoutNotification object:nil];
      [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheUpdate:) name:STCacheDidChangeNotification object:nil];
      [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheWillLoadPage:) name:STCacheWillLoadPageNotification object:nil];
      [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheDidLoadPage:) name:STCacheDidLoadPageNotification object:nil];

      if ([STStampedAPI sharedInstance].currentUser == nil) {
          _scope = STStampedAPIScopeEveryone;
      } else {
          _scope = STStampedAPIScopeFriends;
      }
      _searchQuery = nil;
      _reloading = YES;
      self.showsSearchBar = NO;
  }
  return self;
}

- (void)dealloc {
    
    [_slider release], _slider=nil;
    
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
  
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];

    if (!LOGGED_IN) {
        
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Sign in" style:UIBarButtonItemStyleBordered target:self action:@selector(login:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
        
    } else {
        
        [Util addCreateStampButtonToController:self];

    }
        
    if (!_slider) {
        _slider = [[STSliderScopeView alloc] initWithFrame:CGRectMake(0, 0.0f, self.view.bounds.size.width, 54)];
        _slider.delegate = (id<STSliderScopeViewDelegate>)self;
        _slider.dataSource = (id<STSliderScopeViewDataSource>)self;
        self.footerView = _slider;
        _slider.scope = self.scope;
    }
    
    [self.searchView setPlaceholderTitle:@"Search stamps"];
    [self.tableView reloadData];
    [self updateCache];
    
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
    [_slider release];
}

- (void)viewDidAppear:(BOOL)animated {
    //Resume cache ops
}

- (void)viewDidDisappear:(BOOL)animated {
    //Todo cancel pending cache ops
    [super viewDidDisappear:animated];
}


#pragma mark - Actions

- (void)login:(id)sender {

    STMenuController *controller = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [controller showSignIn];
    
}


#pragma mark - Cache Methods

- (void)updateCache {
    self.cache = nil;
    self.snapshot = nil;
    STCache* fastCache = [STSharedCaches cacheForInboxScope:self.scope];
    if (!fastCache) {
        [STSharedCaches cacheForInboxScope:self.scope withCallback:^(STCache *cache, NSError *error, STCancellation *cancellation) {
            if (cache) {
                //Fast cache will be set this time
                [self updateCache];
            }
        }];
    }
    else {
        self.cache = fastCache;
        self.snapshot = self.cache.snapshot;
        [self reloadDataSource];
    }
    [self.tableView reloadData];
}

- (void)cacheWillLoadPage:(NSNotification *)notification {
    self.reloading = YES;
    [self.tableView reloadData];
}

- (void)cacheDidLoadPage:(NSNotification *)notification {
    self.reloading = NO;
    [self dataSourceDidFinishLoading];
    [self.tableView reloadData];
}

- (void)cacheUpdate:(NSNotification *)notification {
    if (self.cache) {
        self.snapshot = self.cache.snapshot;
        [self.tableView reloadData];
    }
}


#pragma mark - STSliderScopeViewDelegate

- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope {
    self.scope = scope;
    [self updateCache];
    if (self.showsSearchBar) {
        [self.tableView setContentOffset:CGPointMake(0.0f, self.searchView.bounds.size.height-2.0f)];
    }
}


#pragma mark - STSliderScopeViewDataSource

- (NSString*)sliderScopeView:(STSliderScopeView*)slider titleForScope:(STStampedAPIScope)scope {
    
    switch (scope) {
        case STStampedAPIScopeYou:
            return @"you";
            break;
        case STStampedAPIScopeFriends:
            return @"friends";
            break;
        case STStampedAPIScopeEveryone:
            return @"tastemakers";
            break;
        default:
            break;
    }
    
    return @"";
    
}


#pragma mark - UITableViewDataSouce

- (id<STStamp>)stampForTableView:(UITableView*)tableView atIndexPath:(NSIndexPath*)indexPath {
    id<STStamp> stamp = nil;
    if (tableView == _searchResultsTableView) {
        stamp = [self.searchResults objectAtIndex:indexPath.row];
    }
    else {
        stamp = [self.snapshot objectAtIndex:indexPath.row];
    }
    return stamp;
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    id<STStamp> stamp = [self stampForTableView:tableView atIndexPath:indexPath];
    if (stamp) {
        return [STStampCell heightForStamp:stamp];
    }
    else {
        //TODO get number
        return 44;
    }
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    if (tableView == _searchResultsTableView) {
        return self.searchResults.count == 0 ? 0 : 1;
    }
    else {
        return self.snapshot.count == 0 ? 0 : 1;
    }
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    if (tableView == _searchResultsTableView) {
        return self.searchResults.count;
    }
    else {
        return self.snapshot.count;
    }
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  
    static NSString *CellIdentifier = @"CellIdentifier";
    [self.cache refreshAtIndex:indexPath.row+1 force:NO];
    STStampCell *cell = (STStampCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.delegate = (id<STStampCellDelegate>)self;
    }
    
    id<STStamp> stamp = [self stampForTableView:tableView atIndexPath:indexPath];
    [cell setupWithStamp:stamp];
    
    return cell;
  
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    id<STStamp> stamp = [self stampForTableView:tableView atIndexPath:indexPath];
    STActionContext* context = [STActionContext context];
    context.stamp = stamp;
    id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}


#pragma mark - STStampCellDelegate

- (void)stStampCellAvatarTapped:(STStampCell*)cell {
    
    UITableView *tableview = [self isSearching] ? _searchResultsTableView : self.tableView;
    NSIndexPath *indexPath = [tableview indexPathForCell:cell];
    id<STStamp> stamp = [self stampForTableView:tableview atIndexPath:indexPath];
    STUserViewController *controller = [[STUserViewController alloc] initWithUser:stamp.user];
    [self.navigationController pushViewController:controller animated:YES];

    
    //[[STStampedActions sharedInstance] viewUserWithUserID:stamp.user.userID];
    
}


#pragma mark STSearchViewDelegate

- (void)stSearchViewDidCancel:(STSearchView*)view {
    [super stSearchViewDidCancel:view];
    
    // cancel model query
    
}

- (void)stSearchViewDidEndSearching:(STSearchView*)view {
    [super stSearchViewDidEndSearching:view];
    
    self.searchResults = nil;
    self.searchQuery = nil;
}

- (void)stSearchViewDidBeginSearching:(STSearchView *)view {
    [super stSearchViewDidBeginSearching:view];
    
    self.searchQuery = nil;
}

- (void)stSearchView:(STSearchView*)view textDidChange:(NSString*)text {
    [super stSearchView:view textDidChange:text];
    self.searchQuery = text;
}

- (void)stSearchViewHitSearch:(STSearchView *)view withText:(NSString*)text {
    
    //TODO
    //[_searchStamps searchWithQuery:text];
    
}


#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return self.reloading;
}

- (void)loadNextPage {
    [self.cache refreshAtIndex:self.snapshot.count force:NO];
}

- (BOOL)dataSourceHasMoreData {
    return self.cache.hasMore;
}

- (void)reloadDataSource {
    [self.cache refreshAtIndex:-1 force:YES];
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return self.snapshot.count == 0;
}

- (void)setupNoDataView:(NoDataView*)view {

    view.imageView.userInteractionEnabled = YES;
    [[view.imageView subviews] makeObjectsPerformSelector:@selector(removeFromSuperview)];
    
    if (!LOGGED_IN || (LOGGED_IN && self.scope != STStampedAPIScopeYou)) {
        
        UIImage *image = [UIImage imageNamed:@"no_data_find_friends_btn.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button setTitle:LOGGED_IN ? @"Find friends to follow" : @"Sign in / Create account" forState:UIControlStateNormal];
        [button addTarget:self action:@selector(noDataAction:) forControlEvents:UIControlEventTouchUpInside];
        [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
        [button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.9f] forState:UIControlStateNormal];
        button.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button sizeToFit];
        [view.imageView addSubview:button];
        CGRect frame = button.frame;
        frame.origin.y = 34.0f;
        frame.size.width += 48.0f;
        frame.size.height = image.size.height;
        frame.origin.x = (view.imageView.bounds.size.width - frame.size.width)/2;
        button.frame = frame;
        CGFloat maxY = CGRectGetMaxY(button.frame);
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.font = [UIFont systemFontOfSize:12];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.5f];
        [view.imageView addSubview:label];
        [label release];
        
        switch (self.scope) {
            case STStampedAPIScopeYou:
                label.text = @"to create stamps.";
                break;
            case STStampedAPIScopeFriends:
                label.text = LOGGED_IN ? @"to view their stamps" : @"to view stamps from friends.";
                break;
            case STStampedAPIScopeFriendsOfFriends:
                label.text = LOGGED_IN ? @"to view their stamps" : @"to view stamps from friends.";
                break;
            case STStampedAPIScopeEveryone:
                label.text = @"to view popular stamps.";
                break;
                
            default:
                break;
        }
        
        [label sizeToFit];
        
        frame = label.frame;
        frame.origin.x = floorf((view.imageView.bounds.size.width-frame.size.width)/2);
        frame.origin.y = floorf(maxY + 8.0f);
        label.frame = frame;
        
        
        
    }
    
    if (LOGGED_IN && self.scope == STStampedAPIScopeYou) {
        
        view.backgroundColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
        view.imageView.backgroundColor = view.backgroundColor;
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.lineBreakMode = UILineBreakModeWordWrap;
        label.numberOfLines = 3;
        label.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
        label.font = [UIFont boldSystemFontOfSize:13];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.textAlignment = UITextAlignmentCenter;
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.5f];
        [view.imageView addSubview:label];
        [label release];
        
        label.text = @"That amazing burrito place.\nThe last great book you read.\nA movie your friends have to see.";
        
        CGSize size = [label.text sizeWithFont:label.font constrainedToSize:CGSizeMake(240.0f, CGFLOAT_MAX) lineBreakMode:UILineBreakModeWordWrap];
        CGRect frame = label.frame;
        frame.size = size;
        frame.origin.x = floorf((view.imageView.bounds.size.width-size.width)/2);
        frame.origin.y = 24.0f;
        label.frame = frame;
        
        CGFloat maxY = CGRectGetMaxY(label.frame);
        
        label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.lineBreakMode	= UILineBreakModeTailTruncation;
        label.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
        label.font = [UIFont boldSystemFontOfSize:17];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.5f];
        [view.imageView addSubview:label];
        [label release];
        
        label.text = @"Stamp it.";
        [label sizeToFit];
        
        frame = label.frame;
        frame.origin.x = floorf((view.imageView.bounds.size.width-frame.size.width)/2);
        frame.origin.y = floorf(maxY + 4.0f);
        label.frame = frame;
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(noDataTapped:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        [view addGestureRecognizer:gesture];
        [gesture release];
        
    } 

}


#pragma mark - No Data Actions

- (void)noDataAction:(id)sender {
    
    if (!LOGGED_IN) {
        
        STMenuController *controller = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
        [controller showWelcome:NO];
        
    } else {
        
        FindFriendsViewController *controller = [[FindFriendsViewController alloc] init];
        STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
        [self presentModalViewController:navController animated:YES];
        [controller release];
        [navController release];
        
    }
    
}

- (void)noDataTapped:(UITapGestureRecognizer*)gesture {
    
    UIImageView *magnifyView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"no_data_magnify.png"]];
    
    UIGraphicsBeginImageContextWithOptions(magnifyView.bounds.size, YES, 0);
    CGContextRef ctx = UIGraphicsGetCurrentContext();
    CGContextScaleCTM(ctx, 1.2, 1.2);
    CGContextTranslateCTM(ctx, -((self.view.bounds.size.width-magnifyView.bounds.size.width)+20.0f), 0.0f);
    [self.navigationController.view.layer renderInContext:ctx];
    UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    
    UIView *view = [[UIView alloc] initWithFrame:self.navigationController.view.bounds];
    view.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.3f];
    [self.navigationController.view addSubview:view];
    [view release];
    
    CGRect frame = magnifyView.frame;
    frame.origin.x = (view.bounds.size.width - (frame.size.width-24.0f));
    frame.origin.y = -30.0f;
    magnifyView.frame = frame;
    [view addSubview:magnifyView];
    [magnifyView release];

    UIImageView *imageView = [[UIImageView alloc] initWithImage:image];
    [view insertSubview:imageView atIndex:0];
    [imageView release];
    
    frame = imageView.frame;
    frame.origin.x = (view.bounds.size.width - imageView.frame.size.width);
    imageView.frame = frame;
    
    CALayer *layer = [CALayer layer];
    layer.frame = CGRectMake(32, -26.0f, imageView.bounds.size.width-18, imageView.bounds.size.height-18);
    layer.cornerRadius = ((imageView.bounds.size.width-18)/2);
    layer.backgroundColor = [UIColor blackColor].CGColor;
    imageView.layer.mask = layer;
    
    CABasicAnimation *animation = [CABasicAnimation animationWithKeyPath:@"backgroundColor"];
    animation.fromValue = (id)[UIColor clearColor].CGColor;
    animation.duration = 0.3f;
    [view.layer addAnimation:animation forKey:nil];
    
    double delayInSeconds = 4.0;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
        [view removeFromSuperview];
    });
    
}


#pragma mark - UIGestureRecognizerDelegate

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    
    DDMenuController *menuController = (id)((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    return ![[menuController tap] isEnabled];
    
}


#pragma mark - Login Notifications 

- (void)logginStatusChanged:(NSNotification*)notification {
    
    if (!LOGGED_IN) {
        
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Sign in" style:UIBarButtonItemStyleBordered target:self action:@selector(login:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
        
    } else {
        
        [Util addCreateStampButtonToController:self];
        
    }
    
}


@end
