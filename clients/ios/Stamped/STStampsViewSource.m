//
//  STStampsViewSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampsViewSource.h"
#import "STLegacyStampCell.h"
#import "STStampedAPI.h"
#import "Util.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "STRippleBar.h"
#import "STPreviewsView.h"
#import "STStampCell.h"
#import "STLazyList.h"

static const NSInteger _batchSize = 20;

@interface STStampsViewSource ()

@property (nonatomic, readwrite, retain) NSMutableArray<STStamp>* stamps;
@property (nonatomic, readwrite, assign) NSInteger offset;
@property (nonatomic, readwrite, assign) NSInteger maxRow;
@property (nonatomic, readwrite, assign) BOOL noMoreStamps;
@property (nonatomic, readwrite, assign) BOOL waiting;
@property (nonatomic, readwrite, assign) NSInteger generation;
@property (nonatomic, readonly, retain) NSMutableSet* cancellations;
@property (nonatomic, readwrite, assign) NSInteger firstStampOffset;

- (void)populateStamps;
- (BOOL)shouldLoadMore;

@end

@implementation STStampsViewSource

@synthesize firstStampOffset = firstStampOffset_;
@synthesize showSearchBar = showSearchBar_;
@synthesize mainSection = mainSection_;
@synthesize slice = _slice;
@synthesize stamps = _stamps;
@synthesize offset = _offset;
@synthesize maxRow = _maxRow;
@synthesize noMoreStamps = _noMoreStamps;
@synthesize waiting = _waiting;
@synthesize generation = _generation;
@synthesize table = _table;
@synthesize loadingText = _loadingText;
@synthesize lastCellText = _lastCellText;
@synthesize noStampsText = _noStampsText;
@synthesize flareSet = _flareSet;
@synthesize delegate = _delegate;
@synthesize cancellations = cancellations_;

- (id)init {
  self = [super init];
  if (self) {
    _loadingText = @"Loading...";
    _lastCellText = @"No more stamps";
    _noStampsText = @"No stamps available";
    cancellations_ = [[NSMutableSet alloc] init];
  }
  return self;
}

- (void)dealloc {
  [_slice release];
  [_stamps release];
  [_loadingText release];
  [_lastCellText release];
  [_noStampsText release];
  [_flareSet release];
  [super dealloc];
}

- (void)setShowSearchBar:(BOOL)showSearchBar {
  
}

- (void)setSlice:(STGenericCollectionSlice *)slice {
  [_slice autorelease];
  _slice = [slice retain];
  if (slice.limit == nil) {
    slice.limit = [NSNumber numberWithInteger:NSIntegerMax];
  }
  if (slice.offset == nil) {
    slice.offset = [NSNumber numberWithInteger:0];
  }
  self.stamps = [NSMutableArray array];
  self.offset = slice.offset.integerValue;
  self.maxRow = 0;
  self.noMoreStamps = NO;
  self.waiting = NO;
  self.generation += 1;
  [self populateStamps];
  [self.table reloadData];
}

- (void)populateStamps {
  if ([self shouldLoadMore]) {
    NSInteger curBatch = MIN(_batchSize, self.slice.limit.integerValue-self.offset);
    
    STGenericCollectionSlice* curSlice = [self.slice resizedSliceWithLimit:[NSNumber numberWithInteger:curBatch] andOffset:[NSNumber numberWithInteger:self.offset]];
    self.offset += curBatch;
    self.waiting = YES;
    NSInteger thisGeneration = self.generation;
    void (^callback)(NSArray<STStamp>*, NSError*, STCancellation* cancellation) = ^(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation) {
      [self.cancellations removeObject:cancellation];
      if (thisGeneration == self.generation) {
        [self.stamps addObjectsFromArray:stamps];
        self.waiting = NO;
        if ([stamps count] > 0) {
          [self.table reloadData];
          [self populateStamps];
        }
        else {
          self.noMoreStamps = YES;
          [self.table reloadData];
        }
      }
      else {
        NSLog(@"ignoring old request");
      }
    };
    STCancellation* cancellation = [self makeStampedAPICallWithSlice:curSlice andCallback:callback];
    [self.cancellations addObject:cancellation];
  }
}

