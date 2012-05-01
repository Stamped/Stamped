//
//  STTableDelegator.m
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTableDelegator.h"

@interface STTableDelegator ()

@property (nonatomic, readonly, retain) NSMutableArray* tableDelegates;
@property (nonatomic, readonly, retain) NSMutableArray* sectionMappings;

@end

@implementation STTableDelegator

@synthesize tableDelegates = tableDelegates_;
@synthesize sectionMappings = sectionMappings_;

- (id)init {
  self = [super init];
  if (self) {
    tableDelegates_ = [[NSMutableArray alloc] init];
    sectionMappings_ = [[NSMutableArray alloc] init];
  }
  return self;
}

- (void)dealloc
{
  [tableDelegates_ release];
  [sectionMappings_ release];
  [super dealloc];
}

- (void)appendTableDelegate:(id<STTableDelegate>)tableDelegate {
  [self appendTableDelegate:tableDelegate withSectionMapping:0];
}

- (void)appendTableDelegate:(id<STTableDelegate>)tableDelegate withSectionMapping:(NSInteger)sectionMapping {
  [self.tableDelegates addObject:tableDelegate];
  [self.sectionMappings addObject:[NSNumber numberWithInteger:sectionMapping]];
}

- (NSInteger)mapSection:(NSInteger)section {
  return [[self.sectionMappings objectAtIndex:section] integerValue];
}

- (NSIndexPath*)mapPath:(NSIndexPath*)indexPath {
  return [NSIndexPath indexPathForRow:indexPath.row inSection:[self mapSection:indexPath.section]];
}

- (id<STTableDelegate>)delegateForSection:(NSInteger)section {
  return [self.tableDelegates objectAtIndex:section];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  return [[self delegateForSection:section] tableView:tableView numberOfRowsInSection:[self mapSection:section]];
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return self.tableDelegates.count;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  return [[self delegateForSection:indexPath.section] tableView:tableView cellForRowAtIndexPath:[self mapPath:indexPath]];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  [[self delegateForSection:indexPath.section] tableView:tableView didSelectRowAtIndexPath:[self mapPath:indexPath]];
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
  return [[self delegateForSection:indexPath.section] tableView:tableView heightForRowAtIndexPath:[self mapPath:indexPath]];
}

- (void)reloadStampedData {
  NSSet* delegates = [NSSet setWithArray:self.tableDelegates];
  for (id<STTableDelegate> delegate in delegates) {
    [delegate reloadStampedData];
  }
}

@end
