//
//  STStampDetailBlurbView.h
//  Stamped
//
//  Created by Andrew Bonventre on 3/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class UserImageView;
@class TTTAttributedLabel;

@interface STStampDetailBlurbView : UIView

@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) TTTAttributedLabel* nameLabel;
@property (nonatomic, readonly) UILabel* timestampLabel;
@property (nonatomic, readonly) TTTAttributedLabel* blurbLabel;

@end