- (STCancellation*)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice 
                                   andCallback:(void (^)(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation))block {
  return [[STStampedAPI sharedInstance] stampsForInboxSlice:slice andCallback:block];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  if (section < self.mainSection) {
    return 0;
  }
  else if (section > self.mainSection) {
    return 1;
  }
  else {
    NSInteger result = 0;
    if (self.stamps) {
      result = [self.stamps count] + self.firstStampOffset;
    }
    return result;
  }
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return self.mainSection+2;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  if (indexPath.section < self.mainSection) {
    NSAssert(NO, @"Subclass must handle sections before mainSection");
    return nil;
  }
  else if (indexPath.section > self.mainSection) {
    UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"lastCell"] autorelease];
    if (self.shouldLoadMore || self.waiting) {
      cell.textLabel.text = self.loadingText;
    }
    else {
      cell.textLabel.text = [tableView.dataSource tableView:tableView numberOfRowsInSection:0] > 0 ? self.lastCellText : self.noStampsText ;
    }
    cell.textLabel.textAlignment = UITextAlignmentCenter;
    cell.textLabel.textColor = [UIColor stampedGrayColor];
    cell.textLabel.font = [UIFont stampedFontWithSize:20];
    [cell setNeedsLayout];
    return cell;
  }
  else {
    if (indexPath.row >= self.firstStampOffset) {
        static NSString *CellIdentifier = @"CellIdentifier";
        id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row + self.firstStampOffset];
        STStampCell* cell = [[[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        [cell setupWithStamp:stamp];
        self.maxRow = MAX(self.maxRow, indexPath.row);
        [self populateStamps];
        return cell;
    }
    else {
      NSAssert(NO,@"Not implemented yet");
      return nil;
    }
  }
}

- (id<STStamp>)stampForIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.section == self.mainSection) {
    if (indexPath.row >= self.firstStampOffset) {
      id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row + self.firstStampOffset];
      return stamp;
    }
  }
  return nil;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  if (indexPath.section == self.mainSection) {
    if (indexPath.row >= self.firstStampOffset) {
      id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row + self.firstStampOffset];
      STActionContext* context = [STActionContext context];
      context.stamp = stamp;
      id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
      [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
    }
  }
  else if (indexPath.section > self.mainSection) {
    if (!self.shouldLoadMore && !self.waiting) { 
      if ([tableView.dataSource tableView:tableView numberOfRowsInSection:0] > 0) {
        [self selectedLastCell];
      }
      else {
        [self selectedNoStampsCell];
      }
    }
  }
  else {
    //Nothing, for subclasses
  }
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
  if (indexPath.section == self.mainSection) {
    if (indexPath.row >= self.firstStampOffset) {
      id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row + self.firstStampOffset];
      return [STStampCell heightForStamp:stamp];
    }
    else {
      return 40;
    }
  }
  else {
    return [STStampCell heightForStamp:nil];
  }
  /*
   CGFloat defaultHeight = 96;
   if (indexPath.section == self.mainSection) {
   id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row];
   defaultHeight += [STPreviewsView previewHeightForStamp:stamp andMaxRows:1];
   }
   return defaultHeight;
   */
}

- (void)reloadStampedData {
  [self cancelPendingOperations];
  [self.stamps removeAllObjects];
  [self resumeOperations];
}

- (BOOL)shouldLoadMore {
  if ([self.stamps count] < self.slice.limit.integerValue && !self.waiting) {
    if (self.maxRow + _batchSize * 2 > [self.stamps count]) {
      NSLog(@"%d", self.noMoreStamps);
      return !self.noMoreStamps;
    }
  }
  return NO;
}

- (void)setTable:(UITableView *)table {
  _table.delegate = nil;
  _table.dataSource = nil;
  [_table autorelease];
  _table = [table retain];
  if (_table) {
    _table.delegate = self;
    _table.dataSource = self;
    [_table reloadData];
  }
}

- (void)cancelPendingOperations {
  NSLog(@"CancelPendingOperations");
  for (STCancellation* cancellation in self.cancellations) {
    [cancellation cancel];
  }
  [self.cancellations removeAllObjects];
  self.waiting = NO;
}

- (void)selectedNoStampsCell {
  
}

- (void)selectedLastCell {
  
}

- (void)resumeOperations {
  [self populateStamps];
}

- (void)reduceStampCache {
  [self cancelPendingOperations];
  if (self.stamps.count > _batchSize) {
    [self.stamps removeObjectsInRange:NSMakeRange(_batchSize, self.stamps.count - _batchSize)];
  }
}

@end
