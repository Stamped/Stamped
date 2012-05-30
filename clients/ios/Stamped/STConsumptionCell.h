//
//  STConsumptionCell.h
//  Stamped
//
//  Created by Landon Judkins on 4/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STEntityDetail.h"
#import "STCancellation.h"

@interface STConsumptionCell : UITableViewCell

- (id)initWithEntityDetail:(id<STEntityDetail>)entityDetail;

+ (CGFloat)cellHeightForEntityDetail:(id<STEntityDetail>)entityDetail;

+ (STCancellation*)prepareForEntityDetail:(id<STEntityDetail>)entityDetail
                             withCallback:(void (^)(NSError* error, STCancellation* cancellation))block;

@end
