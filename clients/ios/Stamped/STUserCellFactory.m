//
//  STUserCellFactory.m
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STUserCellFactory.h"
#import "STErrorCellFactory.h"
#import "STUserCell.h"
#import "STUserDetail.h"
#import "STStampPreview.h"

@implementation STUserCellFactory

static id _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STUserCellFactory alloc] init];
}

+ (STUserCellFactory*)sharedInstance {
  return _sharedInstance;
}

- (UITableViewCell*)cellForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
  if ([[data class] conformsToProtocol:@protocol(STUserDetail)]) {
    STUserCell* cell = [[[STUserCell alloc] initWithReuseIdentifier:@"TODO"] autorelease];
    cell.user = data;
    return cell;
  }
    if ([[data class] conformsToProtocol:@protocol(STStampPreview)]) {
        STUserCell* cell = [[[STUserCell alloc] initWithReuseIdentifier:@"TODO"] autorelease];
        cell.user = (id)[data user];
        return cell;
    }
  else {
    return [[STErrorCellFactory sharedInstance] cellForTableView:tableView data:data andStyle:style];
  }
}

- (CGFloat)cellHeightForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
  if ([[data class] conformsToProtocol:@protocol(STUserDetail)]) {
    return 52;
  }
  else {
    return [[STErrorCellFactory sharedInstance] cellHeightForTableView:tableView data:data andStyle:style];
  }
}

- (CGFloat)loadingCellHeightForTableView:(UITableView*)tableView andStyle:(NSString*)style {
  return 52;
}

- (STCancellation*)prepareForData:(id)data 
                         andStyle:(NSString*)style 
                     withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
  return [STCancellation dispatchNoopCancellationWithCallback:block];
}

@end
