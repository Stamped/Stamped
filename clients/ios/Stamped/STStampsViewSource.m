//
//  STStampsViewSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampsViewSource.h"
#import "STStampCell.h"
#import "STStampedAPI.h"
#import "Util.h"
#import "STStampedActions.h"
#import "STActionManager.h"

static const NSInteger _batchSize = 20;

@interface STStampsViewSource ()

@property (nonatomic, readwrite, retain) NSMutableArray<STStamp>* stamps;
@property (nonatomic, readwrite, assign) NSInteger offset;
@property (nonatomic, readwrite, assign) NSInteger maxRow;
@property (nonatomic, readwrite, assign) BOOL noMoreStamps;
@property (nonatomic, readwrite, assign) BOOL waiting;
@property (nonatomic, readwrite, assign) NSInteger generation;

- (void)populateStamps;
- (BOOL)shouldLoadMore;

@end

@implementation STStampsViewSource

@synthesize slice = _slice;
@synthesize stamps = _stamps;
@synthesize offset = _offset;
@synthesize maxRow = _maxRow;
@synthesize noMoreStamps = _noMoreStamps;
@synthesize waiting = _waiting;
@synthesize generation = _generation;
@synthesize table = _table;

- (id)init
{
  self = [super init];
  if (self) {
  }
  return self;
}

- (void)dealloc
{
  [_slice release];
  [_stamps release];
  [super dealloc];
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
  self.stamps = [[NSMutableArray array] retain];
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
    void (^callback)(NSArray<STStamp>*, NSError*) = ^(NSArray<STStamp>* stamps, NSError* error) {
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
    [self makeStampedAPICallWithSlice:curSlice andCallback:callback];
  }
}

- (void)makeStampedAPICallWithSlice:(STGenericCollectionSlice*)slice andCallback:(void (^)(NSArray<STStamp>*, NSError*))block {
  [[STStampedAPI sharedInstance] stampsForInboxSlice:slice andCallback:block];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  if (section == 1) {
    return 1;
  }
  NSInteger result = 0;
  if (self.stamps) {
    result = [self.stamps count];
  }
  return result;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 2;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  if (indexPath.section == 1) {
    UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleValue1 reuseIdentifier:@"lastCell"] autorelease];
    if (self.shouldLoadMore || self.waiting) {
      cell.textLabel.text = @"Loading...";
    }
    else {
      cell.textLabel.text = @"No more stamps";
    }
    return cell;
  }
  else {
    STStampCell* cell = [[[STStampCell alloc] initWithReuseIdentifier:@"testing"] autorelease];
    cell.stamp = [self.stamps objectAtIndex:indexPath.row];
    self.maxRow = MAX(self.maxRow, indexPath.row);
    [self populateStamps];
    return cell;
  }
}


- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row];
  STActionContext* context = [STActionContext context];
  context.stamp = stamp;
  id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)reloadStampedData {
  self.slice = self.slice;
  [self.table reloadData];
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
    _table.rowHeight = 96;
    [_table reloadData];
  }
}

@end
