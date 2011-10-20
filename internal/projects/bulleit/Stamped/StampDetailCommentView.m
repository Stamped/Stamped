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
#import "UIColor+Stamped.h"
#import "Util.h"

NSString* const kCommentUserImageTappedNotification = @"kCommentUserImageTappedNotification";

@interface StampDetailCommentView ()
- (void)initViews;
- (void)userImageTapped:(id)sender;
@end

@implementation StampDetailCommentView

@synthesize comment = comment_;
@synthesize userImage = userImage_;

- (id)initWithComment:(Comment*)comment {
  self = [super initWithFrame:CGRectZero];
  if (self) {
    self.backgroundColor = [UIColor whiteColor];
    self.comment = comment;
    [self initViews];
  }
  return self;
}

- (void)initViews {
  userImage_ = [[UserImageView alloc] initWithFrame:CGRectMake(10, 8, 34, 34)];
  userImage_.imageURL = comment_.user.profileImageURL;
  userImage_.enabled = YES;
  [userImage_ addTarget:self
                 action:@selector(userImageTapped:)
       forControlEvents:UIControlEventTouchUpInside];
  [self addSubview:userImage_];
  [userImage_ release];
  CGFloat minHeight = CGRectGetMaxY(userImage_.frame) + 8;

  UILabel* nameLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  nameLabel.textColor = [UIColor stampedGrayColor];
  nameLabel.text = comment_.user.screenName;
  nameLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  CGSize stringSize = [nameLabel sizeThatFits:CGSizeMake(260, MAXFLOAT)];
  const CGFloat leftPadding = CGRectGetMaxX(userImage_.frame) + 8;
  nameLabel.frame = CGRectMake(leftPadding, 8, stringSize.width, stringSize.height);
  [self addSubview:nameLabel];
  [nameLabel release];
  
  UILabel* commentLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  commentLabel.lineBreakMode = UILineBreakModeWordWrap;
  commentLabel.font = [UIFont fontWithName:@"Helvetica" size:12];
  commentLabel.text = comment_.blurb;
  commentLabel.textColor = [UIColor stampedBlackColor];
  commentLabel.numberOfLines = 0;
  stringSize = [commentLabel sizeThatFits:CGSizeMake(220, MAXFLOAT)];
  commentLabel.frame = CGRectMake(leftPadding, 23, stringSize.width, stringSize.height);
  [self addSubview:commentLabel];
  [commentLabel release];
  
  UILabel* timestampLabel = [[UILabel alloc] initWithFrame:CGRectZero];
  timestampLabel.font = [UIFont fontWithName:@"Helvetica-Bold" size:10];
  timestampLabel.textColor = [UIColor stampedLightGrayColor];
  timestampLabel.textAlignment = UITextAlignmentRight;
  timestampLabel.text = [Util shortUserReadableTimeSinceDate:comment_.created];
  [timestampLabel sizeToFit];
  timestampLabel.frame = CGRectMake(310 - CGRectGetWidth(timestampLabel.frame) - 10,
                                    10,
                                    CGRectGetWidth(timestampLabel.frame),
                                    CGRectGetHeight(timestampLabel.frame));
  [self addSubview:timestampLabel];
  [timestampLabel release];
  
  CGRect frame = self.frame;
  frame.size.height = fmaxf(minHeight, CGRectGetMaxY(commentLabel.frame) + 8);
  self.frame = frame;
}

- (void)drawRect:(CGRect)rect {
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSaveGState(ctx);
  CGContextSetFillColorWithColor(ctx, [UIColor colorWithWhite:0.9 alpha:1.0].CGColor);
  CGContextFillRect(ctx, CGRectMake(0, 0, CGRectGetWidth(self.bounds), 1));
  CGContextRestoreGState(ctx);
}

- (void)userImageTapped:(id)sender {
  [[NSNotificationCenter defaultCenter] postNotificationName:kCommentUserImageTappedNotification object:self];
}

@end
