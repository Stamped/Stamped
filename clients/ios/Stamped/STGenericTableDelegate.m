//
//  STGenericTableDelegate.m
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericTableDelegate.h"
#import "STLoadingCell.h"

@interface STGenericTableDelegate () <STLazyListDelegate>

- (NSInteger)roundUpToPageBoundary:(NSInteger)count;

@property (nonatomic, readwrite, assign) BOOL endReached;
@property (nonatomic, readwrite, retain) NSMutableArray* prepareCancellations;

@end

@implementation STGenericTableDelegate

@synthesize lazyList = lazyList_;
@synthesize tableViewCellFactory = tableViewCellFactory_;
@synthesize style = style_;
@synthesize selectedCallback = selectedCallback_;
@synthesize preloadBufferSize = preloadBufferSize_;
@synthesize pageSize = pageSize_;
@synthesize tableShouldReloadCallback = tableShouldReloadCallback_;
@synthesize loadingCellDisabled = loadingCellDisabled_;
@synthesize endReached = endReached_;
@synthesize autoPrepareDisabled = autoPrepareDisabled_;
@synthesize prepareCancellations = prepareCancellations_;

- (id)init
{
  self = [super init];
  if (self) {
    preloadBufferSize_ = 20;
    pageSize_ = 20;
    prepareCancellations_ = [[NSMutableArray alloc] init];
  }
  return self;
}

- (void)dealloc
{
  [self cancelAndClearPreparations];
  [self cancelPendingRequests];
  [lazyList_ removeDelegate:self];
  [lazyList_ release];
  [tableViewCellFactory_ release];
  [style_ release];
  [selectedCallback_ release];
  [tableShouldReloadCallback_ release];
  [prepareCancellations_ release];
  [super dealloc];
}

- (void)cancelAndClearPreparations {
  for (STCancellation* cancellation in self.prepareCancellations) {
    [cancellation cancel];
  }
  [self.prepareCancellations removeAllObjects];
}

- (void)continuePreparations {
  if ([self.tableViewCellFactory respondsToSelector:@selector(prepareForData:andStyle:withCallback:)] &&
      self.lazyList.count > self.prepareCancellations.count &&
      !self.autoPrepareDisabled) {
    NSInteger index = self.prepareCancellations.count;
    id data = [self.lazyList objectAtIndex:index];
    __block STGenericTableDelegate* weakSelf = self;
    STCancellation* cancellation = [self.tableViewCellFactory prepareForData:data andStyle:self.style withCallback:^(NSError *error, STCancellation *cancellation2) {
      NSLog(@"preparedForDatum:%d",index);
      [weakSelf continuePreparations];
    }];
    [self.prepareCancellations addObject:cancellation];
  }
}

- (void)setLazyList:(id<STLazyList>)lazyList {
  [lazyList_ cancelPendingRequests];
  [lazyList_ removeDelegate:self];
  [lazyList_ autorelease];
  [self cancelAndClearPreparations];
  lazyList_ = [lazyList retain];
  [lazyList_ addDelegate:self];
  [lazyList_ prepareRange:NSMakeRange(0, [self roundUpToPageBoundary:self.preloadBufferSize])];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  if (self.lazyList) {
    NSInteger count = self.lazyList.count;
    if (!self.loadingCellDisabled && !self.endReached) {
      count++;
    }
    return count;
  }
  else {
    return 0;
  }
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  NSInteger prepareCount = 0 + self.preloadBufferSize;
  [self.lazyList prepareRange:NSMakeRange(0, [self roundUpToPageBoundary:prepareCount])];
  return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  NSInteger prepareCount = indexPath.row + self.preloadBufferSize;
  [self.lazyList prepareRange:NSMakeRange(0, [self roundUpToPageBoundary:prepareCount])];
  if (self.tableViewCellFactory) {
    if (indexPath.row < self.lazyList.count) {
      return [self.tableViewCellFactory cellForTableView:tableView data:[self.lazyList objectAtIndex:indexPath.row] andStyle:self.style];
    }
    else {
      return [[[STLoadingCell alloc] init] autorelease];
    }
  }
  else {
    return [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"TODO"] autorelease];
  }
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  NSLog(@"Selected Cell: %d inRow: %d", indexPath.row, indexPath.section);
  if (self.selectedCallback) {
    self.selectedCallback(self, tableView, indexPath);
  }
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
  if (self.tableViewCellFactory) {
    id data = nil;
    if (self.lazyList) {
      data = [self.lazyList objectAtIndex:indexPath.row];
      return [self.tableViewCellFactory cellHeightForTableView:tableView data:data andStyle:self.style];
    }
    else {
      return 100;
    }
  }
  else {
    return 0;
  }
}

- (void)reloadStampedData {
  if (self.lazyList) {
    [self cancelAndClearPreparations];
    [self.lazyList reload];
    self.endReached = NO;
  }
}

- (void)lazyListDidReload:(id<STLazyList>)lazyList {
  NSLog(@"did Reload");
  if (self.tableShouldReloadCallback) {
    self.endReached = NO;
    [self cancelAndClearPreparations];
    self.tableShouldReloadCallback(self);
  }
}

- (void)lazyListDidGrow:(id<STLazyList>)lazyList {
  NSLog(@"did grow");
  if (self.tableShouldReloadCallback) {
      [self continuePreparations];
    self.tableShouldReloadCallback(self);
  }
}

- (void)lazyListDidShrink:(id<STLazyList>)lazyList {
  NSLog(@"Did shrink");
  if (self.tableShouldReloadCallback) {
    NSInteger diff = self.prepareCancellations.count - lazyList.count;
    if (diff > 0) {
      NSArray* subset = [self.prepareCancellations subarrayWithRange:NSMakeRange(lazyList.count, diff)];
      for (STCancellation* cancellation in subset) {
        [cancellation cancel];
      }
      [self.prepareCancellations removeObjectsInArray:subset];
    }
    self.tableShouldReloadCallback(self);
  }
}

- (void)lazyListDidReachMaxCount:(id<STLazyList>)lazyList {
  NSLog(@"Did reach max");
  if (self.tableShouldReloadCallback) {
    self.endReached = YES;
    self.tableShouldReloadCallback(self);
  }
}

- (void)lazyListDidFail:(id<STLazyList>)lazyList {
  NSLog(@"did fail");
  if (self.tableShouldReloadCallback) {
    self.tableShouldReloadCallback(self);
  }
}

- (NSInteger)roundUpToPageBoundary:(NSInteger)count {
  NSInteger mod = count % self.pageSize;
  NSInteger result = count - mod;
  if (mod) {
    result += self.pageSize;
  }
  return result;
}

- (void)cancelPendingRequests {
  [self cancelAndClearPreparations];
  [self.lazyList cancelPendingRequests];
}

@end
