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
#import "STBadgeView.h"
#import "Stamp.h"
#import "User.h"
#import "UserImageView.h"

static NSString* kTitleFontString = @"TGLight";
static const CGFloat kTitleFontSize = 47.0;
static NSString* kUserNameFontString = @"Helvetica-Bold";
static NSString* kCommentFontString = @"HelveticaNeue";
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
  UILabel* userNameLabel_;
  UILabel* commentLabel_;
  STBadgeView* badgeView_;

  // NOT managed. Must manage ownership.
  CATextLayer* titleLayer_;
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
@property (nonatomic, copy) NSString* userName;
@property (nonatomic, copy) NSString* comment;

@end

@interface StampCellView ()
- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color;
- (UIImage*)whiteMaskedImageUsingImage:(UIImage*)img;
- (void)invertColors:(BOOL)inverted;
- (void)setSelected:(BOOL)selected animated:(BOOL)animated;
@end

@implementation StampCellView

@synthesize highlighted = highlighted_;
@synthesize selected = selected_;
@synthesize numComments = numComments_;
@synthesize stampImage = stampImage_;
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

    userNameLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    userNameLabel_.lineBreakMode = UILineBreakModeTailTruncation;
    userNameLabel_.textColor = defaultSubstringColor_;
    userNameLabel_.font = [UIFont fontWithName:kUserNameFontString size:kSubstringFontSize];
    [self addSubview:userNameLabel_];
    [userNameLabel_ release];
    
    commentLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    commentLabel_.font = [UIFont fontWithName:kCommentFontString size:kSubstringFontSize];
    commentLabel_.textColor = defaultSubstringColor_;
    [self addSubview:commentLabel_];
    [commentLabel_ release];

    badgeView_ = [[STBadgeView alloc] initWithFrame:CGRectMake(CGRectGetMaxX(self.bounds) - 10 - 17, 30, 17, 17)];
    [self addSubview:badgeView_];
    badgeView_.hidden = YES;
    [badgeView_ release];
    
    titleLayer_ = [[CATextLayer alloc] init];
    titleLayer_.truncationMode = kCATruncationEnd;
    titleLayer_.contentsScale = [[UIScreen mainScreen] scale];
    titleLayer_.foregroundColor = defaultTitleColor_.CGColor;
    titleLayer_.fontSize = 24.0;
    titleLayer_.frame = CGRectMake(userImageRightMargin_, kCellTopPadding + 2.0, kTitleMaxWidth, kTitleFontSize);
    // Disable implicit animations for this layer.
    NSMutableDictionary* actions = [[NSMutableDictionary alloc] initWithObjectsAndKeys:
        [NSNull null], @"onOrderIn",
        [NSNull null], @"onOrderOut",
        [NSNull null], @"sublayers",
        [NSNull null], @"contents",
        [NSNull null], @"bounds",
        nil];
    titleLayer_.actions = actions;
    [actions release];
    
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
  CFRelease(titleFont_);
  CFRelease(titleStyle_);
  [super dealloc];
}

- (void)invertColors:(BOOL)inverted {
  UIColor* titleColor = defaultTitleColor_;
  UIColor* substringColor = defaultSubstringColor_;
  
  if (inverted) {
    substringColor = whiteColor_;
    titleColor = whiteColor_;
    typeImageView_.image = [self whiteMaskedImageUsingImage:typeImage_];
  } else {
    typeImageView_.image = typeImage_;
  }
  
  userNameLabel_.textColor = substringColor;
  commentLabel_.textColor = substringColor;

  [CATransaction begin];
  [CATransaction setValue:(id)kCFBooleanTrue forKey:kCATransactionDisableActions];
  titleLayer_.string = [self titleAttributedStringWithColor:titleColor];
  titleLayer_.foregroundColor = titleColor.CGColor;
  [CATransaction commit];
  [self setNeedsDisplayInRect:titleLayer_.frame];
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
  [stampImage_ drawInRect:stampImageFrame_ blendMode:kCGBlendModeMultiply alpha:1.0];
}

- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color {
  [titleAttributes_ setObject:(id)color.CGColor forKey:(id)kCTForegroundColorAttributeName];
  NSAttributedString* titleAttributedString = [[NSAttributedString alloc] initWithString:title_
                                                                              attributes:titleAttributes_];
  return [titleAttributedString autorelease];
}

- (UIImage*)whiteMaskedImageUsingImage:(UIImage*)img {
  CGFloat width = img.size.width;
  CGFloat height = img.size.height;

  UIGraphicsBeginImageContextWithOptions(img.size, NO, 0.0);
  CGContextRef context = UIGraphicsGetCurrentContext();

  CGContextTranslateCTM(context, 0, height);
  CGContextScaleCTM(context, 1.0, -1.0);
  
  CGContextClipToMask(context, CGRectMake(0, 0, width, height), img.CGImage);
  CGContextSetFillColorWithColor(context, whiteColor_.CGColor);
  CGContextFillRect(context, CGRectMake(0, 0, img.size.width, img.size.height));
  UIImage* maskedImage = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  return maskedImage;
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
}

- (void)setComment:(NSString*)comment {
  comment_ = comment;
  CGSize stringSize = [comment_ sizeWithFont:[UIFont fontWithName:kCommentFontString size:kSubstringFontSize]
                                    forWidth:kSubstringMaxWidth - CGRectGetWidth(userNameLabel_.frame) - 14
                               lineBreakMode:UILineBreakModeTailTruncation];
  commentLabel_.text = comment_;
  commentLabel_.frame = CGRectMake(CGRectGetMaxX(userNameLabel_.frame) + 3, 57, stringSize.width, stringSize.height);
}

- (void)setNumComments:(NSUInteger)numComments {
  numComments_ = numComments;
  badgeView_.hidden = (numComments == 0);
  badgeView_.text = [NSString stringWithFormat:@"%u", numComments];
}

@end


@implementation InboxTableViewCell

@synthesize stamp = stamp_;

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
    customView_.userImage = stamp.user.profileImage;
    customView_.stampImage = stamp.user.stampImage;
    customView_.title = stamp.entityObject.title;
    customView_.typeImage = stamp.categoryImage;
    customView_.userName = stamp.user.displayName;
    customView_.comment = stamp.blurb;
    customView_.numComments = [stamp.numComments unsignedIntegerValue];
    //self.accessoryType = ([stamp.numComments unsignedIntValue] > 0) ?
    //    UITableViewCellAccessoryNone : UITableViewCellAccessoryDisclosureIndicator;
    //[self.accessoryView setNeedsDisplay];
  }
}

@end
