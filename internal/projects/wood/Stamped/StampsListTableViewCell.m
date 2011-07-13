//
//  StampsListTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampsListTableViewCell.h"

#import <QuartzCore/QuartzCore.h>

#import "StampEntity.h"
#import "UserImageView.h"

static NSString* kTitleFontString = @"TGLight";
static const CGFloat kTitleFontSize = 47.0;
static NSString* kUserNameFontString = @"Helvetica-Bold";
static NSString* kCommentFontString = @"HelveticaNeue";
static const CGFloat kSubstringFontSize = 12.0;
static const CGFloat kUserImageHorizontalMargin = 14.0;
static const CGFloat kUserImageSize = 37.0;
static const CGFloat kCellTopPadding = 8.0;
static const CGFloat kTypeIconSize = 12.0;
static const CGFloat kTitleMaxWidth = 225;
static const CGFloat kSubstringMaxWidth = 218.0;

@interface StampCellView : UIView {
 @private
  // Managed by the top-level view system.
  UserImageView* userImageView_;
  UIImageView* typeImageView_;
  UILabel* userNameLabel_;
  UILabel* commentLabel_;

  // NOT managed. Must manage ownership.
  UILabel* titleLabel_;
  CGRect stampImageFrame_;
  CGFloat userImageRightMargin_;
}

// This is magic with UITableViewCell. No need to set this explicitly.
@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, retain) UIImage* stampImage;
@property (nonatomic, copy) NSString* title;
@property (nonatomic, retain) UIImage* userImage;
@property (nonatomic, retain) UIImage* typeImage;
@property (nonatomic, copy) NSString* userName;
@property (nonatomic, copy) NSString* comment;

@end

@implementation StampCellView

@synthesize stampImage = stampImage_;
@synthesize title = title_;
@synthesize userImage = userImage_;
@synthesize typeImage = typeImage_;
@synthesize userName = userName_;
@synthesize comment = comment_;
@synthesize highlighted = highlighted_;

- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.opaque = YES;
		self.backgroundColor = [UIColor whiteColor];
    self.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;

    userImageRightMargin_ = kUserImageSize + (kUserImageHorizontalMargin * 2.0);
    CGRect userImgFrame = CGRectMake(kUserImageHorizontalMargin, kCellTopPadding, kUserImageSize, kUserImageSize);
    userImageView_ = [[UserImageView alloc] initWithFrame:userImgFrame];
    [self addSubview:userImageView_];
    [userImageView_ release];
    
    typeImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(userImageRightMargin_, 59, kTypeIconSize, kTypeIconSize)];
    typeImageView_.contentMode = UIViewContentModeScaleAspectFit;
    [self addSubview:typeImageView_];
    [typeImageView_ release];
    
    UIColor* substringTextColor = [UIColor colorWithWhite:0.6 alpha:1.0];
    userNameLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    userNameLabel_.font = [UIFont fontWithName:kUserNameFontString size:kSubstringFontSize];
    userNameLabel_.textColor = substringTextColor;
    [self addSubview:userNameLabel_];
    [userNameLabel_ release];
    
    commentLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    commentLabel_.font = [UIFont fontWithName:kCommentFontString size:kSubstringFontSize];
    commentLabel_.textColor = substringTextColor;
    [self addSubview:commentLabel_];
    [commentLabel_ release];

    // Drawn within |drawRect:|. Don't add it as a subview.
    titleLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    titleLabel_.font = [UIFont fontWithName:kTitleFontString size:kTitleFontSize];
    titleLabel_.textColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  }
  return self;
}

- (void)dealloc {
  self.userImage = nil;
  self.stampImage = nil;
  self.typeImage = nil;
  [titleLabel_ release];

  [super dealloc];
}

