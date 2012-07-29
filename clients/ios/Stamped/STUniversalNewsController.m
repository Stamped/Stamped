//
//  STUniversalNewsController.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUniversalNewsController.h"
#import <UIKit/UIKit.h>
#import "STStampedAPI.h"
#import "STActivity.h"
#import "STActionManager.h"
#import "STFastActivityCell.h"
#import "Util.h"
#import "STSliderScopeView.h"
#import "STUnreadActivity.h"
#import "STEvents.h"
#import "STBlockUIView.h"
#import <QuartzCore/QuartzCore.h>
#import "QuartzUtils.h"
#import "FindFriendsViewController.h"
#import "STStampedActions.h"
#import "STUsersViewController.h"
#import "EntityDetailViewController.h"

static NSString* const STUniversalNewWasUpdatedNotification = @"STUniversalNewsWasUpdatedNotification";

@interface STUniversalNewsController ()

+ (STCancellation*)cancellationForScope:(STStampedAPIScope)scope;
+ (void)setCancellation:(STCancellation*)cancellation forScope:(STStampedAPIScope)scope;
+ (BOOL)isDirtyForScope:(STStampedAPIScope)scope;
+ (void)setIsDirty:(BOOL)dirty forScope:(STStampedAPIScope)scope;
+ (BOOL)hasMoreForScope:(STStampedAPIScope)scope;
+ (void)setHasMore:(BOOL)dirty forScope:(STStampedAPIScope)scope;
+ (void)cancelAll;
+ (void)dirtyAll;

@property (nonatomic, retain, readonly) STSliderScopeView *slider;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readonly, retain) NSMutableArray* newsItems;

@end

@implementation STUniversalNewsController

@synthesize scope = scope_;
@synthesize slider=_slider;

static NSMutableArray* _youActivity;
static NSMutableArray* _friendsActivity;
static STCancellation* _youCancellation = nil;
static STCancellation* _friendsCancellation = nil;
static BOOL _youDirty = YES;
static BOOL _friendsDirty = YES;
static BOOL _youHasMore = YES;
static BOOL _friendsHasMore = YES;

+ (void)initialize {
    _youActivity = [[NSMutableArray alloc] init];
    _friendsActivity = [[NSMutableArray alloc] init];
}

+ (NSMutableArray*)activityForScope:(STStampedAPIScope)scope {
    if (scope == STStampedAPIScopeYou) {
        return _youActivity;
    }
    else {
        return _friendsActivity;
    }
}

+ (STCancellation *)cancellationForScope:(STStampedAPIScope)scope {
    if (scope == STStampedAPIScopeYou) {
        return _youCancellation;
    }
    else {
        return _friendsCancellation;
    }
}

+ (void)setCancellation:(STCancellation *)cancellation forScope:(STStampedAPIScope)scope {
    if (scope == STStampedAPIScopeYou) {
        [_youCancellation cancel];
        [_youCancellation release];
        _youCancellation = [cancellation retain];
    }
    else {
        [_friendsCancellation cancel];
        [_friendsCancellation release];
        _friendsCancellation = [cancellation retain];
    }
}

+ (BOOL)hasMoreForScope:(STStampedAPIScope)scope {
    if (scope == STStampedAPIScopeYou) {
        return _youHasMore;
    }
    else {
        return _friendsHasMore;
    }
}

+ (void)setHasMore:(BOOL)hasMore forScope:(STStampedAPIScope)scope {
    if (scope == STStampedAPIScopeYou) {
        _youHasMore = hasMore;
    }
    else {
        _friendsHasMore = hasMore;
    }
}

+ (BOOL)isDirtyForScope:(STStampedAPIScope)scope {
    if (scope == STStampedAPIScopeYou) {
        return _youDirty;
    }
    else {
        return _friendsDirty;
    }
}

+ (void)setIsDirty:(BOOL)dirty forScope:(STStampedAPIScope)scope {
    if (scope == STStampedAPIScopeYou) {
        _youDirty = dirty;
    }
    else {
        _friendsDirty = dirty;
    }
}

+ (void)dirtyAll {
    [self setIsDirty:YES forScope:STStampedAPIScopeYou];
    [self setIsDirty:YES forScope:STStampedAPIScopeFriends];
}

+ (void)cancelAll {
    [self setCancellation:nil forScope:STStampedAPIScopeYou];
    [self setCancellation:nil forScope:STStampedAPIScopeFriends];
}

- (id)init {
    if ((self = [super init])) {
        scope_ = STStampedAPIScopeYou;
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(countUpdated:) name:UIApplicationDidBecomeActiveNotification object:nil];
    }
    return self;    
}

