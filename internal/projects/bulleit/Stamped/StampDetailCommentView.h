//
//  StampDetailCommentView.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/21/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "TTTAttributedLabel.h"

@class Comment;
@class UserImageView;
@class StampDetailCommentView;

@protocol StampDetailCommentViewDelegate
- (BOOL)commentViewShouldBeginEditing:(StampDetailCommentView*)commentView;
- (void)commentViewUserImageTapped:(StampDetailCommentView*)commentView;
- (void)commentViewDeleteButtonPressed:(StampDetailCommentView*)commentView;
@end

@interface StampDetailCommentView : UIView <TTTAttributedLabelDelegate>

- (id)initWithComment:(Comment*)comment;

@property (nonatomic, retain) Comment* comment;
@property (nonatomic, assign) BOOL editing;
@property (nonatomic, assign) id<StampDetailCommentViewDelegate> delegate;

@end
