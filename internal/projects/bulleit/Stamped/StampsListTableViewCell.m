//
//  StampsListTableViewCell.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "StampsListTableViewCell.h"

#include <math.h>

#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>

#import "StampEntity.h"
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
  CATextLayer* titleLayer_;

  // NOT managed. Must manage ownership.
  CGRect stampImageFrame_;
  CGFloat userImageRightMargin_;
}

// This is magic with UITableViewCell. No need to set this explicitly.
@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, assign) BOOL selected;
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
		self.backgroundColor = [UIColor whiteColor];
    self.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;

    userImageRightMargin_ = kUserImageSize + (kUserImageHorizontalMargin * 2.0);
    CGRect userImgFrame = CGRectMake(kUserImageHorizontalMargin, kCellTopPadding, kUserImageSize, kUserImageSize);
    userImageView_ = [[UserImageView alloc] initWithFrame:userImgFrame];
    [self addSubview:userImageView_];
    [userImageView_ release];
    
    typeImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(userImageRightMargin_, 58, kTypeIconSize, kTypeIconSize)];
    typeImageView_.contentMode = UIViewContentModeScaleAspectFit;
    [self addSubview:typeImageView_];
    [typeImageView_ release];

    UIColor* substringTextColor = [UIColor colorWithWhite:0.6 alpha:1.0];
    userNameLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    userNameLabel_.lineBreakMode = UILineBreakModeTailTruncation;
    userNameLabel_.textColor = substringTextColor;
    userNameLabel_.font = [UIFont fontWithName:kUserNameFontString size:kSubstringFontSize];
    [self addSubview:userNameLabel_];
    [userNameLabel_ release];
    
    commentLabel_ = [[UILabel alloc] initWithFrame:CGRectZero];
    commentLabel_.font = [UIFont fontWithName:kCommentFontString size:kSubstringFontSize];
    commentLabel_.textColor = substringTextColor;
    [self addSubview:commentLabel_];
    [commentLabel_ release];

    titleLayer_ = [[CATextLayer alloc] init];
    titleLayer_.truncationMode = kCATruncationEnd;
    titleLayer_.contentsScale = [[UIScreen mainScreen] scale];
    titleLayer_.foregroundColor = [UIColor colorWithWhite:0.37 alpha:1.0].CGColor;
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
    [self.layer addSublayer:titleLayer_];
    [titleLayer_ release];
  }
  return self;
}

- (void)dealloc {
  self.userImage = nil;
  self.stampImage = nil;
  self.typeImage = nil;
  [super dealloc];
}

- (void)invertColors:(BOOL)inverted {
  UIColor* titleColor = [UIColor colorWithWhite:0.37 alpha:1.0];
  UIColor* substringColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  
  if (inverted) {
    substringColor = [UIColor whiteColor];
    titleColor = [UIColor whiteColor];
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
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  selected_ = selected;
  [self invertColors:selected];
}

- (void)drawRect:(CGRect)rect {
  [self invertColors:(highlighted_ || selected_)];

  [stampImage_ drawInRect:stampImageFrame_ blendMode:kCGBlendModeMultiply alpha:1.0];
  [super drawRect:rect];
}

- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color {
  CTFontRef titleFont = CTFontCreateWithName((CFStringRef)kTitleFontString, kTitleFontSize, NULL);
  CFIndex numSettings = 1;
  CTLineBreakMode lineBreakMode = kCTLineBreakByTruncatingTail;
  CTParagraphStyleSetting settings[1] = {
    {kCTParagraphStyleSpecifierLineBreakMode, sizeof(lineBreakMode), &lineBreakMode}
  };
  CTParagraphStyleRef titleStyle = CTParagraphStyleCreate(settings, numSettings);
  NSDictionary* titleAttributes = [NSDictionary dictionaryWithObjectsAndKeys:
                                   (id)titleFont, (id)kCTFontAttributeName,
                                   (id)color.CGColor, (id)kCTForegroundColorAttributeName,
                                   (id)titleStyle, (id)kCTParagraphStyleAttributeName,
                                   (id)[NSNumber numberWithDouble:1.2], (id)kCTKernAttributeName,
                                   nil];
  NSAttributedString* titleAttributedString =
      [[NSAttributedString alloc] initWithString:title_ attributes:titleAttributes];
  CFRelease(titleFont);
  CFRelease(titleStyle);
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
  CGContextSetFillColorWithColor(context, [UIColor whiteColor].CGColor);
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
  NSAttributedString* attrString = [self titleAttributedStringWithColor:[UIColor colorWithWhite:0.37 alpha:1.0]];
  titleLayer_.string = attrString;
  CTLineRef line = CTLineCreateWithAttributedString((CFAttributedStringRef)attrString);
  CGFloat ascent, descent, leading, width;
  width = fmin(kTitleMaxWidth, CTLineGetTypographicBounds(line, &ascent, &descent, &leading));
  CGRect oldFrame = stampImageFrame_;
  stampImageFrame_ = CGRectMake(userImageRightMargin_ + width - (kStampSize / 2.0),
                                kStampSize / 2.0,
                                kStampSize,
                                kStampSize);
  [self setNeedsDisplayInRect:oldFrame];
  [self setNeedsDisplayInRect:stampImageFrame_];
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

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
  //[customView_ setHighlighted:highlighted animated:animated];
  [super setHighlighted:highlighted animated:animated];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [customView_ setSelected:selected animated:animated];
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
