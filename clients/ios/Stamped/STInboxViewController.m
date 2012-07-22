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
#import "STUnreadActivity.h"
#import "STNavigationItem.h"
#import "STAppDelegate.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "NoDataView.h"
#import "NoDataUtil.h"

NSString* STInboxViewControllerPrepareForAnimationNotification = @"STInboxViewControllerPrepareForAnimationNotification";

static STStampedAPIScope _lastScope = STStampedAPIScopeFriends;

@interface STInboxViewController ()

@property (nonatomic, readonly, retain) STSliderScopeView *slider;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readwrite, copy) NSString* searchQuery;
@property (nonatomic, readwrite, retain) STCache* cache;
@property (nonatomic, readwrite, retain) STCacheSnapshot* snapshot;
@property (nonatomic, readwrite, retain) NSArray<STStamp>* searchResults;
@property (nonatomic, readwrite, assign) BOOL reloading;
@property (nonatomic, readwrite, assign) BOOL dirty;
@property (nonatomic, readwrite, assign) BOOL showIntro;
@property (nonatomic, readwrite, assign) BOOL goingToShowIntro;
@property (nonatomic, readwrite, retain) UIView* emptyPopupView;
@property (nonatomic, readwrite, retain) UIView* tooltip;
@property (nonatomic, readwrite, retain) UIView* createStampOverlay;

@end

@implementation STInboxViewController

@synthesize slider = _slider;
@synthesize scope = _scope;
@synthesize searchQuery = _searchQuery;
@synthesize cache = _cache;
@synthesize snapshot = _snapshot;
@synthesize searchResults = _searchResults;
@synthesize reloading = _reloading;
@synthesize dirty = _dirty;
@synthesize showIntro = _showIntro;
@synthesize goingToShowIntro = _goingToShowIntro;
@synthesize emptyPopupView = _emptyPopupView;
@synthesize tooltip = _tooltip;
@synthesize createStampOverlay = _createStampOverlay;

- (id)init {
    if (self = [super init]) {
        
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(logginStatusChanged:) name:STStampedAPILoginNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(logginStatusChanged:) name:STStampedAPILogoutNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(logginStatusChanged:) name:STStampedAPIRefreshedTokenNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(logginStatusChanged:) name:STStampedAPIUserUpdatedNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheUpdate:) name:STCacheDidChangeNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheWillLoadPage:) name:STCacheWillLoadPageNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheDidLoadPage:) name:STCacheDidLoadPageNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(localStampModification:) name:STStampedAPILocalStampModificationNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(applicationDidBecomeActive:) name:UIApplicationDidBecomeActiveNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(friendsChanged:) name:STStampedAPIUnfollowNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(friendsChanged:) name:STStampedAPIFollowNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(willShowLeftMenu:) name:DDMenuControllerWillShowLeftMenuNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(prepareForAnimationRequest:) name:STInboxViewControllerPrepareForAnimationNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(popupDismissed:) name:STUtilPopupDismissedNotification object:nil];
        
        NSString* userDefaultsKey = @"otenupvpinouuipovfsdfpdfaipofdais"; //psuedo-random
        NSString* lastUserID = [[NSUserDefaults standardUserDefaults] objectForKey:userDefaultsKey];
        NSString* currentUserID = [STStampedAPI sharedInstance].currentUser.userID;
        _showIntro = currentUserID != nil && ![currentUserID isEqualToString:lastUserID];
        [[NSUserDefaults standardUserDefaults] setObject:currentUserID ? currentUserID : @" invalid userID " forKey:userDefaultsKey];
        if (currentUserID == nil) {
            _scope = STStampedAPIScopeEveryone;
            _lastScope = STStampedAPIScopeEveryone;
        } else {
            _scope = _lastScope;
        }
        _searchQuery = nil;
        _reloading = YES;
        self.showsSearchBar = NO;
    }
    return self;
}

