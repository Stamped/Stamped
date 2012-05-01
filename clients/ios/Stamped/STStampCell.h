//
//  STStampCell.h
//  Stamped
//
//  Created by Landon Judkins on 4/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"

@interface STStampCell : UITableViewCell

- (id)initWithStamp:(id<STStamp>)stamp;

+ (CGFloat)heightForStamp:(id<STStamp>)stamp;

@end
