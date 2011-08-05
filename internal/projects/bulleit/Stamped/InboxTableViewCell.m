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
#import "Util.h"
#import "StampDetailViewController.h"
#import "StampedAppDelegate.h"

NSString* kInboxTableDidScrollNotification = @"InboxTableDidScrollNotification";

static NSString* kTitleFontString = @"TGLight";
static const CGFloat kTitleFontSize = 47.0;
static NSString* kUserNameFontString = @"Helvetica-Bold";
static NSString* kCommentFontString = @"Helvetica";
static const CGFloat kSubstringFontSize = 12.0;
static const CGFloat kUserImageHorizontalMargin = 14.0;
static const CGFloat kUserImageSize = 39.0;
static const CGFloat kCellTopPadding = 10.0;
static const CGFloat kTypeIconSize = 12.0;
static const CGFloat kSubstringMaxWidth = 218.0;
static const CGFloat kStampSize = 18.0;
static const CGFloat kTitleMaxWidth = 210.0;
static const CGFloat kImageRotations[] = {0.09, -0.08, 0.08, -0.09};

@interface InboxCellView : UIView {
 @private
  // Managed by the top-level view system.
  UIImageView* typeImageView_;
  UIImageView* disclosureImageView_;

  // NOT managed. Must manage ownership.
  CATextLayer* titleLayer_;
  UILabel* badgeLabel_;
  UILabel* userNameLabel_;
  UILabel* commentLabel_;
  UIColor* defaultTitleColor_;
  UIColor* defaultSubstringColor_;
  CTFontRef titleFont_;
  CTParagraphStyleRef titleStyle_;
  NSMutableDictionary* titleAttributes_;
  CGRect stampImageFrame_;
  CGFloat userImageRightMargin_;
}

// This is magic with UITableViewCell. No need to set this explicitly.
@property (nonatomic, assign, getter=isHighlighted) BOOL highlighted;
@property (nonatomic, assign) BOOL selected;
@property (nonatomic, assign) BOOL hidePhotos;
@property (nonatomic, assign) NSUInteger numComments;
@property (nonatomic, retain) UIImage* stampImage;
@property (nonatomic, copy) NSString* title;
@property (nonatomic, retain) UIImage* typeImage;
@property (nonatomic, copy) NSArray* stamps;

@end

@interface InboxCellView ()
- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color;
- (void)invertColors:(BOOL)inverted;
- (void)setSelected:(BOOL)selected animated:(BOOL)animated;
- (void)stampChanged:(NSNotification*)notification;
@end

@implementation InboxCellView

@synthesize highlighted = highlighted_;
@synthesize selected = selected_;
@synthesize numComments = numComments_;
@synthesize stampImage = stampImage_;
@synthesize title = title_;
@synthesize typeImage = typeImage_;
@synthesize stamps = stamps_;
@synthesize hidePhotos = hidePhotos_;