- (void)dealloc {
    [_emptyPopupView release];
    _slider.delegate = nil;
    [_slider release], _slider=nil;
    [_tooltip release];
    self.createStampOverlay = nil;
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
    
    if (!LOGGED_IN) {
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Sign in" style:UIBarButtonItemStyleDone  target:self action:@selector(login:)];
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
    STMenuController *controller = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    controller.pan.enabled = NO;
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
    _slider.delegate = nil;
    [_slider release];
    self.createStampOverlay = nil;
}

- (void)viewDidAppear:(BOOL)animated {
    //Resume cache ops
    if (self.dirty) {
        [self reloadDataSource];
    }
}

- (void)abortIntro {
    [self.emptyPopupView removeFromSuperview];
    self.emptyPopupView = nil;
    [self.tooltip removeFromSuperview];
    self.tooltip = nil;
    self.goingToShowIntro = NO;
    [Util setFullScreenPopUp:nil dismissible:NO withBackground:[UIColor clearColor]];
}

- (void)viewDidDisappear:(BOOL)animated {
    [self abortIntro];
    //Todo cancel pending cache ops
    [super viewDidDisappear:animated];
}


- (void)willShowLeftMenu:(id)notImportant {
    [self abortIntro];
}

#pragma mark - Actions

- (void)login:(id)sender {
    
    STMenuController *controller = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [controller showSignIn];
    
}


#pragma mark - Cache Methods

- (void)reloadTableView:(BOOL)preserveOffset {
    
    if (preserveOffset) {
        
        CGPoint offset = self.tableView.contentOffset;
        [self.tableView reloadData];
        self.tableView.contentOffset = offset;
        
    } else {
        [self.tableView reloadData];
    }
    
}

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
    
    [self reloadTableView:NO];
    
}

- (void)cacheWillLoadPage:(NSNotification *)notification {
    self.reloading = YES;
    // [self.tableView reloadData];
}

- (void)cacheDidLoadPage:(NSNotification *)notification {
    self.reloading = NO;
    [self dataSourceDidFinishLoading];
    // [self.tableView reloadData];
}

- (void)cacheUpdate:(NSNotification *)notification {
    if (self.cache) {
        self.snapshot = self.cache.snapshot;
        [self reloadTableView:YES];
    }
}


#pragma mark - STSliderScopeViewDelegate

- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope {
    if (scope != STStampedAPIScopeEveryone) {
        [self.emptyPopupView removeFromSuperview];
        self.emptyPopupView = nil;
    }
    self.scope = scope;
}

- (void)setScope:(STStampedAPIScope)scope {
    if (_scope != scope) {
        _scope = scope;
        _lastScope = _scope;
        [self updateCache];
        if (self.showsSearchBar) {
            [self.tableView setContentOffset:CGPointMake(0.0f, self.searchView.bounds.size.height-2.0f)];
        }
    }
}


#pragma mark - STSliderScopeViewDataSource

