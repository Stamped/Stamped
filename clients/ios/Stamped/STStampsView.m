//
//  STStampsView.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampsView.h"
#import "STStampedAPI.h"
#import "Util.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STStampCell.h"

static const NSInteger _batchSize = 20;

@interface STStampsView () <UITableViewDataSource, UITableViewDelegate>

@property (nonatomic, readwrite, retain) NSMutableArray<STStamp>* stamps;
@property (nonatomic, readwrite, assign) NSInteger offset;
@property (nonatomic, readwrite, assign) NSInteger maxRow;
@property (nonatomic, readwrite, assign) BOOL noMoreStamps;
@property (nonatomic, readwrite, assign) BOOL waiting;
@property (nonatomic, readwrite, assign) NSInteger generation;

- (void)populateStamps;
- (BOOL)shouldLoadMore;

@end

@implementation STStampsView

@synthesize slice = _slice;
@synthesize stamps = _stamps;
@synthesize offset = _offset;
@synthesize maxRow = _maxRow;
@synthesize noMoreStamps = _noMoreStamps;
@synthesize waiting = _waiting;
@synthesize generation = _generation;

- (id)initWithFrame:(CGRect)frame
{
  self = [super initWithFrame:frame];
  if (self) {
    self.delegate = self;
    self.dataSource = self;
    self.rowHeight = 96;
  }
  return self;
}

- (void)dealloc
{
  [_slice release];
  [_stamps release];
  [super dealloc];
}

- (void)setSlice:(STGenericSlice *)slice {
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
  [self reloadData];
}

- (void)populateStamps {
  if ([self shouldLoadMore]) {
    NSInteger curBatch = MIN(_batchSize, self.slice.limit.integerValue-self.offset);
    
    STGenericCollectionSlice* curSlice = [self.slice resizedSliceWithLimit:[NSNumber numberWithInteger:curBatch] andOffset:[NSNumber numberWithInteger:self.offset]];
    self.offset += curBatch;
    self.waiting = YES;
    NSInteger thisGeneration = self.generation;
    void (^callback)(NSArray<STStamp>*, NSError*, STCancellation*) = ^(NSArray<STStamp>* stamps, NSError* error, STCancellation* cancellation) {
      if (thisGeneration == self.generation) {
        [self.stamps addObjectsFromArray:stamps];
        self.waiting = NO;
        if ([stamps count] > 0) {
          [self reloadData];
          [self populateStamps];
        }
        else {
          self.noMoreStamps = YES;
          [self reloadData];
        }
      }
      else {
        NSLog(@"ignoring old request");
      }
    };
    [[STStampedAPI sharedInstance] stampsForInboxSlice:curSlice andCallback:callback];
  }
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
    STStampCell* cell = [[[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"testing"] autorelease];
    [cell setupWithStamp:[self.stamps objectAtIndex:indexPath.row]];
    self.maxRow = MAX(self.maxRow, indexPath.row);
    [self populateStamps];
    return cell;
  }
}


- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  
  id<STStamp> stamp = [self.stamps objectAtIndex:indexPath.row];
  /*
   if (entity.stamps.count > 0) {
   NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
   NSArray* sortedStamps = [entity.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
   User* currentUser = [AccountManager sharedManager].currentUser;
   NSSet* following = currentUser.following;
   if (!following)
   following = [NSSet set];
   
   sortedStamps = [sortedStamps filteredArrayUsingPredicate:[NSPredicate predicateWithFormat:@"(user IN %@ OR user.userID == %@) AND deleted == NO", following, currentUser.userID]];
   stamp = [sortedStamps lastObject];
   } else {
   stamp = [entity.stamps anyObject];
   }
   */
  STActionContext* context = [STActionContext context];
  context.stamp = stamp;
  id<STAction> action = [STStampedActions actionViewStamp:stamp.stampID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)reloadStampedData {
  self.slice = self.slice;
  [self reloadData];
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

@end