- (void)dealloc
{
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [STEvents removeObserver:self];
    [_slider release];
    [super dealloc];
}

- (void)countUpdated:(id)notImportant {
    if (scope_ == STStampedAPIScopeYou) {
        [self clearBadges];
    }
}

- (void)viewDidLoad {
    [super viewDidLoad];
    [STUniversalNewsController dirtyAll];
    [STEvents addObserver:self selector:@selector(countUpdated:) event:EventTypeUnreadCountUpdated];
    if (!self.tableView.backgroundView) {
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            drawGradient([UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor, [UIColor colorWithRed:.85 green:.85 blue:.85 alpha:1.0f].CGColor, ctx);
        }];
        self.tableView.backgroundView = background;
        [background release];
    }
    if (!self.footerView) {
        STSliderScopeView *view = [[STSliderScopeView alloc] initWithStyle:STSliderScopeStyleTwo frame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 54.0f)];
        view.delegate = (id<STSliderScopeViewDelegate>)self;
        view.dataSource = (id<STSliderScopeViewDataSource>)self;
        self.footerView = view;
        view.scope = scope_;
        [view release];
        _slider = [view retain];
    }
    [Util addCreateStampButtonToController:self];
    [self reloadDataSource];
    
}

- (void)clearBadges {
    [STUnreadActivity sharedInstance].count = 0;
    [UIApplication sharedApplication].applicationIconBadgeNumber = 0;
}

- (void)viewDidAppear:(BOOL)animated {
    if (scope_ == STStampedAPIScopeYou) {
        [self clearBadges];
    }
    NSIndexPath* selection = [self.tableView indexPathForSelectedRow];
    if (selection) {
        [self.tableView deselectRowAtIndexPath:selection animated:YES];
    }
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(newsWasUpdated:) name:STUniversalNewWasUpdatedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(willEnterForeground:) name:UIApplicationWillEnterForegroundNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(didEnterBackground:) name:UIApplicationDidEnterBackgroundNotification object:nil];
    [super viewDidAppear:animated];
}

- (void)viewDidDisappear:(BOOL)animated {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [STUniversalNewsController cancelAll];
    [super viewDidDisappear:animated];
}

#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope {
    if (scope_==scope) return; 
    scope_ = scope;
    [self.tableView setContentOffset:CGPointMake(0, 0)];
    if ([STUniversalNewsController isDirtyForScope:scope]) {
        [self reloadDataSource];
    }
    else {
        [super reloadDataSource];
        [super dataSourceDidFinishLoading];
        [self.tableView reloadData];
    }
}


#pragma mark - STSliderScopeViewDelegate

- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope {
    [self setScope:scope];
}


#pragma mark - STSliderScopeViewDataSource

- (NSString*)sliderScopeView:(STSliderScopeView*)slider titleForScope:(STStampedAPIScope)scope {
    
    switch (scope) {
        case STStampedAPIScopeYou:
            return @"about you";
            break;
        case STStampedAPIScopeFriends:
            return @"about your friends";
            break;
        default:
            break;
    }
    
    return @"";
}

- (NSString*)sliderScopeView:(STSliderScopeView*)slider boldTitleForScope:(STStampedAPIScope)scope {
    
    switch (scope) {
        case STStampedAPIScopeYou:
            return @"you";
            break;
        case STStampedAPIScopeFriends:
            return @"your friends";
            break;
        default:
            break;
    }
    
    return @"";
    
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return self.newsItems.count;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
    return [STFastActivityCell heightForCellWithActivity:activity andScope:self.scope];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
    return [[[STFastActivityCell alloc] initWithActivity:activity andScope:self.scope] autorelease];
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    //TODO generic rule for view all subjects as default
    id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
    if (activity.action) {
        [[STActionManager sharedActionManager] didChooseAction:activity.action withContext:[STActionContext context]];
    }
    else if (activity.subjects.count || activity.objects.users.count || activity.objects.stamps.count) {
        NSMutableArray* users = [NSMutableArray array];
        NSMutableDictionary* stamps = [NSMutableDictionary dictionary];
        if (activity.subjects.count) {
            [users addObjectsFromArray:activity.subjects];
        }
        else if (activity.objects.users.count) {
            [users addObjectsFromArray:activity.objects.users];
        }
        else if (activity.objects.stamps.count) {
            for (id<STStampPreview> preview in activity.objects.stamps) {
                if (preview.user && preview.stampID && preview.user.userID) {
                    [users addObject:preview.user];
                    [stamps setObject:preview.stampID forKey:preview.user.userID];
                }
            }
        }
        NSMutableArray* userIDs = [NSMutableArray array];
        for (id<STUser> user in users) {
            if (user.userID) {
                [userIDs addObject:user.userID];
            }
        }
        STUsersViewController* controller = [[[STUsersViewController alloc] initWithUserIDs:userIDs] autorelease];
        [controller setUserIDToStampID:stamps];
        [Util compareAndPushOnto:self withController:controller modal:NO animated:YES];
    }
    else if (activity.objects.entities.count) {
        id<STEntity> entity = [activity.objects.entities objectAtIndex:0];
        if (entity.entityID) {
            EntityDetailViewController* controller = [[[EntityDetailViewController alloc] initWithEntityID:entity.entityID] autorelease];
            [Util compareAndPushOnto:self withController:controller modal:NO animated:YES];
        }
    }
}


