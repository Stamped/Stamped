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

#import "UIColor+Stamped.h"
#import "Notifications.h"
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

- (void)commonInitWithEntityID:(NSString*)entityID andSearchID:(NSString*)searchID;

@property (nonatomic, readonly, retain) NSString* entityID;
@property (nonatomic, readonly, retain) NSString* searchID;
@property (nonatomic, readwrite, retain) id<STEntityDetail> entityDetail;

@end

@implementation EntityDetailViewController

@synthesize synchronousWrapper = _synchronousWrapper;
@synthesize loadingView = loadingView_;
@synthesize referringStamp = referringStamp_;
@synthesize entityDetail = entityDetail_;
@synthesize searchID = _searchID;
@synthesize entityID = _entityID;
@synthesize toolbar = _toolbar;


- (id)initWithEntityID:(NSString*)entityID {
  self = [super init];
  if (self) {
    [self commonInitWithEntityID:entityID andSearchID:nil];
  }
  return self;
}

- (id)initWithSearchID:(NSString*)searchID {
  self = [super init];
  if (self) {
    [self commonInitWithEntityID:nil andSearchID:searchID];
  }
  return self;
}

- (void)commonInitWithEntityID:(NSString*)entityID andSearchID:(NSString*)searchID {
  _entityID = [entityID retain];
  _searchID = [searchID retain];
}

- (void)viewDidLoad {
  STToolbarView* toolbar = [[[STToolbarView alloc] init] autorelease];
  _toolbar = toolbar;
  [super viewDidLoad];
  [self reloadStampedData];
  
}

- (void)dealloc {
  if (self.synchronousWrapper) {
    self.synchronousWrapper.delegate = nil;
  }
  [entityDetail_ release];
  [_searchID release];
  [_entityID release];
  self.loadingView = nil;
  self.referringStamp = nil;
  self.synchronousWrapper = nil;
  [super dealloc];
}

static BOOL _addedStampButton = NO;

- (void)setEntityDetail:(id<STEntityDetail>)anEntityDetail {
  [entityDetail_ autorelease];
  entityDetail_ = [anEntityDetail retain];
  if (self.entityDetail) {
    
    [self.loadingView stopAnimating];
    //[self.loadingView removeFromSuperview];
    self.synchronousWrapper = [STSynchronousWrapper wrapperForEntityDetail:self.entityDetail 
                                                                 withFrame:CGRectMake(0, 0, self.view.bounds.size.width, self.scrollView.frame.size.height)
                                                                  andStyle:@"EntityDetail" 
                                                                  delegate:self.scrollView];
    [self.scrollView appendChildView:self.synchronousWrapper];
    NSMutableArray* views = [NSMutableArray arrayWithObjects:
                             [[[STStampButton alloc] initWithEntity:anEntityDetail] autorelease],
                             nil];
    if (!_addedStampButton) {
      STToolbarView* toolbar = (STToolbarView*) self.toolbar;
      [toolbar packViews:views];
      [toolbar addSubview:[views objectAtIndex:0]];
      [toolbar setNeedsLayout];
    }
  }
}

- (void)reloadStampedData {
  if (self.synchronousWrapper) {
    [self.scrollView removeChildView:self.synchronousWrapper withAnimation:YES];
    self.synchronousWrapper = nil;
  }
  if (self.entityID) {
    [self.loadingView startAnimating];
    [[STStampedAPI sharedInstance] entityDetailForEntityID:self.entityID 
                                               andCallback:^(id<STEntityDetail> detail, NSError *error, STCancellation *cancellation) {
                                                 self.entityDetail = detail;
                                               }];
  }
  else if (self.searchID) {
    [self.loadingView startAnimating];
    [[STStampedAPI sharedInstance] entityDetailForSearchID:self.searchID andCallback:^(id<STEntityDetail> detail) {
      self.entityDetail = detail;
    }];
  }
}

- (UIView *)toolbar {
  return _toolbar;
}

@end
