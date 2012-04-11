//
//  EntityDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/9/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EntityDetailViewController.h"

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "CreateStampViewController.h"
#import "DetailedEntity.h"
#import "Entity.h"
#import "Stamp.h"
#import "SearchResult.h"
#import "UIColor+Stamped.h"
#import "StampDetailViewController.h"
#import "Notifications.h"
#import "Favorite.h"
#import "User.h"
#import "StampedAppDelegate.h"
#import "Alerts.h"
#import "STToolbar.h"
#import "STSimpleEntityDetail.h"
#import "STStampedAPI.h"
#import "STHeaderViewFactory.h"
#import "STMetadataViewFactory.h"
#import "STGalleryViewFactory.h"
#import "STActionsViewFactory.h"
#import "STActionMenuFactory.h"
#import "STEntityDetailViewFactory.h"
#import "STSynchronousWrapper.h"
#import "STRdio.h"
#import "STScrollViewContainer.h"
#import "STToolbarView.h"
#import "STLikeButton.h"
#import "STTodoButton.h"
#import "STStampButton.h"

static NSString* const kEntityLookupPath = @"/entities/show.json";

@interface EntityDetailViewController ()

- (void)commonInitWithEntityID:(NSString*)entityID andSearchResult:(SearchResult*)searchResult;

@end

@implementation EntityDetailViewController

@synthesize synchronousWrapper = _synchronousWrapper;
@synthesize loadingView = loadingView_;
@synthesize referringStamp = referringStamp_;
@synthesize entityDetail = entityDetail_;
@synthesize operationQueue = operationQueue_;


- (id)initWithEntityID:(NSString*)entityID {
  self = [super init];
  if (self) {
    [self commonInitWithEntityID:entityID andSearchResult:nil];
  }
  return self;
}

- (id)initWithEntityObject:(Entity*)entity {
  self = [super init];
  if (self) {
    [self commonInitWithEntityID:entity.entityID andSearchResult:nil];
  }
  return self;
}

- (id)initWithSearchResult:(SearchResult*)searchResult {
  self = [super init];
  if (self) {
    [self commonInitWithEntityID:nil andSearchResult:searchResult];
  }
  return self;
}

- (void)commonInitWithEntityID:(NSString*)entityID andSearchResult:(SearchResult*)searchResult {
  operationQueue_ = [[NSOperationQueue alloc] init];
  if (entityID) {
    [[STStampedAPI sharedInstance] entityDetailForEntityID:entityID andCallback:^(id<STEntityDetail> detail, NSError* error) {
      [self didLoadEntityDetail:detail];
    }];
  }
  else if (searchResult) {
    [[STStampedAPI sharedInstance] entityDetailForSearchID:searchResult.searchID andCallback:^(id<STEntityDetail> detail) {
      [self didLoadEntityDetail:detail];
    }];
  }
  [self.loadingView startAnimating];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.scrollView.scrollsToTop = YES;
  STToolbarView* toolbar = [[[STToolbarView alloc] init] autorelease];
  [self setToolbar:toolbar withAnimation:YES];
  
}

- (void)dealloc {
  if (self.synchronousWrapper) {
    self.synchronousWrapper.delegate = nil;
  }
  [self.operationQueue cancelAllOperations];
  [operationQueue_ release];
  [entityDetail_ release];
  self.loadingView = nil;
  self.referringStamp = nil;
  self.synchronousWrapper = nil;
  [super dealloc];
}

- (void)didLoadEntityDetail:(id<STEntityDetail>)anEntityDetail {
  entityDetail_ = [anEntityDetail retain];
  if (self.entityDetail) {
    
    [self.loadingView stopAnimating];
    [self.loadingView removeFromSuperview];
    self.synchronousWrapper = [STSynchronousWrapper wrapperForEntityDetail:self.entityDetail 
                                                                 withFrame:CGRectMake(0, 0, 320, self.scrollView.frame.size.height) 
                                                                  andStyle:@"EntityDetail" 
                                                                  delegate:self.scrollView];
    [self.scrollView appendChildView:self.synchronousWrapper];
    NSMutableArray* views = [NSMutableArray arrayWithObjects:
                             [[[STStampButton alloc] initWithEntity:anEntityDetail] autorelease],
                             nil];
    STToolbarView* toolbar = (STToolbarView*) self.toolbar;
    [toolbar packViews:views];
    //[toolbar addSubview:[views objectAtIndex:0]];
    [toolbar setNeedsLayout];
  }
}

/*
- (void)reloadData {
  [self performSelector:@selector(shouldFinishLoading) withObject:nil afterDelay:.5];
}
*/

@end
