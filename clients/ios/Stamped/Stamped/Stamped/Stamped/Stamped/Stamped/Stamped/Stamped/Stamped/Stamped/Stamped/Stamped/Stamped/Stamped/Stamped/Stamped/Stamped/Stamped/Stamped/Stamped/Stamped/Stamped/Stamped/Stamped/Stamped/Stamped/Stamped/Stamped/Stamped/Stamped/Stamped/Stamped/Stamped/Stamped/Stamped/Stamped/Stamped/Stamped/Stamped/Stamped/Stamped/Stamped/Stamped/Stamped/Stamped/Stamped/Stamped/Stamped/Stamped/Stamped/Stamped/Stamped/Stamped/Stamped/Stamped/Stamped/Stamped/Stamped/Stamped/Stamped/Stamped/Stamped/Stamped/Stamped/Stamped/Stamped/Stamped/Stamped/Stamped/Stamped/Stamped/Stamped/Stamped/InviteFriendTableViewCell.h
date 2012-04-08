//
//  InviteFriendTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 11/6/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class UserImageView;

@interface InviteFriendTableViewCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) UIButton* inviteButton;
@property (nonatomic, readonly) UILabel* emailLabel;
@property (nonatomic, readonly) UILabel* nameLabel;

@end
