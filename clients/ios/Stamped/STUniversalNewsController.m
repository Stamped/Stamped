//
//  STUniversalNewsController.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUniversalNewsController.h"
#import "STStampedAPI.h"
#import "STActivity.h"
#import "STActionManager.h"
#import "STActivityCell.h"
#import "Util.h"
#import "STSliderScopeView.h"

@interface STUniversalNewsController ()

@property (nonatomic, retain, readonly) STSliderScopeView *slider;
@property (nonatomic, readonly, retain) NSMutableArray* newsItems;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readwrite, assign) BOOL reloading;

@end

@implementation STUniversalNewsController

@synthesize newsItems = newsItems_;
@synthesize scope = scope_;
@synthesize reloading = _reloading;
@synthesize slider=_slider;

- (id)init {
    if ((self = [super init])) {
        scope_ = STStampedAPIScopeYou;
    }
    return self;    
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!self.tableView.backgroundView) {
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
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
        [view release];
        _slider = [view retain];
    }
    
    [Util addCreateStampButtonToController:self];
    [self reloadDataSource];
    [STEvents postEvent:EventTypeUnreadCountUpdated object:[NSNumber numberWithInt:0]];
    
}

- (void)viewDidUnload {
    [_slider release], _slider=nil;
    [super viewDidUnload];
}

- (void)dealloc {
    [newsItems_ release], newsItems_=nil;
    [_slider release], _slider=nil;
    [super dealloc];
}


#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope {
    if (scope_==scope) return; 
    scope_ = scope;
    [self reloadDataSource];
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
        case STStampedAPIScopeEveryone:
            return @"about your friends";
            break;
        default:
            break;
    }
    
    return nil;
}

- (NSString*)sliderScopeView:(STSliderScopeView*)slider boldTitleForScope:(STStampedAPIScope)scope {
    
    switch (scope) {
        case STStampedAPIScopeYou:
            return @"you";
            break;
        case STStampedAPIScopeEveryone:
            return @"your friends";
            break;
        default:
            break;
    }
    
    return nil;
    
}


#pragma mark - UITableViewDataSource

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    if (self.newsItems) {
        return self.newsItems.count;
    }
    return 0;
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
    return [STActivityCell heightForCellWithActivity:activity andScope:self.scope];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
    return [[[STActivityCell alloc] initWithActivity:activity andScope:self.scope] autorelease];
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    
    id<STActivity> activity = [self.newsItems objectAtIndex:indexPath.row];
    if (activity.action) {
        [[STActionManager sharedActionManager] didChooseAction:activity.action withContext:[STActionContext context]];
    }
}


#pragma mark - DataSource Reloading

- (void)reloadStampedData {
    STGenericSlice* slice = [[[STGenericSlice alloc] init] autorelease];
    slice.limit = [NSNumber numberWithInteger:100];
    if (self.scope == STStampedAPIScopeYou) {
        [[STStampedAPI sharedInstance] activitiesForYouWithGenericSlice:slice andCallback:^(NSArray<STActivity> *activities, NSError *error) {
            if (activities) {
                NSLog(@"activities:%@",activities);
                newsItems_ = [[NSMutableArray arrayWithArray:activities] retain];
                [self.tableView reloadData];
            }
            else {
                NSLog(@"activity error: %@",error);
            }
            [self dataSourceDidFinishLoading];
        }];
    }
    else {
        [[STStampedAPI sharedInstance] activitiesForFriendsWithGenericSlice:slice andCallback:^(NSArray<STActivity> *activities, NSError *error) {
            if (activities) {
                NSLog(@"activities:%@",activities);
                newsItems_ = [[NSMutableArray arrayWithArray:activities] retain];
                [self.tableView reloadData];
            }
            else {
                NSLog(@"activity error: %@",error);
            }
            [self dataSourceDidFinishLoading];
        }];
    }
}


#pragma mark - STRestViewController Methods

- (BOOL)dataSourceReloading {
    return self.reloading;
}

- (void)loadNextPage {
    //[self.cache refreshAtIndex:self.snapshot.count force:NO];
}

- (BOOL)dataSourceHasMoreData {
    return self.reloading;
}

- (void)reloadDataSource {
    self.reloading = YES;
    [self reloadStampedData];
    [super reloadDataSource];
}

- (void)dataSourceDidFinishLoading {
    self.reloading = NO;
    [super dataSourceDidFinishLoading];
}

- (BOOL)dataSourceIsEmpty {
    return self.newsItems.count == 0;
}

- (void)noDataTapped:(id)notImportant {
    [Util warnWithMessage:@"not implemented yet..." andBlock:nil];
}

- (void)setupNoDataView:(NoDataView*)view {
    
    [view setupWithTitle:@"No news" detailTitle:@"No news found."];
    
}


@end
