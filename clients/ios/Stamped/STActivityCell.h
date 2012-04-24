//
//  STActivityCell.h
//  Stamped
//
//  Created by Landon Judkins on 4/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STActivity.h"
#import "STStampedAPI.h"

@interface STActivityCell : UITableViewCell

- (id)initWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

+ (CGFloat)heightForCellWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

@end
