//
//  STGenericCellFactory.m
//  Stamped
//
//  Created by Landon Judkins on 5/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericCellFactory.h"
#import "STStampCellFactory.h"
#import "STUserCellFactory.h"
#import "STErrorCellFactory.h"
#import "STEntityDetailCellFactory.h"
#import "STUserDetail.h"
#import "STStamp.h"
#import "STDebug.h"
#import "STEntityDetail.h"

@implementation STGenericCellFactory

static id _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STGenericCellFactory alloc] init];
}

+ (STGenericCellFactory*)sharedInstance {
  return _sharedInstance;
}

- (UITableViewCell*)cellForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
  if ([[data class] conformsToProtocol:@protocol(STStamp)]) {
    return [[STStampCellFactory sharedInstance] cellForTableView:tableView data:data andStyle:style];
  }
  else if ([[data class] conformsToProtocol:@protocol(STUserDetail)]) {
    return [[STUserCellFactory sharedInstance] cellForTableView:tableView data:data andStyle:style];
  }
  else if ([[data class] conformsToProtocol:@protocol(STEntityDetail)]) {
      return [[STEntityDetailCellFactory sharedInstance] cellForTableView:tableView data:data andStyle:style];
  }
  else {
    [STDebug log:[NSString stringWithFormat:@"%@ created error cell because %@ was not a recognized model", self, data]];
    return [[STErrorCellFactory sharedInstance] cellForTableView:tableView data:data andStyle:style];
  }
}

- (CGFloat)cellHeightForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
  if ([[data class] conformsToProtocol:@protocol(STStamp)]) {
    return [[STStampCellFactory sharedInstance] cellHeightForTableView:tableView data:data andStyle:style];
  }
  else if ([[data class] conformsToProtocol:@protocol(STUserDetail)]) {
    return [[STUserCellFactory sharedInstance] cellHeightForTableView:tableView data:data andStyle:style];
  }
  else if ([[data class] conformsToProtocol:@protocol(STEntityDetail)]) {
      return [[STEntityDetailCellFactory sharedInstance] cellHeightForTableView:tableView data:data andStyle:style];
  }
  else {
    return [[STErrorCellFactory sharedInstance] cellHeightForTableView:tableView data:data andStyle:style];
  }
}

- (CGFloat)loadingCellHeightForTableView:(UITableView*)tableView andStyle:(NSString*)style {
  return tableView.rowHeight > 10 ? tableView.rowHeight : 90;
}

- (STCancellation*)prepareForData:(id)data 
                         andStyle:(NSString*)style 
                     withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
  if ([[data class] conformsToProtocol:@protocol(STStamp)]) {
    return [[STStampCellFactory sharedInstance] prepareForData:data andStyle:style withCallback:block];
  }
  else if ([[data class] conformsToProtocol:@protocol(STUserDetail)]) {
    return [[STUserCellFactory sharedInstance] prepareForData:data andStyle:style withCallback:block];
  }
  else if ([[data class] conformsToProtocol:@protocol(STEntityDetail)]) {
      return [[STEntityDetailCellFactory sharedInstance] prepareForData:data andStyle:nil withCallback:block];
  }
  else {
    return [[STErrorCellFactory sharedInstance] prepareForData:data andStyle:style withCallback:block];
  }
}


@end
