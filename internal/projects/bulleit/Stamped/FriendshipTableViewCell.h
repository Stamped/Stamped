//
//  FriendshipTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 9/13/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "PeopleTableViewCell.h"

@interface FriendshipTableViewCell : PeopleTableViewCell

@property (nonatomic, readonly) UIActivityIndicatorView* indicator;
@property (nonatomic, readonly) UIButton* followButton;
@property (nonatomic, readonly) UIButton* unfollowButton;

@end
