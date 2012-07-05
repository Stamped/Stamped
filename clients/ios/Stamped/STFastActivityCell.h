//
//  STFastActivityCell.h
//  Stamped
//
//  Created by Landon Judkins on 6/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STActivity.h"
#import "STTypes.h"

@interface STFastActivityCell : UITableViewCell

- (id)initWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

+ (CGFloat)heightForCellWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

@end
