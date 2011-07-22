//
//  StampDetailCommentView.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/21/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Comment;

@interface StampDetailCommentView : UIView

- (id)initWithComment:(Comment*)comment;

@property (nonatomic, retain) Comment* comment;

@end
