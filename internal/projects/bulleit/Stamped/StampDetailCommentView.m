//
//  StampDetailCommentView.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/21/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampDetailCommentView.h"

#import "Comment.h"
#import "User.h"
#import "UserImageView.h"

@interface StampDetailCommentView ()
- (void)initViews;
@end

@implementation StampDetailCommentView

@synthesize comment = comment_;

- (id)initWithComment:(Comment*)comment {
  self = [super initWithFrame:CGRectZero];
  if (self) {
    self.backgroundColor = [UIColor clearColor];
    self.comment = comment;
    [self initViews];
  }
  return self;
}

- (void)initViews {
  UserImageView* userImage = [[UserImageView alloc] initWithFrame:CGRectMake(10, 8, 31, 31)];
  userImage.image = comment_.user.profileImage;
  [self addSubview:userImage];
  [userImage release];
  CGFloat minHeight = CGRectGetMaxY(userImage.frame) + 8;

  UIFont* nameFont = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  const CGFloat leftPadding = CGRectGetMaxX(userImage.frame) + 8;
  CGSize stringSize = [comment_.user.displayName sizeWithFont:nameFont
                                                     forWidth:260
                                                lineBreakMode:UILineBreakModeTailTruncation];
  UILabel* nameLabel = [[UILabel alloc] initWithFrame:CGRectMake(leftPadding, 8, stringSize.width, stringSize.height)];
  nameLabel.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  nameLabel.text = comment_.user.displayName;
  nameLabel.font = nameFont;
  [self addSubview:nameLabel];
  [nameLabel release];
  
  UILabel* commentLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  UIFont* commentFont = [UIFont fontWithName:@"Helvetica" size:12];
  commentLabel.font = commentFont;
  commentLabel.text = comment_.blurb;
  commentLabel.textColor = [UIColor colorWithWhite:0.35 alpha:1.0];
  commentLabel.numberOfLines = 0;
  stringSize = [comment_.blurb sizeWithFont:commentFont
                          constrainedToSize:CGSizeMake(210, MAXFLOAT)
                              lineBreakMode:commentLabel.lineBreakMode];
  commentLabel.frame = CGRectMake(leftPadding, 23, stringSize.width, stringSize.height);
  [self addSubview:commentLabel];
  [commentLabel release];
  
  CGRect frame = self.frame;
  frame.size.height = fmaxf(minHeight, CGRectGetMaxY(commentLabel.frame) + 8);
  self.frame = frame;
}

- (void)drawRect:(CGRect)rect {
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSaveGState(ctx);
  CGContextSetFillColorWithColor(ctx, [UIColor colorWithWhite:0.9 alpha:1.0].CGColor);
  CGContextFillRect(ctx, CGRectMake(0, CGRectGetMaxY(self.bounds) - 1, CGRectGetWidth(self.bounds), 1));
  CGContextRestoreGState(ctx);
}

@end
