//
//  InboxTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "InboxTableViewCell.h"

#include <math.h>

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "Stamp.h"
#import "User.h"
#import "UserImageView.h"
#import "Util.h"

static NSString* kTitleFontString = @"TGLight";
static const CGFloat kTitleFontSize = 47.0;
static NSString* kUserNameFontString = @"Helvetica-Bold";
static NSString* kCommentFontString = @"Helvetica";
static const CGFloat kSubstringFontSize = 12.0;
static const CGFloat kUserImageHorizontalMargin = 14.0;
static const CGFloat kUserImageSize = 41.0;
static const CGFloat kCellTopPadding = 8.0;
static const CGFloat kTypeIconSize = 12.0;
static const CGFloat kSubstringMaxWidth = 218.0;
static const CGFloat kStampSize = 18.0;
static const CGFloat kTitleMaxWidth = 210.0;

@interface StampCellView : UIView {
 @private
  // Managed by the top-level view system.
  UserImageView* userImageView_;
  UIImageView* typeImageView_;
  UIImageView* disclosureImageView_;

  // NOT managed. Must manage ownership.
  CATextLayer* titleLayer_;
  UILabel* badgeLabel_;
  UILabel* userNameLabel_;
  UILabel* commentLabel_;
  UIColor* defaultTitleColor_;
  UIColor* defaultSubstringColor_;
  UIColor* whiteColor_;
  CTFontRef titleFont_;
  CTParagraphStyleRef titleStyle_;
  NSMutableDictionary* titleAttributes_;
  CGRect stampImageFrame_;
  CGFloat userImageRightMargin_;
}

// This is magic with UITableViewCell. No need to set this explicitly.
@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, assign) BOOL selected;
@property (nonatomic, assign) NSUInteger numComments;
@property (nonatomic, retain) UIImage* stampImage;
@property (nonatomic, copy) NSString* title;
@property (nonatomic, retain) UIImage* userImage;
@property (nonatomic, retain) UIImage* typeImage;
@property (nonatomic, retain) UIImage* disclosureArrowImage;
@property (nonatomic, copy) NSString* userName;
@property (nonatomic, copy) NSString* comment;

@end

@interface StampCellView ()
- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color;
- (void)invertColors:(BOOL)inverted;
- (void)setSelected:(BOOL)selected animated:(BOOL)animated;
@end

@implementation StampCellView

@synthesize highlighted = highlighted_;
@synthesize selected = selected_;
@synthesize numComments = numComments_;
@synthesize stampImage = stampImage_;
@synthesize disclosureArrowImage = disclosureArrowImage_;
@synthesize title = title_;
@synthesize userImage = userImage_;
@synthesize typeImage = typeImage_;
@synthesize userName = userName_;
@synthesize comment = comment_;


- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.opaque = YES;
		whiteColor_ = [[UIColor alloc] initWithWhite:1.0 alpha:1.0];

    self.backgroundColor = whiteColor_;
    self.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    
    defaultTitleColor_ = [[UIColor alloc] initWithWhite:0.37 alpha:1.0];
    defaultSubstringColor_ = [[UIColor alloc] initWithWhite:0.6 alpha:1.0];
    
    userImageRightMargin_ = kUserImageSize + (kUserImageHorizontalMargin * 2.0);
    CGRect userImgFrame = CGRectMake(kUserImageHorizontalMargin, kCellTopPadding, kUserImageSize, kUserImageSize);
    userImageView_ = [[UserImageView alloc] initWithFrame:userImgFrame];
    [self addSubview:userImageView_];
    [userImageView_ release];
    
    typeImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(userImageRightMargin_, 58, kTypeIconSize, kTypeIconSize)];
    typeImageView_.contentMode = UIViewContentModeScaleAspectFit;
    [self addSubview:typeImageView_];
    [typeImageView_ release];

    self.disclosureArrowImage = [UIImage imageNamed:@"disclosure_arrow"];
    disclosureImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(300, 34, 8, 11)];
    disclosureImageView_.contentMode = UIViewContentModeScaleAspectFit;
    disclosureImageView_.image = self.disclosureArrowImage;
    disclosureImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:self.disclosureArrowImage];
    [self addSubview:disclosureImageView_];
    [disclosureImageView_ release];
    
    userNameLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    userNameLabel_.lineBreakMode = UILineBreakModeTailTruncation;
    userNameLabel_.textColor = defaultSubstringColor_;
    userNameLabel_.font = [UIFont fontWithName:kUserNameFontString size:kSubstringFontSize];
    
    commentLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    commentLabel_.font = [UIFont fontWithName:kCommentFontString size:kSubstringFontSize];
    commentLabel_.textColor = defaultSubstringColor_;

    CGRect badgeFrame = CGRectMake(CGRectGetMaxX(self.bounds) - 10 - 17, 30, 17, 17);
    badgeLabel_ = [[UILabel alloc] initWithFrame:badgeFrame];
    badgeLabel_.font = [UIFont fontWithName:@"Helvetica-Bold" size:10];
    badgeLabel_.textAlignment = UITextAlignmentCenter;
    badgeLabel_.textColor = [UIColor whiteColor];
    
    titleLayer_ = [[CATextLayer alloc] init];
    titleLayer_.truncationMode = kCATruncationEnd;
    titleLayer_.contentsScale = [[UIScreen mainScreen] scale];
    titleLayer_.foregroundColor = defaultTitleColor_.CGColor;
    titleLayer_.fontSize = 24.0;
    titleLayer_.frame = CGRectMake(userImageRightMargin_, kCellTopPadding + 2.0, kTitleMaxWidth, kTitleFontSize);
    titleFont_ = CTFontCreateWithName((CFStringRef)kTitleFontString, kTitleFontSize, NULL);
    CFIndex numSettings = 1;
    CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
    CTParagraphStyleSetting settings[1] = {
      {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
    };
    titleStyle_ = CTParagraphStyleCreate(settings, numSettings);
    titleAttributes_ = [[NSMutableDictionary alloc] initWithObjectsAndKeys:
        (id)titleFont_, (id)kCTFontAttributeName,
        (id)defaultTitleColor_.CGColor, (id)kCTForegroundColorAttributeName,
        (id)titleStyle_, (id)kCTParagraphStyleAttributeName,
        (id)[NSNumber numberWithDouble:1.2], (id)kCTKernAttributeName, nil];
  }
  return self;
}

