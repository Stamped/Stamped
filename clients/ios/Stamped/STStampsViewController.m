//
//  STStampsViewController.m
//  Stamped
//
//  Created by Landon Judkins on 7/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampsViewController.h"
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
#import "STCache.h"
#import "STGenericCacheConfiguration.h"
#import "STCreditPageSource.h"
#import "STAppDelegate.h"

@interface STStampsViewController ()

@property (nonatomic, readwrite, retain) STCache* cache;
@property (nonatomic, readwrite, retain) STCacheSnapshot* snapshot;
@property (nonatomic, readwrite, assign) BOOL reloading;
@property (nonatomic, readwrite, assign) BOOL dirty;

@end

@implementation STStampsViewController

@synthesize cache = _cache;
@synthesize snapshot = _snapshot;
@synthesize reloading = _reloading;
@synthesize dirty = _dirty;

+ (STCancellation*)creditsViewWithUserID:(NSString*)userID
                             andCallback:(void (^)(UIViewController* controller, NSError* error, STCancellation* cancellation))block {
    STGenericCacheConfiguration* config = [[[STGenericCacheConfiguration alloc] init] autorelease];
    config.pageSource = [[[STCreditPageSource alloc] initWithUserID:userID] autorelease];
    NSString* name = [NSString stringWithFormat:@"ProfileCredits_%@", userID];
    return [STCache cacheForName:name 
                     accelerator:nil
                   configuration:config
                     andCallback:^(STCache *cache, NSError *error, STCancellation *cancellation) {
                         if (cache) {
                             STStampsViewController* controller = [[[STStampsViewController alloc] initWithCache:cache] autorelease];
                             controller.dirty = YES;
                             block(controller, nil, cancellation);
                         }
                         else {
                             block(nil, error, cancellation);
                         }
                     }];
}

- (id)initWithCache:(STCache*)cache {
    if (self = [super init]) {
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheUpdate:) name:STCacheDidChangeNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheWillLoadPage:) name:STCacheWillLoadPageNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(cacheDidLoadPage:) name:STCacheDidLoadPageNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(localStampModification:) name:STStampedAPILocalStampModificationNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(applicationDidBecomeActive:) name:UIApplicationDidBecomeActiveNotification object:nil];
        
        _reloading = YES;
        self.showsSearchBar = NO;
        _cache = [cache retain];
        _snapshot = [[cache snapshot] retain];
    }
    return self;
}

- (void)dealloc {
    [_cache release];
    [_snapshot release];
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
    
    [self.tableView reloadData];
}

- (void)viewDidAppear:(BOOL)animated {
    if (self.dirty) {
        [self reloadDataSource];
    }
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

- (void)cacheWillLoadPage:(NSNotification *)notification {
    self.reloading = YES;
    //[self.tableView reloadData];
}

- (void)cacheDidLoadPage:(NSNotification *)notification {
    self.reloading = NO;
    [self dataSourceDidFinishLoading];
    //[self.tableView reloadData];
}

- (void)cacheUpdate:(NSNotification *)notification {
    if (self.cache) {
        self.snapshot = self.cache.snapshot;
        [self reloadTableView:YES];
    }
}

#pragma mark - UITableViewDataSouce

- (id<STStamp>)stampForTableView:(UITableView*)tableView atIndexPath:(NSIndexPath*)indexPath {
    return [self.snapshot objectAtIndex:indexPath.row];
}

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    id<STStamp> stamp = [self stampForTableView:tableView atIndexPath:indexPath];
    return [STStampCell heightForStamp:stamp];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return self.snapshot.count == 0 ? 0 : 1;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return self.snapshot.count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    static NSString *CellIdentifier = @"CellIdentifier";
    NSLog(@"tableCell");
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

#pragma mark - STRestController 

- (BOOL)dataSourceReloading {
    return self.reloading;
}

- (void)loadNextPage {
    NSLog(@"loadNextPage");
    [self.cache refreshAtIndex:self.snapshot.count force:NO];
}

- (BOOL)dataSourceHasMoreData {
    return self.cache.hasMore;
}

- (void)reloadDataSource {
    NSLog(@"reloading");
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

- (void)setupNoDataView:(NoDataView*)view {
    CGRect frame = view.frame;
    CGFloat height = self.tableView.tableHeaderView.bounds.size.height;
    frame.origin.y = height;
    frame.size.height -= height;
    view.frame = frame;
    [view setupWithTitle:@"No stamps" detailTitle:@"Tap to go back"];
}


#pragma mark - No Data Actions

- (void)noDataAction:(id)sender {
    [Util compareAndPopController:self animated:YES];
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

- (void)localStampModification:(id)notImportant {
    self.dirty = YES;
}

- (void)applicationDidBecomeActive:(id)notImportant {
    [self reloadDataSource];
}

@end