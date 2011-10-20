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
- (void)handleSwipeRight:(UISwipeGestureRecognizer*)recognizer;

@property (nonatomic, readonly) UILabel* nameLabel;
@property (nonatomic, readonly) UILabel* commentLabel;
@property (nonatomic, readonly) UIButton* deleteButton;

@end

@implementation StampDetailCommentView

@synthesize comment = comment_;
@synthesize userImage = userImage_;
@synthesize nameLabel = nameLabel_;
@synthesize commentLabel = commentLabel_;
@synthesize deleteButton = deleteButton_;
@synthesize editing = editing_;

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

  nameLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
  nameLabel_.textColor = [UIColor stampedGrayColor];
  nameLabel_.text = comment_.user.screenName;
  nameLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:12];
  CGSize stringSize = [nameLabel_ sizeThatFits:CGSizeMake(260, MAXFLOAT)];
  const CGFloat leftPadding = CGRectGetMaxX(userImage_.frame) + 8;
  nameLabel_.frame = CGRectMake(leftPadding, 8, stringSize.width, stringSize.height);
  [self addSubview:nameLabel_];
  [nameLabel_ release];

  commentLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
  commentLabel_.lineBreakMode = UILineBreakModeWordWrap;
  commentLabel_.font = [UIFont fontWithName:@"Helvetica" size:12];
  commentLabel_.text = comment_.blurb;
  commentLabel_.textColor = [UIColor stampedBlackColor];
  commentLabel_.numberOfLines = 0;
  stringSize = [commentLabel_ sizeThatFits:CGSizeMake(215, MAXFLOAT)];
  commentLabel_.frame = CGRectMake(leftPadding, 23, stringSize.width, stringSize.height);
  [self addSubview:commentLabel_];
  [commentLabel_ release];
  
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
  frame.size.height = fmaxf(minHeight, CGRectGetMaxY(commentLabel_.frame) + 8);
  self.frame = frame;
  
  deleteButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
  [deleteButton_ setImage:[UIImage imageNamed:@"delete_comment_icon"] forState:UIControlStateNormal];
  deleteButton_.frame = CGRectMake(7, self.center.y - (31 / 2), 31, 31);
  deleteButton_.alpha = 0;
  [self addSubview:deleteButton_];

  UISwipeGestureRecognizer* recognizer =
      [[UISwipeGestureRecognizer alloc] initWithTarget:self
                                                action:@selector(handleSwipeRight:)];
  [self addGestureRecognizer:recognizer];
  [recognizer release];
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

- (void)setEditing:(BOOL)editing {
  if (editing_ == editing)
    return;

  editing_ = editing;
  
  CGFloat offset = 35;
  if (!editing)
    offset *= -1;
  
  [UIView animateWithDuration:0.2 animations:^{
    deleteButton_.alpha = editing ? 1 : 0;
    userImage_.frame = CGRectOffset(userImage_.frame, offset, 0);
    nameLabel_.frame = CGRectOffset(nameLabel_.frame, offset, 0);
    commentLabel_.frame = CGRectOffset(commentLabel_.frame, offset, 0);
  }];
}

- (void)handleSwipeRight:(UISwipeGestureRecognizer*)recognizer {
  if (recognizer.state != UIGestureRecognizerStateEnded)
    return;

  self.editing = !editing_;
}

@end
