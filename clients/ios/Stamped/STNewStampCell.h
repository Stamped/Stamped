//
//  STNewStampCell.h
//  Stamped
//
//  Created by Landon Judkins on 7/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"

@interface STNewStampCell : UITableViewCell

- (void)setupWithStamp:(id<STStamp>)stamp;

+ (CGFloat)heightForStamp:(id<STStamp>)stamp;

@end