- (void)dealloc {
  self.userImage = nil;
  self.stampImage = nil;
  self.typeImage = nil;
  [defaultTitleColor_ release];
  [defaultSubstringColor_ release];
  [whiteColor_ release];
  [titleAttributes_ release];
  [titleLayer_ release];
  [badgeLabel_ release];
  [userNameLabel_ release];
  [commentLabel_ release];
  CFRelease(titleFont_);
  CFRelease(titleStyle_);
  [super dealloc];
}

- (void)invertColors:(BOOL)inverted {
  UIColor* titleColor = defaultTitleColor_;
  UIColor* substringColor = defaultSubstringColor_;
  UIColor* badgeTextColor = whiteColor_;
  if (inverted) {
    substringColor = whiteColor_;
    titleColor = whiteColor_;
    badgeTextColor = [UIColor blueColor];
  }

  userNameLabel_.textColor = substringColor;
  commentLabel_.textColor = substringColor;
  badgeLabel_.textColor = badgeTextColor;

  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  titleLayer_.string = [self titleAttributedStringWithColor:titleColor];
  titleLayer_.foregroundColor = titleColor.CGColor;
  [CATransaction commit];
  [self setNeedsDisplay];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  selected_ = selected;
  [self invertColors:selected];
}

- (void)setHighlighted:(BOOL)highlighted {
  highlighted_ = highlighted;
  [self invertColors:highlighted];
}

- (void)drawRect:(CGRect)rect {
  [super drawRect:rect];
  CGContextRef ctx = UIGraphicsGetCurrentContext();
  CGContextSaveGState(ctx);
  CGContextTranslateCTM(ctx, titleLayer_.frame.origin.x, titleLayer_.frame.origin.y);
  [titleLayer_ drawInContext:ctx];
  CGContextRestoreGState(ctx);
  if (!badgeLabel_.hidden) {
    UIBezierPath* badgePath = [UIBezierPath bezierPathWithRoundedRect:badgeLabel_.frame cornerRadius:2.0];
    UIColor* fillColor = highlighted_ ? [UIColor whiteColor] : [UIColor lightGrayColor]; 
    [fillColor setFill];
    [badgePath fill];
    [badgeLabel_ drawTextInRect:badgeLabel_.frame];
  }
  [userNameLabel_ drawTextInRect:userNameLabel_.frame];
  [commentLabel_ drawTextInRect:commentLabel_.frame];
  [stampImage_ drawInRect:stampImageFrame_ blendMode:kCGBlendModeMultiply alpha:1.0];
}

- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color {
  [titleAttributes_ setObject:(id)color.CGColor forKey:(id)kCTForegroundColorAttributeName];
  NSAttributedString* titleAttributedString = [[NSAttributedString alloc] initWithString:title_
                                                                              attributes:titleAttributes_];
  return [titleAttributedString autorelease];
}

- (void)setUserImage:(UIImage*)userImage {
  if (userImage != userImage_) {
    [userImage_ release];
    userImage_ = [userImage retain];
    if (userImage)
      userImageView_.image = userImage;
  }
}