- (void)drawRect:(CGRect)rect {
  [super drawRect:rect];
  
  if (highlighted_) {
    userNameLabel_.textColor = [UIColor whiteColor];
    commentLabel_.textColor = [UIColor whiteColor];
    titleLabel_.textColor = [UIColor whiteColor];
  } else {
    UIColor* substringTextColor = [UIColor colorWithWhite:0.6 alpha:1.0];
    userNameLabel_.textColor = substringTextColor;
    commentLabel_.textColor = substringTextColor;
    titleLabel_.textColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  }
  [titleLabel_ drawTextInRect:titleLabel_.frame];
  [stampImage_ drawInRect:stampImageFrame_ blendMode:kCGBlendModeMultiply alpha:1.0];
}

- (void)setUserImage:(UIImage*)userImage {
  if (userImage != userImage_) {
    [userImage_ release];
    userImage_ = [userImage retain];
    userImageView_.image = userImage_;
  }
}

- (void)setStampImage:(UIImage*)stampImage {
  if (stampImage != stampImage_) {
    [stampImage_ release];
    stampImage_ = [stampImage retain];
    [self setNeedsDisplay];
  }
}

- (void)setTypeImage:(UIImage*)typeImage {
  if (typeImage != typeImage_) {
    [typeImage_ release];
    typeImage_ = [typeImage retain];
    typeImageView_.image = typeImage_;
  }
}

- (void)setTitle:(NSString*)title {
  title_ = title;
  CGSize stringSize = [title_ sizeWithFont:[UIFont fontWithName:kTitleFontString size:kTitleFontSize]
                                  forWidth:kTitleMaxWidth
                             lineBreakMode:UILineBreakModeTailTruncation];
  stampImageFrame_ = CGRectMake(userImageRightMargin_ + stringSize.width - (23 / 2), 7, 23, 23);
  titleLabel_.frame = CGRectMake(userImageRightMargin_, kCellTopPadding, stringSize.width, stringSize.height);
  titleLabel_.text = title;
  [self setNeedsDisplay];
}

- (void)setUserName:(NSString*)userName {
  userName_ = userName;
  CGSize stringSize = [userName_ sizeWithFont:[UIFont fontWithName:kUserNameFontString size:kSubstringFontSize]
                                     forWidth:kSubstringMaxWidth
                                lineBreakMode:UILineBreakModeTailTruncation];
  userNameLabel_.frame = CGRectMake(userImageRightMargin_ + 16, 58, stringSize.width, stringSize.height);
  userNameLabel_.text = userName_;
}

- (void)setComment:(NSString*)comment {
  comment_ = comment;
  CGSize stringSize = [comment_ sizeWithFont:[UIFont fontWithName:kCommentFontString size:kSubstringFontSize]
                                    forWidth:kSubstringMaxWidth - CGRectGetWidth(userNameLabel_.frame) - 14
                               lineBreakMode:UILineBreakModeTailTruncation];
  commentLabel_.text = comment_;
  commentLabel_.frame = CGRectMake(CGRectGetMaxX(userNameLabel_.frame) + 3, 58, stringSize.width, stringSize.height);
}

@end


@implementation StampsListTableViewCell

@synthesize stampEntity = stampEntity_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
    CGRect customViewFrame = CGRectMake(0.0, 0.0, self.contentView.bounds.size.width, self.contentView.bounds.size.height);
		customView_ = [[StampCellView alloc] initWithFrame:customViewFrame];
		[self.contentView addSubview:customView_];
    [customView_ release];
  }
  return self;
}

- (void)dealloc {  
  self.stampEntity = nil;
  [super dealloc];
}

- (void)setStampEntity:(StampEntity*)stampEntity {
  if (stampEntity != stampEntity_) {
    [stampEntity_ release];
    stampEntity_ = [stampEntity retain];
    customView_.userImage = stampEntity.userImage;
    customView_.stampImage = stampEntity.stampImage;
    customView_.title = stampEntity.name;
    customView_.typeImage = stampEntity.categoryImage;
    customView_.userName = stampEntity.userName;
    
    if (stampEntity.comment)
      customView_.comment = stampEntity.comment;
  }
}

@end
