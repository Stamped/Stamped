//
//  StampDetailAddCommentView.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/18/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class UserImageView;

@interface StampDetailAddCommentView : UIView

@property (nonatomic, readonly) UserImageView* userImageView;
@property (nonatomic, readonly) UITextField* commentTextField;

@end
