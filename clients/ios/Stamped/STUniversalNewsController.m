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

@interface STUniversalNewsController ()
@property (nonatomic, readonly, retain) NSMutableArray* newsItems;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@end

@implementation STUniversalNewsController

@synthesize newsItems = newsItems_;
@synthesize scope = scope_;

- (id)init {
    if ((self = [super init])) {
        scope_ = STStampedAPIScopeYou;
    }
    return self;    
}

- (void)viewDidLoad {
    [super viewDidLoad];
    [Util addHomeButtonToController:self withBadge:NO];
    [self reloadDataSource];
}

- (void)viewDidUnload {
    [super viewDidUnload];
}


#pragma mark - Setters

- (void)setScope:(STStampedAPIScope)scope {
    scope_ = scope;
    [self reloadStampedData];
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
    }];
  }
}


#pragma mark - STRestViewController Methods

- (BOOL)dataSourceReloading {
    return NO; //self.reloading;
}

- (void)loadNextPage {
    //[self.cache refreshAtIndex:self.snapshot.count force:NO];
}

- (BOOL)dataSourceHasMoreData {
    return NO; //self.cache.hasMore;
}

- (void)reloadDataSource {
    [self reloadStampedData];
    [super reloadDataSource];
}

- (BOOL)dataSourceIsEmpty {
    return self.newsItems.count == 0;
}

- (void)setupNoDataView:(NoDataView*)view {
    
    view.imageView.userInteractionEnabled = YES;
    [[view.imageView subviews] makeObjectsPerformSelector:@selector(removeFromSuperview)];
    
    if (self.scope == STStampedAPIScopeYou) {
        
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


@end
