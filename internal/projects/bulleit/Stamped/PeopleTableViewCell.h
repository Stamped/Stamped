//
//  PeopleTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class User;

@interface PeopleTableViewCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) User* user;
@property (nonatomic, readonly) UIImageView* disclosureArrowImageView;
@property (nonatomic, readonly) UIActivityIndicatorView* indicator;
@property (nonatomic, readonly) UIButton* followButton;
@property (nonatomic, readonly) UIButton* unfollowButton;

@end
