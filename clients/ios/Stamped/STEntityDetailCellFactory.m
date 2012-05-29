//
//  STEntityDetailCellFactory.m
//  Stamped
//
//  Created by Landon Judkins on 5/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntityDetailCellFactory.h"
#import "STEntityDetail.h"
#import "STConsumptionCell.h"
#import "STDebug.h"
#import "STErrorCellFactory.h"

@implementation STEntityDetailCellFactory

static id _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STEntityDetailCellFactory alloc] init];
}

+ (STEntityDetailCellFactory *)sharedInstance {
    return _sharedInstance;
}

- (UITableViewCell*)cellForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
    if ([[data class] conformsToProtocol:@protocol(STEntityDetail)]) {
        return [[[STConsumptionCell alloc] initWithEntityDetail:data] autorelease];
    }
    else {
        [STDebug log:[NSString stringWithFormat:@"%@ created error cell because %@ was not a stamp", self, data]];
        return [[STErrorCellFactory sharedInstance] cellForTableView:tableView data:data andStyle:style];
    }
}

- (CGFloat)cellHeightForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
    if ([[data class] conformsToProtocol:@protocol(STEntityDetail)]) {
        return [STConsumptionCell cellHeightForEntityDetail:data];
    }
    else {
        return [[STErrorCellFactory sharedInstance] cellHeightForTableView:tableView data:data andStyle:style];
    }
}

- (CGFloat)loadingCellHeightForTableView:(UITableView*)tableView andStyle:(NSString*)style {
    return 250;
}

- (STCancellation*)prepareForData:(id)data 
                         andStyle:(NSString*)style 
                     withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
    if ([[data class] conformsToProtocol:@protocol(STEntityDetail)]) {
        return [STConsumptionCell prepareForEntityDetail:data withCallback:block];
    }
    return [STCancellation dispatchNoopCancellationWithCallback:block];
}


@end