- (NSString*)sliderScopeView:(STSliderScopeView*)slider titleForScope:(STStampedAPIScope)scope {
    
    switch (scope) {
        case STStampedAPIScopeYou:
            return @"you";
            break;
        case STStampedAPIScopeFriends:
            return @"you + friends";
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
    [controller release];
    
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
    if (self.dirty) {
        [self.cache updateAllWithAccellerator:[STStampedAPI sharedInstance]];
    }
    self.dirty = NO;
    [self.cache refreshAtIndex:-1 force:YES];
    [[STUnreadActivity sharedInstance] update];
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return self.snapshot.count == 0;
}

- (void)exitNoDataView:(id)notImportant {
    [self showTooltip];
    [Util setFullScreenPopUp:nil dismissible:NO withBackground:[UIColor clearColor]];
}

- (void)showScopeShiftPopup {
    if ([Util topController] == self) {
        NoDataView* noDataView = [[[NoDataView alloc] initWithFrame:[Util fullscreenFrame]] autorelease];
        //        [Util reframeView:noDataView withDeltas:CGRectMake(0, -50, 0, 0)];
        noDataView.userInteractionEnabled = YES;
        NSString* topString = @"Since you're not yet following anyone, we're showing you stamps from Tastemakers.";
        //        NSString* bottomString = @"Got it.";
        UILabel* top = [Util viewWithText:topString
                                     font:[UIFont stampedBoldFontWithSize:14]
                                    color:[UIColor whiteColor]
                                     mode:UILineBreakModeWordWrap
                               andMaxSize:CGSizeMake(200, CGFLOAT_MAX)];
        top.textAlignment = UITextAlignmentCenter;
        CGRect bounds = CGRectMake(0, 0, noDataView.imageView.frame.size.width, noDataView.imageView.frame.size.height);
        top.frame = [Util centeredAndBounded:top.frame.size inFrame:bounds];
        [noDataView.imageView addSubview:top];
        [Util reframeView:top withDeltas:CGRectMake(0, - 8 , 0, 0)];
        noDataView.imageView.userInteractionEnabled = YES;
        UIButton* exitButton = [UIButton buttonWithType:UIButtonTypeCustom];
        [exitButton addTarget:self action:@selector(exitNoDataView:) forControlEvents:UIControlEventTouchUpInside];
        [exitButton setImage:[UIImage imageNamed:@"closebutton_black"] forState:UIControlStateNormal];
        exitButton.frame = CGRectMake(-6.5, - 11, 48, 48);
        [noDataView.imageView addSubview:exitButton];
        
        //noDataView.frame = [Util centeredAndBounded:noDataView.frame.size inFrame:CGRectMake(0, 0, self.view.frame.size.width, self.view.frame.size.height)];
        noDataView.backgroundColor = [UIColor clearColor];
        //        [self.view addSubview:noDataView];
        //        self.emptyPopupView = noDataView;
        top.hidden = YES;
        //        bottom.hidden = YES;
        CGRect rectAfter = noDataView.imageView.frame;
        [Util setFullScreenPopUp:noDataView dismissible:YES withBackground:[UIColor clearColor]];
        noDataView.imageView.frame = [Util centeredAndBounded:CGSizeMake(20, 14) inFrame:rectAfter];
        [noDataView addGestureRecognizer:[[[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(exitNoDataView:)] autorelease]];
        [UIView animateWithDuration:.2 delay:0 options:UIViewAnimationCurveEaseInOut animations:^{
            noDataView.backgroundColor = [UIColor colorWithWhite:0 alpha:.3];
            noDataView.imageView.frame = rectAfter;
        } completion:^(BOOL finished) {
            top.hidden = NO;
            
        }];
        noDataView.userInteractionEnabled = YES;
    }
}

- (void)dataSourceDidFinishLoading {
    BOOL showIntro = self.showIntro && !self.cache.hasMore && self.snapshot.count == 0 && self.scope == STStampedAPIScopeFriends;
    self.showIntro = NO;
    if (showIntro) {
        self.goingToShowIntro = YES;
        [Util executeWithDelay:.8 onMainThread:^{
            if ([Util topController] == self && self.goingToShowIntro) {
                [self.slider setScope:STStampedAPIScopeEveryone animated:YES];
                [Util executeWithDelay:1.0 onMainThread:^{
                    if (self.goingToShowIntro) {
                        [self showScopeShiftPopup]; 
                    }
                    self.goingToShowIntro = NO;
                }];
            }
        }];
        //        [self.slider moveToScope:STStampedAPIScopeEveryone animated:YES duration:.4 completion:^{
        //            NSLog(@"yayayayay"); 
        //        }];
        //        [self.slider setScope:STStampedAPIScopeEveryone animated:YES];
    }
    [super dataSourceDidFinishLoading];
}

- (void)setupNoDataView:(NoDataView*)view {
    
    view.imageView.userInteractionEnabled = YES;
    [[view.imageView subviews] makeObjectsPerformSelector:@selector(removeFromSuperview)];
    
    if (!LOGGED_IN || (LOGGED_IN && self.scope != STStampedAPIScopeYou)) {
        if (self.goingToShowIntro) {
            view.custom = YES;
            
            UIView* waterMark = [NoDataUtil stampWatermarkWithTitle:@"No stamps" andSubtitle:@"from friends"];
            waterMark.frame = [Util centeredAndBounded:waterMark.frame.size inFrame:CGRectMake(0, 0, view.frame.size.width, view.frame.size.height)];
            [view addSubview:waterMark];
        }
        else {
            UIImage *image = [UIImage imageNamed:@"pop-up_findfriendstofollow_btn"];
            UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
            [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
            [button setTitle:LOGGED_IN ? @"Find friends to follow" : @"Sign in / Create account" forState:UIControlStateNormal];
            [button addTarget:self action:@selector(noDataAction:) forControlEvents:UIControlEventTouchUpInside];
            [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
            //[button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.9f] forState:UIControlStateNormal];
            //button.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
            button.titleLabel.font = [UIFont stampedBoldFontWithSize:12];
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
    }
    else if (LOGGED_IN && self.scope == STStampedAPIScopeYou) {
        //DUCKTAPE
        view.backgroundColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
        view.imageView.backgroundColor = view.backgroundColor;
        
        UILabel* label = [[UILabel alloc] initWithFrame:CGRectMake(0, 0, 240, 90)];
        label.frame = [Util centeredAndBounded:label.frame.size inFrame:CGRectMake(-10, 16, 320, label.frame.size.height)];
        label.lineBreakMode	= UILineBreakModeWordWrap;
        label.font = [UIFont stampedBoldFontWithSize:13];
        label.textAlignment = UITextAlignmentCenter;
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.5f];
        [view.imageView addSubview:label];
        [label release];
        label.numberOfLines = 3;
        label.text = @"Tap the \"+\" button to create\nyour first stamp. It's easy, just\nthink of something you love!";
        
        [Util executeOnMainThread:^{
            if ([Util topController] == self && self.scope == STStampedAPIScopeYou) {
                [self noDataTapped:nil];
            }
        }];
        
    } 
    
}


#pragma mark - No Data Actions

- (void)noDataAction:(id)sender {
    
    if (!LOGGED_IN) {
        
        STMenuController *controller = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
        [controller showSignIn];
        
    } else {
        
        FindFriendsViewController *controller = [[[FindFriendsViewController alloc] init] autorelease];
        [[Util sharedNavigationController] pushViewController:controller animated:YES];
    }
    
}

- (void)noDataTapped:(id)notImportant {
    if (!self.createStampOverlay) {
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
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(createStampHelper:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        [view addGestureRecognizer:gesture];
        [gesture release];
        self.createStampOverlay = view;
        double delayInSeconds = 2.5;
        dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
        dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
            [view removeFromSuperview];
            self.createStampOverlay = nil;
        });
    }
}

- (void)createStampHelper:(id)notImportant {
    [self.createStampOverlay removeFromSuperview];
    self.createStampOverlay = nil;
    //    id customView = self.navigationItem.rightBarButtonItem.customView;
    //    if ([customView respondsToSelector:@selector(sendActionsForControlEvents:)]) {
    //        [customView sendActionsForControlEvents:UIControlEventTouchUpInside];
    //    }
}


#pragma mark - UIGestureRecognizerDelegate

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    
    DDMenuController *menuController = (id)((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    return ![[menuController tap] isEnabled];
    
}

- (void)localStampModification:(id)notImportant {
    self.dirty = YES;
}

- (void)showTooltip {
    [Util executeWithDelay:5 onMainThread:^{
        if ([Util topController] == self) {
            self.tooltip = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"bubble_addfriends"]] autorelease];
            self.tooltip.frame = [Util centeredAndBounded:self.tooltip.frame.size inFrame:CGRectMake(0, 320, 320, self.tooltip.frame.size.height)];
            [self.view addSubview:self.tooltip];
            self.tooltip.alpha = 0;
            [UIView animateWithDuration:.3 animations:^{
                self.tooltip.alpha = 1;
            } completion:^(BOOL finished) {
                if (finished) {
                    [Util executeWithDelay:2 onMainThread:^{ 
                        [UIView animateWithDuration:.4 animations:^{
                            self.tooltip.alpha = 0;
                        } completion:^(BOOL finished) {
                            [self.tooltip removeFromSuperview];
                            self.tooltip = nil;
                        }];
                    }];
                }
            }];
            
        }
    }];}

#pragma mark - Login Notifications 

- (void)logginStatusChanged:(NSNotification*)notification {
    
    _showIntro = YES;
    if (!LOGGED_IN) {
        
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Sign in" style:UIBarButtonItemStyleBordered target:self action:@selector(login:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
    } 
    else {
        [Util addCreateStampButtonToController:self];
        self.slider.scope = STStampedAPIScopeFriends;
        self.scope = STStampedAPIScopeFriends;
    }
    
    [self reloadDataSource];
}

- (void)applicationDidBecomeActive:(id)notImportant {
    [self reloadDataSource];
}

- (void)friendsChanged:(id)notImportant {
    //    _showIntro = YES;
    self.dirty = YES;
}

- (void)prepareForAnimationRequest:(id)notImportant {
    self.dirty = YES;
    _showIntro = YES;
}

- (void)popupDismissed:(id)notImportant {
    if ([Util topController] == self) {
        [self showTooltip];
    }
}









@end
