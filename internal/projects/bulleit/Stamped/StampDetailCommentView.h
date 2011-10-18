//
//  StampDetailCommentView.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/21/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Comment;
@class UserImageView;

extern NSString* const kCommentUserImageTappedNotification;

@interface StampDetailCommentView : UIView

- (id)initWithComment:(Comment*)comment;

@property (nonatomic, retain) Comment* comment;
@property (nonatomic, readonly) UserImageView* userImage;
@property (nonatomic, assign) BOOL borderHidden;

@end
