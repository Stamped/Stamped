//
//  STConsumptionCell.h
//  Stamped
//
//  Created by Landon Judkins on 4/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"
#import "STCancellation.h"

@interface STConsumptionCell : UITableViewCell

- (id)initWithStamp:(id<STStamp>)stamp;

+ (CGFloat)cellHeightForStamp:(id<STStamp>)stamp;
+ (STCancellation*)prepareForStamp:(id<STStamp>)stamp withCallback:(void (^)(NSError* error, STCancellation* cancellation))block;

@end