#pragma mark - DataSource Reloading

+ (void)loadWithScope:(STStampedAPIScope)scope {
    BOOL dirty = [self isDirtyForScope:scope];
    NSMutableArray* array = [self activityForScope:scope];
    NSInteger offset;
    if (dirty) {
        [[self cancellationForScope:scope] cancel];
        [self setCancellation:nil forScope:scope];
        [self setHasMore:YES forScope:scope];
        offset = 0;
    }
    else {
        offset = array.count;
    }
    [self setIsDirty:NO forScope:scope];
    STCancellation* cancellation = [self cancellationForScope:scope];
    NSInteger limit = 20;
    if (!cancellation) {
        cancellation = [[STStampedAPI sharedInstance] activitiesForScope:scope
                                                                  offset:offset
                                                                   limit:limit
                                                             andCallback:^(NSArray<STActivity> *activities, NSError *error, STCancellation *cancellation) {
                                                                 [self setCancellation:nil forScope:scope];
                                                                 if (activities) {
                                                                     if (offset < array.count) {
                                                                         [array removeObjectsInRange:NSMakeRange(offset, array.count - offset)];
                                                                     }
                                                                     [array addObjectsFromArray:activities];
                                                                     if (activities.count < limit) {
                                                                         [self setHasMore:NO forScope:scope];
                                                                     }
                                                                 }
                                                                 else {
                                                                     [self setHasMore:NO forScope:scope];
                                                                     [Util warnWithAPIError:error andBlock:nil];
                                                                 }
                                                                 [[NSNotificationCenter defaultCenter] postNotificationName:STUniversalNewWasUpdatedNotification object:nil];
                                                             }];
        [self setCancellation:cancellation forScope:scope];
    }
}


#pragma mark - STRestViewController Methods

- (BOOL)dataSourceReloading {
    return [STUniversalNewsController cancellationForScope:self.scope] != nil;
}

- (void)loadNextPage {
    if ([STUniversalNewsController hasMoreForScope:self.scope]) {
        [STUniversalNewsController loadWithScope:self.scope];
    }
}


- (BOOL)dataSourceHasMoreData {
    return [STUniversalNewsController hasMoreForScope:self.scope];
}

- (void)reloadDataSource {
    [STUniversalNewsController setIsDirty:YES forScope:self.scope];
    [STUniversalNewsController loadWithScope:self.scope];
    [self.tableView reloadData];
    [super reloadDataSource];
}

- (void)dataSourceDidFinishLoading {
    [super dataSourceDidFinishLoading];
}

- (BOOL)dataSourceIsEmpty {
    return self.newsItems.count == 0;
}

- (void)noDataAction:(id)sender {
    
    FindFriendsViewController *controller = [[[FindFriendsViewController alloc] init] autorelease];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
    
}

- (void)setupNoDataView:(NoDataView*)view {
    
    [view setupWithButtonTitle:LOGGED_IN ? @"Find friends to follow" : @"Sign in / Create account"
                   detailTitle:self.scope == STStampedAPIScopeYou ? @"To get more activity on your stamps" : @"To see activity for friends."
                        target:self
                     andAction:@selector(noDataAction:)];
}


#pragma mark - Notifications 

- (void)didEnterBackground:(NSNotification*)notification {    
}

- (void)willEnterForeground:(NSNotification*)notification {
    [self reloadDataSource];
}

- (void)newsWasUpdated:(NSNotification*)notification {
    [self dataSourceDidFinishLoading];
    [self.tableView reloadData];
}

#pragma mark - Getters

- (NSMutableArray *)newsItems {
    return [STUniversalNewsController activityForScope:self.scope];
}

@end