- (id)initWithFrame:(CGRect)frame {
  self = [super initWithFrame:frame];
  if (self) {
    self.opaque = YES;
    self.backgroundColor = [UIColor whiteColor];
    self.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    
    defaultTitleColor_ = [[UIColor alloc] initWithWhite:0.37 alpha:1.0];
    defaultSubstringColor_ = [[UIColor alloc] initWithWhite:0.6 alpha:1.0];
    
    userImageRightMargin_ = kUserImageSize + (kUserImageHorizontalMargin * 2.0);
    
    typeImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(userImageRightMargin_, 58, kTypeIconSize, kTypeIconSize)];
    typeImageView_.contentMode = UIViewContentModeScaleAspectFit;
    [self addSubview:typeImageView_];
    [typeImageView_ release];

    disclosureImageView_ = [[UIImageView alloc] initWithFrame:CGRectMake(300, 34, 8, 11)];
    disclosureImageView_.contentMode = UIViewContentModeScaleAspectFit;
    UIImage* disclosureArrowImage = [UIImage imageNamed:@"disclosure_arrow"];
    disclosureImageView_.image = disclosureArrowImage;
    disclosureImageView_.highlightedImage = [Util whiteMaskedImageUsingImage:disclosureArrowImage];
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
    titleLayer_.frame = CGRectMake(userImageRightMargin_, kCellTopPadding, kTitleMaxWidth, kTitleFontSize);
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
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.stampImage = nil;
  self.typeImage = nil;
  self.stamps = nil;
  [defaultTitleColor_ release];
  [defaultSubstringColor_ release];
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
  UIColor* badgeTextColor = [UIColor whiteColor];
  if (inverted) {
    substringColor = [UIColor whiteColor];
    titleColor = [UIColor whiteColor];
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
  if (hidePhotos_)
    return;

  CGRect userImgFrame = CGRectMake(kUserImageHorizontalMargin, kCellTopPadding, kUserImageSize, kUserImageSize);
  Stamp* s = nil;
  NSUInteger stampsCount = [stamps_ count];
  for (NSUInteger i = MAX(0, (NSInteger)stampsCount - 3); i < stampsCount; ++i) {
    s = [stamps_ objectAtIndex:i];
    UIImage* img = s.user.profileImage;
    if (i == stampsCount - 1) {
      CGContextRef ctx = UIGraphicsGetCurrentContext();
      CGContextSaveGState(ctx);
      CGContextSetShadow(ctx, CGSizeMake(0, 0), 3.0);
      [[UIColor whiteColor] setFill];
      UIBezierPath* path = [UIBezierPath bezierPathWithRect:userImgFrame];
      [path fill];
      CGContextRestoreGState(ctx);
      [img drawInRect:CGRectInset(userImgFrame, 2, 2)];
      return;
    }
    CGFloat width = kUserImageSize;
    CGFloat height = kUserImageSize;
    CGSize rotatedSize = CGRectInset(userImgFrame, -5, -5).size;
    UIGraphicsBeginImageContextWithOptions(rotatedSize, NO, 0.0);
    CGContextRef imgContext = UIGraphicsGetCurrentContext();
    CGContextTranslateCTM(imgContext, rotatedSize.width * 0.5, rotatedSize.height * 0.5);
    CGContextRotateCTM(imgContext, kImageRotations[i % 4]);
    CGContextScaleCTM(imgContext, 1.0, -1.0);
    CGRect imgFrame = CGRectMake(-width / 2, -height / 2, width, height);
    CGContextSaveGState(imgContext);
    UIBezierPath* path = [UIBezierPath bezierPathWithRect:imgFrame];
    CGContextSetFillColorWithColor(imgContext, [UIColor whiteColor].CGColor);
    CGContextSetShadow(imgContext, CGSizeMake(0, 0), 3.0);
    CGContextAddPath(imgContext, path.CGPath);
    CGContextClosePath(imgContext);
    CGContextFillPath(imgContext);
    CGContextRestoreGState(imgContext);
    CGContextDrawImage(imgContext, CGRectInset(imgFrame, 2, 2), img.CGImage);
    
    UIImage* rotatedImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    [rotatedImage drawInRect:CGRectOffset(CGRectInset(userImgFrame, -5, -5), 0, 4 * ((stampsCount - 1) - i))];
  }
}

- (NSAttributedString*)titleAttributedStringWithColor:(UIColor*)color {
  [titleAttributes_ setObject:(id)color.CGColor forKey:(id)kCTForegroundColorAttributeName];
  NSAttributedString* titleAttributedString = [[NSAttributedString alloc] initWithString:title_
                                                                              attributes:titleAttributes_];
  return [titleAttributedString autorelease];
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
  if (title_ != title) {
    title_ = [title copy];
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
}

- (void)setNumComments:(NSUInteger)numComments {
  numComments_ = numComments;
  badgeLabel_.hidden = (numComments_ == 0);
  disclosureImageView_.hidden = !badgeLabel_.hidden;
  badgeLabel_.text = [NSString stringWithFormat:@"%u", numComments];
  [self setNeedsDisplayInRect:badgeLabel_.frame];
}

- (void)setStamps:(NSArray*)stamps {
  if (stamps_ != stamps) {
    stamps_ = [stamps copy];
    Stamp* stamp = [stamps objectAtIndex:0];
    self.stampImage = stamp.user.stampImage;
    NSString* userName = stamp.user.displayName;
    CGSize stringSize = [userName sizeWithFont:[UIFont fontWithName:kUserNameFontString size:kSubstringFontSize]
                                       forWidth:kSubstringMaxWidth
                                  lineBreakMode:UILineBreakModeTailTruncation];
    userNameLabel_.frame = CGRectMake(userImageRightMargin_ + 16, 57, stringSize.width, stringSize.height);
    userNameLabel_.text = userName;

    NSString* comment = stamp.blurb;
    if ([comment length] > 0)
      comment = [NSString stringWithFormat:@"\u201c%@\u201d", comment];

    stringSize = [comment sizeWithFont:[UIFont fontWithName:kCommentFontString size:kSubstringFontSize]
                              forWidth:kSubstringMaxWidth - CGRectGetWidth(userNameLabel_.frame) - 14
                         lineBreakMode:UILineBreakModeTailTruncation];
    commentLabel_.text = comment;
    commentLabel_.frame = CGRectMake(CGRectGetMaxX(userNameLabel_.frame) + 3, 57, stringSize.width, stringSize.height);

    self.numComments = [stamp.numComments unsignedIntegerValue];
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    for (Stamp* s in stamps) {
      [[NSNotificationCenter defaultCenter] addObserver:self
                                               selector:@selector(stampChanged:)
                                                   name:kStampDidChangeNotification
                                                 object:s];
    }
    [self setNeedsDisplay];
  }
}

- (void)stampChanged:(NSNotification*)notification {
  // Comments may have changed...
  Stamp* stamp = [notification object];
  self.numComments = [stamp.numComments unsignedIntegerValue];
}

@end

@interface InboxTableViewCell ()
- (void)expandStack;
- (void)collapseStack;
- (void)collapseButtonTapped:(id)sender;
- (void)inboxTableDidScroll:(NSNotification*)notification;
- (CGAffineTransform)transformForUserImageAtIndex:(NSUInteger)index;
- (void)userImageTapped:(id)sender;
@end

@implementation InboxTableViewCell

@synthesize entityObject = entityObject_;

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier {
  self = [super initWithStyle:UITableViewCellStyleDefault
              reuseIdentifier:reuseIdentifier];
  if (self) {
    self.accessoryType = UITableViewCellAccessoryNone;
    CGRect customViewFrame = CGRectMake(0, 0, self.contentView.bounds.size.width,
                                              self.contentView.bounds.size.height);
		customView_ = [[InboxCellView alloc] initWithFrame:customViewFrame];
		[self.contentView addSubview:customView_];
    [customView_ release];

    stacksBackgroundView_ = [[UIView alloc] initWithFrame:customViewFrame];
    stacksBackgroundView_.autoresizingMask = UIViewAutoresizingFlexibleWidth |
                                             UIViewAutoresizingFlexibleHeight;
    stacksBackgroundView_.backgroundColor = [UIColor colorWithWhite:0.93 alpha:1.0];
    stacksBackgroundView_.alpha = 0.0;
    [self.contentView addSubview:stacksBackgroundView_];
    [stacksBackgroundView_ release];
    
    stackCollapseButton_ = [UIButton buttonWithType:UIButtonTypeCustom];
    stackCollapseButton_.frame = CGRectMake(11, 7, 46, 46);
    [stackCollapseButton_ setImage:[UIImage imageNamed:@"stacks_back_button"]
                          forState:UIControlStateNormal];
    stackCollapseButton_.alpha = 0.0;
    [stackCollapseButton_ addTarget:self
                             action:@selector(collapseButtonTapped:)
                   forControlEvents:UIControlEventTouchUpInside];
    [self.contentView addSubview:stackCollapseButton_];
    userImageScrollView_ = [[UIScrollView alloc] initWithFrame:CGRectMake(60, 0, 249, 63)];
    userImageScrollView_.pagingEnabled = YES;
    userImageScrollView_.backgroundColor = [UIColor clearColor];
    userImageScrollView_.hidden = YES;
    [self.contentView addSubview:userImageScrollView_];
    [userImageScrollView_ release];
  }
  return self;
}

- (void)dealloc {
  [[NSNotificationCenter defaultCenter] removeObserver:self];
  self.entityObject = nil;
  [super dealloc];
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
  [super setSelected:selected animated:animated];
  [customView_ setSelected:selected animated:animated];
}

- (void)setEntityObject:(Entity*)entityObject {
  if (entityObject != entityObject_) {
    [entityObject_ release];
    entityObject_ = [entityObject retain];
    if (entityObject) {
      customView_.title = entityObject.title;
      customView_.typeImage = entityObject.categoryImage;
      NSSortDescriptor* desc = [NSSortDescriptor sortDescriptorWithKey:@"created" ascending:YES];
      customView_.stamps =
          [entityObject.stamps sortedArrayUsingDescriptors:[NSArray arrayWithObject:desc]];
      [[NSNotificationCenter defaultCenter] removeObserver:self];
      if (customView_.stamps.count > 1) {
        [[NSNotificationCenter defaultCenter] addObserver:self
                                                 selector:@selector(inboxTableDidScroll:)
                                                     name:kInboxTableDidScrollNotification
                                                   object:nil];
      }
    }
  }
}

- (void)inboxTableDidScroll:(NSNotification*)notification {
  [self collapseButtonTapped:nil];
}

#pragma mark - Touch Events.

- (void)touchesBegan:(NSSet*)touches withEvent:(UIEvent*)event {
  if (stackExpanded_)
    return;
  
  UITouch* touch = [touches anyObject];
  if (customView_.stamps.count > 1 &&
      CGRectContainsPoint(CGRectMake(0, 0, 63, 63), [touch locationInView:customView_])) {
    return;  // Eat the touch event.
  }
  [super touchesBegan:touches withEvent:event];
}

- (void)touchesCancelled:(NSSet*)touches withEvent:(UIEvent*)event {
  if (stackExpanded_)
    return;

  [super touchesCancelled:touches withEvent:event];
}

- (void)touchesEnded:(NSSet*)touches withEvent:(UIEvent*)event {
  UITouch* touch = [touches anyObject];
  if (stackExpanded_)
    return;
  
  if (customView_.stamps.count > 1 &&
      CGRectContainsPoint(CGRectMake(0, 0, 63, 63), [touch locationInView:customView_])) {
    [self expandStack];
    return;
  }
  [super touchesEnded:touches withEvent:event];
}

- (void)touchesMoved:(NSSet*)touches withEvent:(UIEvent*)event {
  if (stackExpanded_)
    return;

  [super touchesMoved:touches withEvent:event];
}

- (void)collapseButtonTapped:(id)sender {
  [self collapseStack];
}

- (CGAffineTransform)transformForUserImageAtIndex:(NSUInteger)index {
  NSUInteger stampsCount = entityObject_.stamps.count;
  CGAffineTransform transform = CGAffineTransformIdentity;
  if (index >= MAX((NSInteger)stampsCount - 3, 0) && index < stampsCount - 1) {
    transform = CGAffineTransformRotate(
        CGAffineTransformMakeTranslation(0, 4 * ((stampsCount - 1) - index)),
        kImageRotations[index % 4]);
  }
  return transform;
}

- (void)collapseStack {
  if (stackExpanded_ == NO)
    return;

  userImageScrollView_.contentOffset = CGPointZero;
  userImageScrollView_.hidden = YES;
  NSUInteger i = 0;
  for (UIView* view in userImageScrollView_.subviews) {
    if (![view isMemberOfClass:[UIButton class]] || view == stackCollapseButton_)
      continue;
    
    [self.contentView addSubview:view];
    view.transform = CGAffineTransformTranslate(view.transform, 60, 0);
    ++i;
  }
  [UIView animateWithDuration:0.25
                        delay:0
                      options:UIViewAnimationOptionAllowUserInteraction
                   animations:^{
    customView_.transform = CGAffineTransformIdentity;
    stacksBackgroundView_.alpha = 0;
    stackCollapseButton_.alpha = 0;
    NSUInteger i = 0;
    for (UIView* view in self.contentView.subviews) {
      if (![view isMemberOfClass:[UIButton class]] || view == stackCollapseButton_)
        continue;
      
      view.transform = [self transformForUserImageAtIndex:i];
      ++i;
    }
  } completion:^(BOOL finished) {
    customView_.hidePhotos = NO;
    self.selectionStyle = UITableViewCellSelectionStyleBlue;
    stackExpanded_ = NO;
    for (UIView* view in self.contentView.subviews) {
      if (![view isMemberOfClass:[UIButton class]] || view == stackCollapseButton_)
        continue;
      [view removeFromSuperview];
    }
    [customView_ setNeedsDisplay];
    [self.contentView setNeedsDisplay];
    [stackCollapseButton_ setNeedsDisplay];
  }];
}

- (void)expandStack {
  if (stackExpanded_)
    return;

  stackExpanded_ = YES;
  userImageScrollView_.hidden = NO;
  self.selectionStyle = UITableViewCellSelectionStyleNone;
  CGRect userImgFrame = CGRectMake(kUserImageHorizontalMargin,
                                   kCellTopPadding,
                                   kUserImageSize,
                                   kUserImageSize);
  NSUInteger stampsCount = [entityObject_.stamps count];
  Stamp* s = nil;
  for (NSUInteger i = 0; i < stampsCount; ++i) {
    s = [customView_.stamps objectAtIndex:i];
    UIButton* userImageButton = [UIButton buttonWithType:UIButtonTypeCustom];
    userImageButton.frame = CGRectInset(userImgFrame, -2, -2);

    userImageButton.contentMode = UIViewContentModeCenter;
    userImageButton.layer.shadowOffset = CGSizeZero;
    userImageButton.layer.shadowOpacity = 0.5;
    userImageButton.layer.shadowRadius = 1.0;
    userImageButton.layer.shadowPath = [UIBezierPath bezierPathWithRect:
        CGRectMake(2, 2, CGRectGetWidth(userImgFrame), CGRectGetHeight(userImgFrame))].CGPath;
    CGFloat width = kUserImageSize + 4;
    CGFloat height = kUserImageSize + 4;
    UIGraphicsBeginImageContextWithOptions(CGSizeMake(width, height), NO, 0.0);
    CGContextRef imgContext = UIGraphicsGetCurrentContext();
    CGContextTranslateCTM(imgContext, 0, height);
    CGContextScaleCTM(imgContext, 1.0, -1.0);
    CGRect imgFrame = CGRectMake(0, 0, width, height);
    CGContextSaveGState(imgContext);
    UIBezierPath* clearBorderPath = [UIBezierPath bezierPathWithRect:imgFrame];
    CGContextSetFillColorWithColor(imgContext, [UIColor clearColor].CGColor);
    CGContextAddPath(imgContext, clearBorderPath.CGPath);
    CGContextClosePath(imgContext);
    CGContextFillPath(imgContext);
    CGContextRestoreGState(imgContext);
    CGContextSaveGState(imgContext);
    UIBezierPath* path = [UIBezierPath bezierPathWithRect:CGRectInset(imgFrame, 2, 2)];
    CGContextSetFillColorWithColor(imgContext, [UIColor whiteColor].CGColor);
    CGContextAddPath(imgContext, path.CGPath);
    CGContextClosePath(imgContext);
    CGContextFillPath(imgContext);
    CGContextRestoreGState(imgContext);
    CGContextDrawImage(imgContext, CGRectInset(imgFrame, 4, 4), s.user.profileImage.CGImage);
    UIImage* userImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    [userImageButton setImage:userImage forState:UIControlStateNormal];
    [userImageButton addTarget:self
                        action:@selector(userImageTapped:)
              forControlEvents:UIControlEventTouchUpInside];
    userImageButton.transform = [self transformForUserImageAtIndex:i];
    userImageButton.tag = i;
    [self.contentView addSubview:userImageButton];
  }
  customView_.hidePhotos = YES;
  [UIView animateWithDuration:0.25 animations:^{
    CGAffineTransform rightTransform =
      CGAffineTransformMakeTranslation(CGRectGetWidth(self.contentView.frame), 0);
    customView_.transform = rightTransform;
    stacksBackgroundView_.alpha = 1.0;
    stackCollapseButton_.alpha = 1.0;
    
    NSUInteger i = 0;
    for (UIView* view in self.contentView.subviews) {
      if (![view isMemberOfClass:[UIButton class]] || view == stackCollapseButton_)
        continue;
      
      NSInteger xPos = 55 + (48 * ((stampsCount - 1) - i));
      view.transform = CGAffineTransformMakeTranslation(xPos, 0);
      if (stampsCount > 5 && (stampsCount - 1 - i) > 4)
        view.alpha = 0.0;

      ++i;
    }
  } completion:^(BOOL finished) {
    NSUInteger i = 0;
    for (UIView* view in self.contentView.subviews) {
      if (![view isMemberOfClass:[UIButton class]] || view == stackCollapseButton_)
        continue;

      [userImageScrollView_ addSubview:view];
      view.transform = CGAffineTransformTranslate(view.transform, -60, 0);
      if (stampsCount > 5 && (stampsCount - 1 - i) > 4)
        view.alpha = 1.0;

      ++i;
    }
    CGRect scrollBounds = userImageScrollView_.bounds;
    NSUInteger numPages = ceil(stampsCount / 5.0);
    userImageScrollView_.contentSize =
        CGSizeMake(numPages * CGRectGetWidth(scrollBounds), CGRectGetHeight(scrollBounds));
    [self.contentView setNeedsDisplay];
  }];
}

- (void)userImageTapped:(id)sender {
  UIButton* button = sender;
  Stamp* stamp = [customView_.stamps objectAtIndex:button.tag];

  StampDetailViewController* detailViewController =
      [[StampDetailViewController alloc] initWithStamp:stamp];

  StampedAppDelegate* delegate = (StampedAppDelegate*)[[UIApplication sharedApplication] delegate];
  [delegate.navigationController pushViewController:detailViewController animated:YES];
  [detailViewController release];
}


@end
