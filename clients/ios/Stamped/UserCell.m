//
//  UserCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/19/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "UserCell.h"

@implementation UserCell

- (id)initWithUser:(id<STUser>)user
{
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"UserCell"];
    if (self) {
      self.textLabel.text = user.screenName;
    }
    return self;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
    [super setSelected:selected animated:animated];
}

@end
