//
//  SuggestedUserTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/30/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class User;

@interface SuggestedUserTableViewCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) User* user;
@property (nonatomic, readonly) UIActivityIndicatorView* indicator;
@property (nonatomic, readonly) UIButton* followButton;
@property (nonatomic, readonly) UIButton* unfollowButton;
@property (nonatomic, readonly) UILabel* bioLabel;
@end
