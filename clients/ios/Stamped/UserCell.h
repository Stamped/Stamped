//
//  UserCell.h
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STUser.h"

@interface UserCell : UITableViewCell

- (id)initWithUser:(id<STUser>)user;

@end
