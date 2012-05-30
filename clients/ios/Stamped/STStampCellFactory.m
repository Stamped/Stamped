//
//  STStampCellFactory.m
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampCellFactory.h"
#import "STErrorCellFactory.h"
#import "STStamp.h"
#import "STStampCell.h"
#import "STCellStyles.h"
#import "STConsumptionCell.h"
#import "Util.h"
#import "STDebug.h"

@implementation STStampCellFactory

static STStampCellFactory* _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STStampCellFactory alloc] init];
}

+ (STStampCellFactory*)sharedInstance {
    return _sharedInstance;
}

- (UITableViewCell*)cellForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
    if ([[data class] conformsToProtocol:@protocol(STStamp)]) {
        
        
        STStampCell *cell = [tableView dequeueReusableCellWithIdentifier:[STStampCell cellIdentifier]];
        if (cell == nil) {
            cell = [[[STStampCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:[STStampCell cellIdentifier]] autorelease];
        }
        [cell setupWithStamp:data];
        return cell;
    }
    else {
        [STDebug log:[NSString stringWithFormat:@"%@ created error cell because %@ was not a stamp", self, data]];
        return [[STErrorCellFactory sharedInstance] cellForTableView:tableView data:data andStyle:style];
    }
}

- (CGFloat)cellHeightForTableView:(UITableView*)tableView data:(id)data andStyle:(NSString*)style {
    if ([[data class] conformsToProtocol:@protocol(STStamp)]) {
        
        return [STStampCell heightForStamp:data];
    }
    else {
        return [[STErrorCellFactory sharedInstance] cellHeightForTableView:tableView data:data andStyle:style];
    }
}

- (CGFloat)loadingCellHeightForTableView:(UITableView*)tableView andStyle:(NSString*)style {
    return 91;
}

- (STCancellation*)prepareForData:(id)data 
                         andStyle:(NSString*)style 
                     withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
    if ([[data class] conformsToProtocol:@protocol(STStamp)]) {
        return [STStampCell prepareForStamp:data withCallback:block];
    }
    return [STCancellation dispatchNoopCancellationWithCallback:block];
}

@end
