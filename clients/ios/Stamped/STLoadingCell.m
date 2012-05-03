//
//  STLoadingCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STLoadingCell.h"

@implementation STLoadingCell

- (id)init
{
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"TODO"];
    if (self) {
      self.accessoryType = UITableViewCellAccessoryNone;
      self.selectionStyle = UITableViewCellSelectionStyleNone;
      UIActivityIndicatorView* activityView = [[[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray] autorelease];
      activityView.frame = self.frame;
      self.autoresizingMask = UIViewAutoresizingFlexibleHeight | UIViewAutoresizingFlexibleWidth;
      activityView.autoresizingMask = UIViewAutoresizingFlexibleHeight | UIViewAutoresizingFlexibleWidth;
      [self addSubview:activityView];
      [activityView startAnimating];
    }
    return self;
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
    [super setSelected:selected animated:animated];
}

@end