- (void)setStampImage:(UIImage*)stampImage {
  if (stampImage != stampImage_) {
    [stampImage_ release];
    stampImage_ = [stampImage retain];
    if (stampImage)
      [self setNeedsDisplay];
  }
}

- (void)setTypeImage:(UIImage*)typeImage {
  if (typeImage != typeImage_) {
    [typeImage_ release];
    typeImage_ = [typeImage retain];
    if (typeImage) {
      typeImageView_.image = typeImage;
      typeImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:typeImage];
    }
  }
}

- (void)setTitle:(NSString*)title {
  title_ = title;
  NSAttributedString* attrString = [self titleAttributedStringWithColor:defaultTitleColor_];
  titleLayer_.string = attrString;
  CTLineRef line = CTLineCreateWithAttributedString((CFAttributedStringRef)attrString);
  CGFloat ascent, descent, leading, width;
  width = fmin(kTitleMaxWidth, CTLineGetTypographicBounds(line, &ascent, &descent, &leading));
  CFRelease(line);
  CGRect oldFrame = stampImageFrame_;
  stampImageFrame_ = CGRectMake(userImageRightMargin_ + width - (kStampSize / 2.0),
                                kStampSize / 2.0,
                                kStampSize,
                                kStampSize);
  [self setNeedsDisplayInRect:oldFrame];
  [self setNeedsDisplayInRect:stampImageFrame_];
  [self setNeedsDisplayInRect:titleLayer_.frame];
}

- (void)setUserName:(NSString*)userName {
  userName_ = userName;
  CGSize stringSize = [userName_ sizeWithFont:[UIFont fontWithName:kUserNameFontString size:kSubstringFontSize]
                                     forWidth:kSubstringMaxWidth
                                lineBreakMode:UILineBreakModeTailTruncation];
  userNameLabel_.frame = CGRectMake(userImageRightMargin_ + 16, 57, stringSize.width, stringSize.height);
  userNameLabel_.text = userName_;
  [self setNeedsDisplayInRect:userNameLabel_.frame];
}

- (void)setComment:(NSString*)comment {
  if ([comment length] > 0)
    comment = [NSString stringWithFormat:@"\"%@\"", comment];

  comment_ = comment;
  CGSize stringSize = [comment_ sizeWithFont:[UIFont fontWithName:kCommentFontString size:kSubstringFontSize]
                                    forWidth:kSubstringMaxWidth - CGRectGetWidth(userNameLabel_.frame) - 14
                               lineBreakMode:UILineBreakModeTailTruncation];
  commentLabel_.text = comment_;
  commentLabel_.frame = CGRectMake(CGRectGetMaxX(userNameLabel_.frame) + 3, 57, stringSize.width, stringSize.height);
}

- (void)setNumComments:(NSUInteger)numComments {
  numComments_ = numComments;
  badgeLabel_.hidden = (numComments_ == 0);
  disclosureImageView_.hidden = !badgeLabel_.hidden;
  badgeLabel_.text = [NSString stringWithFormat:@"%u", numComments];
  [self setNeedsDisplayInRect:badgeLabel_.frame];
}

@end

@interface InboxTableViewCell ()
- (void)stampChanged:(NSNotification*)notification;
@end

@implementation InboxTableViewCell

@synthesize stamp = stamp_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGRect customViewFrame = CGRectMake(0.0, 0.0, self.contentView.bounds.size.width, self.contentView.bounds.size.height);
		customView_ = [[StampCellView alloc] initWithFrame:customViewFrame];
		[self.contentView addSubview:customView_];
    [customView_ release];
  }
  return self;
}

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.stamp = nil;
  [super dealloc];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [customView_ setSelected:selected animated:animated];
}

- (void)setStamp:(Stamp*)stamp {
  if (stamp != stamp_) {
    [stamp_ release];
    stamp_ = [stamp retain];
    if (stamp) {
      customView_.userImage = stamp.user.profileImage;
      customView_.stampImage = stamp.user.stampImage;
      customView_.title = stamp.entityObject.title;
      customView_.typeImage = stamp.entityObject.categoryImage;
      customView_.userName = stamp.user.displayName;
      customView_.comment = stamp.blurb;
      customView_.numComments = [stamp.numComments unsignedIntegerValue];
      [[NSNotificationCenter defaultCenter] removeObserver:self];
      [[NSNotificationCenter defaultCenter] addObserver:self
                                               selector:@selector(stampChanged:)
                                                   name:kStampDidChangeNotification
                                                 object:stamp_];
    }
  }
}

- (void)stampChanged:(NSNotification*)notification {
  // Comments may have changed...
  customView_.numComments = [stamp_.numComments unsignedIntegerValue];
}

@end
