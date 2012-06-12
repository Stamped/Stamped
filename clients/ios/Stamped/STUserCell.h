//
//  STUserCell.h
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STUser.h"

@interface STUserCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, readwrite, retain) id<STUser> user;
@property (nonatomic, readonly) UIImageView* disclosureArrowImageView;
@property (nonatomic, readonly) UIActivityIndicatorView* indicator;
@property (nonatomic, readonly) UIButton* followButton;
@property (nonatomic, readonly) UIButton* unfollowButton;

@end
