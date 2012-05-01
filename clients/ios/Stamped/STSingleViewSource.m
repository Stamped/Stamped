//
//  STSingleViewSource.m
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSingleViewSource.h"

@interface STSingleViewSource ()

@property (nonatomic, readonly, retain) UIView* view;

@end

@implementation STSingleViewSource

@synthesize view = view_;

- (id)initWithView:(UIView*)view {
  self = [super init];
  if (self) {
    view_ = [view retain];
  }
  return self;
}

- (void)dealloc
{
  [view_ release];
  [super dealloc];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
  return 1;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
  return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
  if (self.view.superview) {
    [self.view removeFromSuperview];
  }
  UITableViewCell* cell = [[[UITableViewCell alloc] initWithFrame:self.view.frame] autorelease];
  cell.accessoryType = UITableViewCellAccessoryNone;
  cell.selectionStyle = UITableViewCellSelectionStyleNone;
  [cell addSubview:self.view];
  return cell;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
  return self.view.frame.size.height;
}

- (void)reloadStampedData {
  if ([self.view respondsToSelector:@selector(reloadStampedData)]) {
    [(id)self.view reloadStampedData];
  }
}

@end
