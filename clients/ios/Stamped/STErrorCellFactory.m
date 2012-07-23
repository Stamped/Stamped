//
//  STErrorCellFactory.m
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STErrorCellFactory.h"

@implementation STErrorCellFactory

static STErrorCellFactory* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STErrorCellFactory alloc] init];
}

+ (STErrorCellFactory*)sharedInstance {
  return _sharedInstance;
}

- (UITableViewCell*)cellForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
  UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:@"TODO"] autorelease];
  cell.textLabel.text = @"ERROR CELL, see log";
  cell.detailTextLabel.text = [NSString stringWithFormat:@"Data: %@ style: %@ table: %@", data, style, tableView];
  cell.detailTextLabel.lineBreakMode = UILineBreakModeWordWrap;
  return cell;
}

- (CGFloat)cellHeightForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
  return tableView.frame.size.height;
}

- (CGFloat)loadingCellHeightForTableView:(UITableView*)tableView andStyle:(NSString*)style {
  return 100;
}

- (STCancellation*)prepareForData:(id)data 
                         andStyle:(NSString*)style 
                     withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
  return [STCancellation dispatchNoopCancellationWithCallback:block];
}

@end
